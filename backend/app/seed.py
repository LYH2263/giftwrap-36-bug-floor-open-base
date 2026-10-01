from app.db import connect

DEFAULT_STOCK_LEN = 50.0


def _migrate(c):
    """老库补列：papers.stock_len（标称卷长，米）。缺列则加列并回填默认标称。"""
    cols = {r["name"] for r in c.execute("PRAGMA table_info(papers)").fetchall()}
    if "stock_len" not in cols:
        c.execute("ALTER TABLE papers ADD COLUMN stock_len REAL")
        c.execute("UPDATE papers SET stock_len=? WHERE stock_len IS NULL", (DEFAULT_STOCK_LEN,))


def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,stock_len REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,result_json TEXT,note TEXT,created_at TEXT);
    """)
    _migrate(c)
    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,stock_len,data_quality,note) VALUES (?,?,?,?,?)",[
            ("哑光纸1.0m",1.0,50.0,"clean",""),
            ("牛皮纸0.7m",0.7,30.0,"clean",""),
            ("残卷-缺标称",0.6,0,"dirty","标称卷长缺失，仅演示托底拦截"),
        ])
        c.execute("INSERT INTO settings(key,value) VALUES ('overlap','1.15')")
    c.commit()
    c.close()
