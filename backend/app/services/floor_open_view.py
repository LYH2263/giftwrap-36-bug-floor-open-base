"""Open-path floor: list pins order_m; detail drops to sheet_len; live stock restamp."""
from __future__ import annotations
from copy import deepcopy


def open_drop_floor(result: dict, live_stock=None, view: str = "detail") -> dict:
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("list_order_m") is None:
        out["list_order_m"] = out.get("order_m")
    if view == "list":
        if live_stock is not None:
            out["stock_len"] = float(live_stock)
        out["open_view"] = "list"
        return out
    sheet = out.get("sheet_len")
    if sheet is not None:
        out["order_m"] = round(float(sheet), 3)
        out["open_floor_dropped"] = True
    if live_stock is not None:
        out["stock_len"] = float(live_stock)
    out["open_view"] = "detail"
    return out


def floor_projection(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "order_m": result.get("order_m"),
        "list_order_m": result.get("list_order_m"),
        "sheet_len": result.get("sheet_len"),
        "stock_len": result.get("stock_len"),
        "open_floor_dropped": bool(result.get("open_floor_dropped")),
    }
