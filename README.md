# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 → 包装纸面积 → 展开示意；算纸必选纸卷：按卷宽折下料长，不够一卷按整卷标称卷长托底订货米，写入用纸档后钉住不回填。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
