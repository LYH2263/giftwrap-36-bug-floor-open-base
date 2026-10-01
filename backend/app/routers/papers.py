from fastapi import APIRouter, HTTPException
from app.repositories import papers as repo
from app.schemas.paper import PaperUpdate

router = APIRouter()

@router.get("/papers")
def list_papers(): return {"items": repo.list_papers()}

@router.put("/papers/{pid}")
def update_paper(pid: int, body: PaperUpdate):
    name = body.name.strip()
    if not name:
        raise HTTPException(422, "paper name required")
    ok = repo.update_paper(pid, name, float(body.roll_width), float(body.stock_len), body.note)
    if not ok:
        raise HTTPException(404, "paper not found")
    return repo.get_paper(pid)
