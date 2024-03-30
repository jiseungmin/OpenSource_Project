from fastapi import APIRouter

router  = APIRouter()

@router.get("/test")
def read_test(itme_id: int = None ):
  return {"HI Tets": itme_id}