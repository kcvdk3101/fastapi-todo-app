from fastapi import APIRouter, Response

router = APIRouter(prefix='/health', tags=["Health"])

@router.get("")
async def health_check() -> Response:
  return Response(status_code=200)