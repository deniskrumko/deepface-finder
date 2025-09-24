from typing import List

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.templates import render_template
from app.image_processing.face_detection import (
    find_similar_faces,
    get_faces_from_bytes,
)

router = APIRouter()


@router.get("/")
async def index_view(request: Request) -> Response:
    return render_template("index.html", request)


@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(default=...),  # noqa
    request: Request = None,  # type:ignore
) -> JSONResponse:
    """
    Handle file uploads from the index page.
    Accepts up to 5 image files for processing.
    """
    # Validate number of files
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 files allowed",
        )

    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required",
        )

    # Validate file types
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/heic"}
    uploaded_files = []
    total_faces = []
    for file in files:
        # Check file type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not a supported image format",
            )

        # Check file size (10MB limit per file)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is too large (max 10MB)",
            )

        faces = get_faces_from_bytes(content)
        if not faces:
            raise HTTPException(
                status_code=400,
                detail=f"No faces detected in file {file.filename}",
            )

        total_faces.extend(faces)

        # Reset file position for potential future reads
        await file.seek(0)

    project_data = request.app.projects_data["kolesa_birthday_2025"]

    for sf in find_similar_faces(total_faces, project_data.embeddings):
        print(f"exports/samples/{sf.filename} - distance {sf.distance:.4f}")  # noqa

    return JSONResponse(
        content={
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": [
                {
                    "filename": f["filename"],
                    "content_type": f["content_type"],
                    "size": f["size"],
                }
                for f in uploaded_files
            ],
        },
        status_code=200,
    )
