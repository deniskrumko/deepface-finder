from fastapi import (
    APIRouter,
    Request,
)
from starlette.responses import Response

from app.core.templates import render_template

router = APIRouter()


@router.get("/")
async def index_view(request: Request) -> Response:
    return render_template("index.html", request)
