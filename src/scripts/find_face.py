"""
PYTHONPATH=src py src/scripts/find_face.py
"""

from pathlib import Path

from app.image_processing.face_detection import (
    find_similar_faces,
    get_faces,
)
from app.image_processing.face_embeddings import read_embeddings_file

if __name__ == "__main__":
    targets = [
        "exports/targets/denis1.HEIC",
        "exports/targets/denis2.HEIC",
        "exports/targets/denis3.JPG",
        # "exports/targets/dima.jpg",
        # "exports/targets/dima2.jpg",
        # "exports/targets/ilik.jpg",
        # "exports/targets/ilik2.HEIC",
        # "exports/targets/lana.jpg",
        # "exports/targets/lana2.jpg",
        # "exports/targets/lana3.png",
        # "exports/targets/serega.jpg",
        # "exports/targets/yana.jpg",
    ]

    embeddings = []
    for emb_file in Path("exports/samples_embeddings").glob("*.parq"):
        emb = read_embeddings_file(emb_file)
        embeddings.extend(emb)

    total_faces = []
    for target in targets:
        print(f"Processing target: {target}")
        faces = get_faces(image_path=target)
        print(f"  Found {len(faces)} faces")
        if faces:
            total_faces.extend(faces)

    for sf in find_similar_faces(total_faces, embeddings):
        print(f"exports/samples/{sf.filename} - distance {sf.distance:.4f}")
