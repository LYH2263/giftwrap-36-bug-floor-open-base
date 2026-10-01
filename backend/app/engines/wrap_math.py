import math


def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}


def roll_order(paper_m2: float, roll_width: float, stock_len: float) -> dict:
    """整卷起订托底。

    下料长 sheet_len = 用纸面积 / 卷宽（按卷宽折出）；
    订货米 order_m：够一卷取下料长，不够则按整卷倍数上托。
    卷宽或标称卷长非正一律报错（调用方据此不落库）。
    """
    rw = float(roll_width)
    sl = float(stock_len)
    need = float(paper_m2)
    if rw <= 0:
        raise ValueError("roll_width must be positive")
    if sl <= 0:
        raise ValueError("stock_len must be positive")
    if need <= 0:
        raise ValueError("paper_m2 must be positive")
    sheet = round(need / rw, 3)
    if sheet <= sl:
        order = sheet
    else:
        # 1e-9 吸收浮点误差，整卷倍数本身不再多托一卷
        order = round(math.ceil(sheet / sl - 1e-9) * sl, 3)
    return {"sheet_len": sheet, "stock_len": sl, "order_m": order}
