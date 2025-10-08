from pathlib import Path
from typing import (
    Any,
    NoReturn,
)

from fastapi import (
    FastAPI,
    HTTPException,
    Response,
)
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class CacheControlledStaticFiles(StaticFiles):
    """Static files handler that injects a Cache-Control header.

    Extends starlette.staticfiles.StaticFiles by adding a configurable
    "public, max-age=<seconds>" cache header to every successful file response.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""
        self.max_age = kwargs.pop("max_age", 86400)
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response


def init_fastapi_app(with_routes: bool = True) -> FastAPI:
    """Create and configure a FastAPI application instance.

    Mounts the static files application and optionally registers API/UI routes.

    Args:
        with_routes: When True (default) include project routers.

    Returns:
        The configured FastAPI application object.
    """
    app = FastAPI()
    static_dir = Path(__file__).parent.parent.parent / "static"
    app.mount("/static", CacheControlledStaticFiles(directory=static_dir), name="static")

    # app.app_version = get_version()

    if with_routes:
        register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    """Attach application routers to the provided FastAPI app.

    Currently registers the index router; extend this as new routers are added.

    Args:
        app: The FastAPI application to modify.
    """
    from app.views.index import router as index_router

    for router in (index_router,):
        app.include_router(router)


def error_response(detail: str, status_code: int = 400) -> NoReturn:
    """Raise a formatted HTTPException with a detail message.

    Args:
        detail: Error description returned to the client.
        status_code: HTTP status to raise (default 400).
    """
    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )
