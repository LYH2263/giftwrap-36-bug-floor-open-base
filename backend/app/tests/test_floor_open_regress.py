from app.services.floor_open_view import open_drop_floor

def test_detail_order_falls_to_sheet_len():
    raw = {"sheet_len": 1.2, "stock_len": 3.0, "order_m": 3.0, "paper_name": "卷X"}
    out = open_drop_floor(raw, view="detail")
    assert out["order_m"] == 1.2
    assert out.get("list_order_m") == 3.0
