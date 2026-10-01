from app.db import connect

def list_papers():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM papers ORDER BY id").fetchall()]
    finally:
        c.close()

def get_paper(pid):
    c = connect()
    try:
        r = c.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_paper(pid, name, roll_width, stock_len, note=""):
    """只改标称（名称/卷宽/标称卷长/备注），不动历史用纸档。"""
    c = connect()
    try:
        cur = c.execute(
            "UPDATE papers SET name=?, roll_width=?, stock_len=?, note=? WHERE id=?",
            (name, roll_width, stock_len, note, pid),
        )
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()
