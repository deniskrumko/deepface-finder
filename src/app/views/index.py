import logging
from typing import Any

from fastapi import (
    APIRouter,
    File,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.fastapi import error_response
from app.core.i18n import _
from app.core.settings import Settings
from app.core.templates import render_template
from app.image_processing.face_detection import (
    find_similar_faces,
    get_faces,
)
from app.image_processing.resources import (
    IMAGE_MIMETYPES,
    Face,
)
from app.storages import S3Proxy

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILES: int = 5


@router.get("/")
async def index_view(request: Request) -> Response:
    return render_template("index.html", request)


@router.post("/")
async def upload_files(
    files: list[UploadFile] = File(default=...),  # noqa
    request: Request = None,  # type:ignore
) -> JSONResponse:
    # Validate number of files
    if len(files) > MAX_FILES:
        return error_response(_("Maximum {} files allowed").format(MAX_FILES))

    if len(files) == 0:
        return error_response(_("At least one file is required"))

    settings: Settings = request.app.settings  # type:ignore

    try:
        user_faces = await extract_faces_from_files(
            files=files,
            detector_backend=settings.deepface.detector_backend,
            min_face_size=settings.deepface.min_detector_face_size,
        )
    except Exception as e:
        logger.exception(f"Error during processing uploaded files: {e!r}")
        return error_response(_("Error during processing uploaded files: {}").format(e))

    try:
        similar_faces = find_similar_faces(
            faces=user_faces,
            embeddings=request.app.embeddings,
            model_name=settings.deepface.model_name,
        )
    except Exception as e:
        logger.exception(f"Error during finding similar photos: {e!r}")
        return error_response(_("Error during finding similar photos: {}").format(e))

    logger.info(f"Found {len(similar_faces)} similar faces for {len(user_faces)} uploaded faces")

    s3_proxy: S3Proxy = request.app.s3_proxy  # type:ignore
    result_files = [
        {
            "filename": sf.filename,
            "distance": sf.distance,
            "resized": s3_proxy.get_proxy_path(sf.filename, prefix=settings.images.resized),
            "original": s3_proxy.get_proxy_path(sf.filename, prefix=settings.images.original),
        }
        for sf in similar_faces
    ]

    return JSONResponse(
        content={
            "success": True,
            "files": result_files,
        },
        status_code=200,
    )


async def extract_faces_from_files(files: list[UploadFile], **kwargs: Any) -> list[Face]:
    user_faces: list[Face] = []

    for file in files:
        filename = file.filename

        # Check file type
        if file.content_type not in IMAGE_MIMETYPES:
            raise ValueError(_("File {} is not a supported image format").format(filename))

        # Check file size (10MB limit per file)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise ValueError(_("File {} is too large (max 10MB)").format(filename))

        faces = get_faces(content, **kwargs)
        if not faces:
            raise ValueError(_("No faces detected in file {}").format(filename))

        if len(faces) > 1:
            raise ValueError(
                _(
                    "Multiple faces detected in file {}. "
                    "Please upload images with a single face.",
                ).format(filename),
            )

        user_faces.extend(faces)

        # Reset file position for potential future reads
        await file.seek(0)

    return user_faces
