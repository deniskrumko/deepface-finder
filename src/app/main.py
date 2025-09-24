from pathlib import Path

from pydantic import BaseModel

from app.core.fastapi import init_fastapi_app
from app.core.settings import (
    Project,
    get_settings,
)
from app.image_processing.face_embeddings import read_embeddings_dir
from app.image_processing.resources import FaceEmbedding
from app.image_processing.storages import (
    download_file_from_s3,
    get_s3_client,
    list_files_in_s3_prefix,
)

# Initialize FastAPI application
app = init_fastapi_app()

settings = get_settings()
app.settings = settings  # type:ignore


class ProjectData(BaseModel):
    project: Project
    original_images: list[str]
    resized_images: list[str]
    embeddings: list[FaceEmbedding]

    def __repr__(self) -> str:
        return (
            f"<ProjectData {self.project.name} "
            f"({len(self.original_images)}/{len(self.resized_images)}/{len(self.embeddings)})>"
        )


projects_data: dict[str, ProjectData] = {}

for project_name, project in settings.projects.items():
    source = settings.sources.get(project.source)
    if source is None:
        raise ValueError(f"Source '{project.source}' not found in settings sources")

    objects_lists = {}
    for attr in ["original_images", "resized_images", "embeddings"]:
        if source.type == "filesystem":
            objects = [str(p) for p in (Path(source.path) / getattr(project, attr)).rglob("*")]
        elif source.type == "s3":
            s3_client = get_s3_client(**source.model_dump())
            objects = list_files_in_s3_prefix(
                s3_client=s3_client,
                bucket_name=source.bucket,
                s3_prefix=getattr(project, attr),
            )
        else:
            raise ValueError(f"Unsupported source type: {source.type}")

        if not objects:
            raise ValueError(f"No {attr} objects found in {source}")

        objects_lists[attr] = objects

    if source.type == "filesystem":
        embeddings_dir = Path(source.path) / project.embeddings
    elif source.type == "s3":
        embeddings_dir = Path("/tmp") / project.name / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)

        for embedding in objects_lists["embeddings"]:
            local_path = embeddings_dir / Path(embedding).name
            if local_path.exists():
                continue

            download_file_from_s3(
                s3_client=s3_client,
                bucket_name=source.bucket,
                s3_key=embedding,
                local_path=local_path,
            )
            print(f"Downloaded embedding to {local_path}")  # noqa

    embeddings = read_embeddings_dir(embeddings_dir)

    project_data = ProjectData(
        project=project,
        original_images=objects_lists["original_images"],
        resized_images=objects_lists["resized_images"],
        embeddings=embeddings,
    )
    projects_data[project_name] = project_data
    print(f"Loaded project data: {project_name} – {project_data!r}")  # noqa

app.projects_data = projects_data  # type:ignore
