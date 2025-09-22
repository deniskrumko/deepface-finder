import os
import pickle

from deepface import DeepFace
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()
model = "VGG-Face"
photos = "/Users/krumko/kolesa_group_birthday"
pkl_photos_dir = "/Users/krumko/kolesa_group_birthday_pkl"
targets = [
    "target.png",
    "target2.png",
    "target3.jpg",
]


def convert_to_jpg(input_file, output_file):
    try:
        img = Image.open(input_file)
        img = img.convert("RGB")
        img.save(output_file, "JPEG", quality=95)

        # Delete the original .heic file after successful conversion
        os.remove(input_file)
    except Exception as e:
        print(f"Error converting {input_file} to {output_file}: {e}")


def prepare_pkl():
    for root, dirs, files in os.walk(photos):
        for file in files:
            filepath = os.path.join(root, file)
            pkl_path = os.path.join(pkl_photos_dir, file) + ".pkl"

            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".heic")):
                continue

            if os.path.exists(pkl_path):
                print("x", end="", flush=True)
                continue  # Skip if .pkl file already exists

            faces = DeepFace.represent(os.path.join(root, file), enforce_detection=False)
            if len(faces) == 1 and not faces[0]["face_confidence"]:
                print("E", end="", flush=True)
                continue

            with open(pkl_path, "wb") as f:
                pickle.dump(faces, f)
            print(".", end="", flush=True)


def find_similar_faces(target_face, representations):
    return DeepFace.recognition.find_batched(
        representations,
        source_objs=[target_face],
    )


def load_representations(pkl_photos_dir):
    representations = []
    for root, dirs, files in os.walk(pkl_photos_dir):
        for file in files:
            if file.endswith(".pkl"):
                pkl_path = os.path.join(root, file)
                with open(pkl_path, "rb") as f:
                    try:
                        faces = pickle.load(f)
                        for face in faces:
                            face["filename"] = file
                        representations.extend(faces)
                    except Exception as e:
                        print(f"Error loading {pkl_path}: {e}")
    return representations


def main():
    # prepare_pkl()

    target = targets[2]
    target_faces = DeepFace.extract_faces(target)
    if len(target_faces) != 1:
        raise ValueError("Target image must contain exactly one face.")

    target_face = target_faces[0]
    representations = load_representations(pkl_photos_dir)

    for similar in find_similar_faces(target_face, representations)[0]:
        similar_filename = similar["filename"].replace(".pkl", "")
        similar_path = os.path.join(photos, similar_filename)
        face_confidence = similar["face_confidence"]
        print(f"Found similar face in: {similar_path}: {face_confidence}")


if __name__ == "__main__":
    main()
