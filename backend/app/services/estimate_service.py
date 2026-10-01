from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate, roll_order
from app.repositories import boxes, history, papers as papers_repo, settings_repo

def run_estimate(box_id: int, paper_id: int | None, overlap: float | None, wrap_style: str, save: bool, note: str):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404, "box not found")
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    if paper_id is None:
        raise HTTPException(422, "paper_id required: 必须选纸卷")
    paper = papers_repo.get_paper(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    try:
        roll = roll_order(calc["paper_m2"], paper["roll_width"], paper["stock_len"])
    except (TypeError, ValueError) as e:
        # 卷宽非正 / 标称卷长缺失或非正：失败且不落库
        raise HTTPException(422, f"paper nominal invalid: {e}")
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    payload = {
        **calc, **roll, "ribbon": ribbon,
        "box_id": box_id, "paper_id": paper["id"], "paper_name": paper["name"],
    }
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "paper": paper, "run_id": run_id, **calc, **roll, "ribbon": ribbon}
