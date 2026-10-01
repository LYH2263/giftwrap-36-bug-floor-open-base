from pydantic import BaseModel

class PaperUpdate(BaseModel):
    """只改标称：名称、卷宽、标称卷长、备注。历史用纸档不回填。"""
    name: str
    roll_width: float
    stock_len: float
    note: str = ""
