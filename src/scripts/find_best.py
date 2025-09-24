import time

from app.image_processing.face_embeddings import (
    create_embeddings_file,
    find_similar_faces,
    get_faces,
    read_embeddings_dir,
)

LABELS: dict[str, list[str]] = {
    "DSC05674": ["ilik", "lana"],
    "DSC05683": ["lana", "serega"],
    "DSC05688": ["lana", "dima"],
    "DSC05694": ["den"],
    "DSC05697": ["den"],
    "DSC05699": ["kum1", "kum2"],
    "DSC05705": [],
    "DSC05707": [],
    "DSC05710": ["dima"],
    "DSC05711": ["serega", "x"],
    "DSC05713": ["ilik", "lana"],
    "DSC05718": ["den", "ilik", "x"],
    "DSC05719": ["den", "ilik", "x", "x"],
    "DSC05721": ["dima"],
    "DSC05725": ["1", "2"],
    "DSC05726": ["1", "2"],
    "DSC05729": ["arai"],
}

TARGETS = {
    "den": ["denis1.HEIC", "denis2.HEIC", "denis3.JPG"],
    "dima": ["dima.jpg", "dima2.jpg"],
    "ilik": ["ilik.jpg", "ilik2.HEIC"],
    "lana": ["lana.jpg", "lana2.jpg"],
    "serega": ["serega.jpg"],
}


final_metrics = {}
# for model_name in ["Facenet", "Facenet512", "OpenFace"]:
for model_name in [
    "Facenet",
]:
    # for detector_backend in ["retinaface", "yolov8", "yolov11s"]:
    for detector_backend in ["yolov11s", "yolov11m"]:
        # for detector_backend in ["opencv", "retinaface", "ssd", "yolov8"]:
        time_start = time.monotonic()
        print("\nModel:", model_name, "Detector:", detector_backend)

        detector_score = 0
        model_score = 0

        embeddings_dir = f"exports/emb_{detector_backend}_{model_name}"
        for img, people in LABELS.items():
            img_path = f"exports/samples/{img}.JPG"
            count = create_embeddings_file(
                image_path=img_path,
                embedding_path=f"{embeddings_dir}/{img}.parq",
                model_name=model_name,
                detector_backend=detector_backend,
                skip_existing=False,
            )
            if count < 0:
                raise ValueError("Should not skip existing")

            actual_people = len([p for p in people if p != "x"])
            probable_people = len([p for p in people if p == "x"])

            if actual_people <= count <= actual_people + probable_people:
                detector_score += 1
            else:
                print(
                    "--Detector embedding error:",
                    img_path,
                    count,
                    actual_people,
                    probable_people,
                )
                detector_score -= 1

        embeddings = read_embeddings_dir(embeddings_dir)
        if not embeddings:
            continue

        for person, files in TARGETS.items():
            for file in files:
                faces = get_faces(f"exports/{file}", detector_backend=detector_backend)
                if len(faces) != 1:
                    print("--Target detector error:", file, len(faces))
                    detector_score -= 1
                    continue

                for sf in find_similar_faces(faces, embeddings, model_name=model_name):
                    label = sf.filename.split(".")[0]
                    expected_people = LABELS[label]
                    if person not in expected_people:
                        model_score -= 1
                        print(
                            f"--Person {person} was found on photo of "
                            f"{expected_people} (matched exports/samples/{sf.filename})",
                        )
                    else:
                        model_score += 1

        time_end = time.monotonic()
        total_time = f"{time_end - time_start:.3f}"
        metrics = {
            "model_score": model_score,
            "detector_score": detector_score,
            "time": float(total_time),
        }
        final_metrics[f"{detector_backend}_{model_name}"] = metrics
        print("Metrics:", metrics)


print("\n\nFinal metrics:\n")
min_metrics: dict[str, float] = {}
max_metrics: dict[str, float] = {}

for k, v in final_metrics.items():
    print(k.upper())
    for mk, mv in v.items():
        print(f"  {mk}: {mv}")
        if mk not in min_metrics or mv < min_metrics[mk]:
            min_metrics[mk] = mv
        if mk not in max_metrics or mv > max_metrics[mk]:
            max_metrics[mk] = mv
    print()

print("\n\nMin metrics:")
for min_m, min_v in min_metrics.items():
    print(f"\n  {min_m}: {min_v} ", end=": ")
    for k, v in final_metrics.items():
        value = v[min_m]
        if value == min_v:
            print(f"{k}", end=", ")

print("\nMax metrics:")
for max_m, max_v in max_metrics.items():
    print(f"\n  {max_m}: {max_v} ", end=": ")
    for k, v in final_metrics.items():
        value = v[max_m]
        if value == max_v:
            print(f"{k}", end=", ")
