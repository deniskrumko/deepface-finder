from pathlib import Path
from typing import Any

from fastapi import (
    FastAPI,
    Response,
)
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class CacheControlledStaticFiles(StaticFiles):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""
        self.max_age = kwargs.pop("max_age", 86400)
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response


def init_fastapi_app(with_routes: bool = True) -> FastAPI:
    """Initialize FastAPI application with settings and routes."""
    app = FastAPI()
    static_dir = Path(__file__).parent.parent.parent / "static"
    app.mount("/static", CacheControlledStaticFiles(directory=static_dir), name="static")

    # app.app_version = get_version()

    if with_routes:
        register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    from app.views.index import router as index_router

    for router in (index_router,):
        app.include_router(router)
