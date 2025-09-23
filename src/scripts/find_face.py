"""
PYTHONPATH=src py src/scripts/find_face.py exports/target.HEIC
"""

from pathlib import Path

from app.image_processing import (
    find_similar_faces,
    get_faces,
    read_embeddings_file,
)

if __name__ == "__main__":
    targets = [
        # "exports/target.HEIC",
        # "exports/target.jpg",
        # "exports/target.png",
        # "exports/target2.JPG",
        # "exports/target2.HEIC",
        "exports/lana.jpg",
        # "exports/lana2.jpg",
    ]

    embeddings = []
    for emb_file in Path("exports/samples_embeddings").glob("*.parq"):
        emb = read_embeddings_file(emb_file)
        if "5707" in emb_file.name:
            breakpoint()  # FIXME: Breakpoint
        embeddings.extend(emb)

    total_faces = []
    for target in targets:
        print(f"Processing target: {target}")
        faces = get_faces(image_path=target)
        print(f"  Found {len(faces)} faces")
        if faces:
            total_faces.extend(faces)

    for sf in find_similar_faces(total_faces, embeddings):
        print(f"exports/samples/{sf}")
