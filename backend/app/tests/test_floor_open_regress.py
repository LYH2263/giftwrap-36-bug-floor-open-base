"""回归：详情回看不得把 order_m 掉回未托底基础米。

整卷托底落库后，列表与详情都钉住写入的 order_m / sheet_len / stock_len；
同卷干算与落库互证；响应不残留开放视图的掉底标记。
"""
import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="gw-test-")

import pytest
from fastapi.testclient import TestClient

from app import seed
from app.config import DB_PATH
from app.main import app


@pytest.fixture()
def client():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    seed.init_db()
    with TestClient(app) as c:
        yield c


def test_detail_readback_keeps_floored_order_m(client):
    # 标称 0.2m：下料 0.31m 超一卷，订货米整卷上托到 0.4m
    client.put("/api/papers/1", json={"name": "哑光纸1.0m", "roll_width": 1.0, "stock_len": 0.2})
    saved = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True}).json()
    assert saved["order_m"] == 0.4
    assert saved["sheet_len"] == 0.31

    rid = saved["run_id"]
    detail = client.get(f"/api/runs/{rid}").json()["result"]
    listed = client.get("/api/runs").json()["items"][0]["result"]

    # 详情与列表同钉写入的托升值，不掉回未托底下料长
    for got in (detail, listed):
        assert got["order_m"] == 0.4
        assert got["sheet_len"] == 0.31
        assert got["stock_len"] == 0.2
        assert got["paper_name"] == "哑光纸1.0m"

    # 不残留开放视图掉底标记
    for key in ("open_floor_dropped", "open_view", "list_order_m"):
        assert key not in detail
    assert "open_projection" not in client.get(f"/api/runs/{rid}").json()

    # 同卷干算与落库编号互证
    dry = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1}).json()
    assert dry["order_m"] == detail["order_m"] == 0.4
