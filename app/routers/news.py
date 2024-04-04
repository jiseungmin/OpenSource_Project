from fastapi import APIRouter

router  = APIRouter()

@router.get("/news")
def read_test(itme_id: int = None ):
  return {"HI Tets": itme_id}