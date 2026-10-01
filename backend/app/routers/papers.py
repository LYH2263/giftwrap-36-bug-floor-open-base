from fastapi import APIRouter, HTTPException
from app.repositories import papers as repo
from app.schemas.paper import PaperUpdate

router = APIRouter()

@router.get("/papers")
def list_papers(): return {"items": repo.list_papers()}

@router.put("/papers/{pid}")
def update_paper(pid: int, body: PaperUpdate):
    name = body.name.strip()
    if not name:
        raise HTTPException(422, "paper name required")
    stock_len = float(body.stock_len)
    if stock_len <= 0:
        # 标称卷长非正：拒绝写入，旧标称保持不变
        raise HTTPException(422, "stock_len must be positive: 标称卷长必须大于0")
    ok = repo.update_paper(pid, name, float(body.roll_width), stock_len, body.note)
    if not ok:
        raise HTTPException(404, "paper not found")
    return repo.get_paper(pid)
