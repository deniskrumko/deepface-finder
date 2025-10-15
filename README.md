# deepface-finder

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/deniskrumko/deepface-finder/build-and-push.yml)](https://github.com/deniskrumko/deepface-finder/actions)
[![GitHub Release](https://img.shields.io/github/v/release/deniskrumko/deepface-finder)](https://github.com/deniskrumko/deepface-finder/releases)
[![Docker pulls](https://img.shields.io/docker/pulls/deniskrumko/deepface-finder)](https://hub.docker.com/r/deniskrumko/deepface-finder/tags)

Face finder web app powered by [DeepFace](https://github.com/serengil/deepface)

Docker Hub: https://hub.docker.com/r/deniskrumko/deepface-finder

![preview](https://github.com/deniskrumko/deepface-finder/blob/main/src/static/images/preview.jpg?raw=true)

# How it works

- You get a bunch of images (from your birthday party, huge IT event, or anything)
- Preprocess them using scripts: create resized versions and get embeddings. How? Read the "How to prepare images" section
- Upload original/resized/embedding files to cloud storage (currently, only S3 is supported)
- Run the [deepface-finder](https://github.com/deniskrumko/deepface-finder) service
- Upload 1 to 5 photos with your face and instantly find photos with your face!

![preview](https://github.com/deniskrumko/deepface-finder/blob/main/src/static/images/ui-results.jpg?raw=true)

# How to prepare images

This service needs some configuration and files processing before you can use it:

- Clone [deepface-finder](https://github.com/deniskrumko/deepface-finder) repository

    ```bash
    gh repo clone deniskrumko/deepface-finder
    ```

- Create Python 3.12 virtual environment (I like virtualenv-wrapper with pyenv)

    ```bash
    mkvirtualenv deepface-finder -p ~/.pyenv/versions/3.12.4/bin/python
    ```

- Prepare config file. See "Configuration" section bellow. For example, it will be `my_config.toml`
- Locate directory with your photos, for example `photos/original`
- First, run [resizing script](https://github.com/deniskrumko/deepface-finder/blob/main/src/scripts/prepare_images.py)

    ```bash
    PYTHONPATH=src py src/scripts/prepare_images.py \
    --src photos/original \
    --dst photos/resized
    ```

- Second, run [embedding script](https://github.com/deniskrumko/deepface-finder/blob/main/src/scripts/prepare_embeddings.py)

    ```bash
    PYTHONPATH=src py src/scripts/prepare_embeddings.py \
    --src photos/original \
    --dst photos/embeddings \
    --config my_config.toml
    ```

- And the last step, run [uploading script](https://github.com/deniskrumko/deepface-finder/blob/main/src/scripts/upload_to_s3.py)

    ```bash
    PYTHONPATH=src py src/scripts/upload_to_s3.py \
    --config my_config.toml \
    --original photos/original \
    --resized photos/resized \
    --embeddings photos/embeddings
    ```

- That's it! Now you can run the service. See "How to run service" section

# Configuration

```toml
[ui]
language = "en"  # en/ru supported
branding_title = "My Face Finder"
branding_image = "https://media1.tenor.com/m/x8v1oNUOmg4AAAAd/rickroll-roll.gif"
branding_text = """
<p>Welcome to <span class="highlight">My Face Finder</span></p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec dapibus nibh mollis viverra interdum. Donec tortor urna, fringilla quis mattis in, vehicula quis ipsum. Duis ut ligula nec massa pretium viverra. Duis tortor odio, finibus sit amet libero quis, sodales pulvinar quam<p>
"""

[deepface]
model_name = "Facenet"
detector_backend = "yolov8"

[s3]
region = "us-east-1"
endpoint = "YOUR_ENDPOINT"
key = "YOUR_ACCESS_KEY"
secret = "YOUR_SECRET_KEY"

[proxy]
url = "https://my-images-proxy.com/"

[images]
bucket = "deepface-images"
original = "my_birthday_party/original/"
resized = "my_birthday_party/resized/"
embeddings = "my_birthday_party/embeddings/"
```

With this configuration UI will look like...

![preview](https://github.com/deniskrumko/deepface-finder/blob/main/src/static/images/ui-example.jpg?raw=true)

# How to run service

NOTE: See "CUDA support" section bellow to use CUDA-based Docker image.

1. Locally using virtual env:

    ```bash
    PYTHONPATH=src APP_CONFIG=my_config.toml python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080
    ```

2. Using `docker-compose.yml`

    ```
    services:

      deepface-finder:
        image: deniskrumko/deepface-finder:latest
        volumes:
          - ./my_config.toml:/config.toml:ro
        ports:
          - 8080:8080
    ```

3. Using Docker

    ```bash
    docker run -p 8080:8080 -v ./my_config.toml:/config.toml deniskrumko/deepface-finder:latest
    ```

# Preload model to Docker image

You can build your custom Docker image with preloaded model and detector backend. It will significantly speedup processing because typically model/detector are loaded only after first request to deepface-finder.

Example Dockerfile with build args:

```Dockerfile
FROM deniskrumko/deepface-finder:latest

# Preload models
ARG model_name
ARG detector_backend
RUN python3 -m scripts.prepare_models --model-name ${model_name} --detector-backend ${detector_backend}
```

Then run:

```bash
docker build -t deepface-finder:facenet-yolov8 . \
    --build-arg model_name=Facenet \
    --build-arg detector_backend=yolov8
```

# CUDA support

There is a separate Docker image `deniskrumko/deepface-finder-cuda11.6.2:latest` that uses CUDA versions of Torch and TorchVision.

# Credits

- Powered by Python 3.12, FastAPI and Jinja2
- [DeepFace](https://github.com/serengil/deepface) library
- Fonts/icons from [Google fonts](https://fonts.google.com/icons?icon.size=24&icon.color=%23e3e3e3)
