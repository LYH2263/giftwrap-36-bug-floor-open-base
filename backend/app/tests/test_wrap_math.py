import pytest
from app.engines.wrap_math import paper_area, ribbon_estimate, roll_order

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

# —— 整卷起订托底 roll_order ——

def test_roll_order_fits_single_roll():
    r = roll_order(0.31, 1.0, 50.0)
    assert r["sheet_len"] == 0.31
    assert r["stock_len"] == 50.0
    assert r["order_m"] == 0.31  # 够一卷取下料长

def test_roll_order_rounds_up_to_whole_rolls():
    r = roll_order(0.31, 1.0, 0.2)
    assert r["sheet_len"] == 0.31
    assert r["order_m"] == 0.4  # 不够一卷，按整卷倍数上托：2 × 0.2

def test_roll_order_exact_multiple_not_over_rounded():
    assert roll_order(0.4, 1.0, 0.2)["order_m"] == 0.4   # 恰 2 卷
    assert roll_order(2.1, 1.0, 0.7)["order_m"] == 2.1   # 恰 3 卷（浮点边界）
    assert roll_order(2.2, 1.0, 0.7)["order_m"] == 2.8   # 超一点上托到 4 卷

def test_roll_order_sheet_len_uses_roll_width():
    r = roll_order(0.31, 0.7, 30.0)
    assert r["sheet_len"] == 0.443  # 0.31 / 0.7 按卷宽折出
    assert r["order_m"] == 0.443

def test_roll_order_rejects_bad_nominal():
    with pytest.raises(ValueError):
        roll_order(0.31, 0, 50.0)      # 卷宽非正
    with pytest.raises(ValueError):
        roll_order(0.31, -0.5, 50.0)
    with pytest.raises(ValueError):
        roll_order(0.31, 1.0, 0)       # stock_len 非正
    with pytest.raises(ValueError):
        roll_order(0.31, 1.0, -10.0)
    with pytest.raises(ValueError):
        roll_order(0, 1.0, 50.0)       # 面积非正
