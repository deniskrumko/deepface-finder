"""
PYTHONPATH=src py src/scripts/prepare_models.py \
    --model-name Facenet \
    --detector-backend yolov8
"""

from deepface import DeepFace

MODELS = [
    "VGG-Face",
    "Facenet",
    "Facenet512",
    "OpenFace",
    "DeepFace",
    "DeepID",
    "Dlib",
    "ArcFace",
    "SFace",
    "GhostFaceNet",
    "Buffalo_L",
]
DETECTORS = [
    "opencv",
    "mtcnn",
    "ssd",
    "dlib",
    "retinaface",
    "mediapipe",
    "yolov8",
    "yolov11n",
    "yolov11s",
    "yolov11m",
    "yunet",
    "fastmtcnn",
    "centerface",
]

if __name__ == "__main__":
    import argparse

    model_name = ", ".join(MODELS)
    detector_backend = ", ".join(DETECTORS)
    parser = argparse.ArgumentParser(description="Preload models locally")
    parser.add_argument("--model-name", help=f"Model name ({model_name})")
    parser.add_argument("--detector-backend", help=f"Detector backend ({detector_backend})")

    args = parser.parse_args()
    preloaded = False

    if args.model_name:
        if args.model_name not in MODELS:
            raise ValueError(f"Invalid model name. Choose from: {model_name}")

        DeepFace.build_model(args.model_name, "facial_recognition")
        print(f"Facial recognition model '{args.model_name}' is ready")
        preloaded = True

    if args.detector_backend:
        if args.detector_backend not in DETECTORS:
            raise ValueError(f"Invalid detector backend. Choose from: {detector_backend}")

        DeepFace.build_model(args.detector_backend, "face_detector")
        print(f"Face detector model '{args.detector_backend}' is ready")
        preloaded = True

    if not preloaded:
        print(
            "No models was preloaded. "
            "Use --model-name or --detector-backend to specify a model.",
        )
