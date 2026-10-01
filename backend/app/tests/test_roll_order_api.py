"""整卷起订托底的端到端口径测试。

预览/落库同返 sheet_len、stock_len、order_m；失败不加行；
列表与详情钉住写入值；同参干算与回看互证；改标称只影响新单。
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


def _runs(client):
    return client.get("/api/runs").json()["items"]


# 种子：盒1 书型盒(clean)；纸1 哑光纸 卷宽1.0 标称50m；纸2 牛皮纸 0.7/30m；纸3 残卷 stock_len=0

def test_preview_returns_roll_fields_and_writes_nothing(client):
    r = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["paper_m2"] == 0.31
    assert body["sheet_len"] == 0.31
    assert body["stock_len"] == 50.0
    assert body["order_m"] == 0.31
    assert body["run_id"] is None
    assert _runs(client) == []  # 预览不落库


def test_save_pins_order_and_detail_matches_list(client):
    r = client.post("/api/estimate", json={"box_id": 1, "paper_id": 2, "save": True})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"]
    assert (body["sheet_len"], body["stock_len"], body["order_m"]) == (0.443, 30.0, 0.443)

    items = _runs(client)
    assert len(items) == 1
    listed = items[0]["result"]
    assert listed["order_m"] == body["order_m"]
    assert listed["sheet_len"] == body["sheet_len"]
    assert listed["stock_len"] == body["stock_len"]

    detail = client.get(f"/api/runs/{body['run_id']}")
    assert detail.status_code == 200
    got = detail.json()["result"]
    assert got["order_m"] == listed["order_m"] == body["order_m"]  # 列表与详情一致
    assert got["sheet_len"] == body["sheet_len"]
    assert got["stock_len"] == body["stock_len"]

    # 同参干算与回看互证
    dry = client.get("/api/estimate", params={"box_id": 1, "paper_id": 2}).json()
    assert dry["order_m"] == got["order_m"]
    assert dry["sheet_len"] == got["sheet_len"]


def test_missing_or_unknown_paper_fails_without_row(client):
    r = client.post("/api/estimate", json={"box_id": 1, "save": True})  # 缺 paper_id
    assert r.status_code == 422
    r = client.post("/api/estimate", json={"box_id": 1, "paper_id": 999, "save": True})
    assert r.status_code == 404
    assert _runs(client) == []


def test_non_positive_stock_len_fails_without_row(client):
    r = client.post("/api/estimate", json={"box_id": 1, "paper_id": 3, "save": True})
    assert r.status_code == 422
    assert _runs(client) == []


def test_non_positive_roll_width_fails_without_row(client):
    ok = client.put("/api/papers/1", json={"name": "哑光纸1.0m", "roll_width": 0, "stock_len": 50.0})
    assert ok.status_code == 200
    r = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True})
    assert r.status_code == 422
    assert _runs(client) == []


def test_rename_nominal_keeps_old_runs_pinned(client):
    first = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True}).json()
    assert first["order_m"] == 0.31
    rid = first["run_id"]

    # 纸张页只改标称：标称卷长 50m → 0.2m
    r = client.put("/api/papers/1", json={"name": "哑光纸1.0m", "roll_width": 1.0, "stock_len": 0.2})
    assert r.status_code == 200
    assert r.json()["stock_len"] == 0.2

    # 旧单列表与详情钉住写入值，不按新标称重托
    listed = _runs(client)[0]["result"]
    detail = client.get(f"/api/runs/{rid}").json()["result"]
    assert listed["order_m"] == 0.31
    assert detail["order_m"] == 0.31
    assert detail["stock_len"] == 50.0

    # 新单按新标称上托，且干算与落库互证（只对照新单）
    dry = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1}).json()
    assert dry["stock_len"] == 0.2
    assert dry["order_m"] == 0.4
    second = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True}).json()
    assert second["order_m"] == dry["order_m"] == 0.4
    again = client.get(f"/api/runs/{second['run_id']}").json()["result"]
    assert again["order_m"] == 0.4
    assert client.get(f"/api/runs/{rid}").json()["result"]["order_m"] == 0.31  # 旧单仍钉住
