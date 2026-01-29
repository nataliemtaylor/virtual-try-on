import argparse
import base64
import json
import os
from pathlib import Path

import requests

MODEL_ID = "virtual-try-on"

def read_image_base64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def build_payload(person_b64: str, garment_b64: str) -> dict:
    return {
        "instances": [
            {
                "person_image": {"bytesBase64Encoded": person_b64},
                "garment_image": {"bytesBase64Encoded": garment_b64},
            }
        ],
        "parameters": {
            "sample_count": 1,
        },
    }


def get_access_token(explicit_token: str | None) -> str:
    if explicit_token:
        return explicit_token
    token = os.environ.get("ACCESS_TOKEN")
    if not token:
        raise SystemExit(
            "Missing access token. Provide --access-token or set ACCESS_TOKEN."
        )
    return token


def call_virtual_try_on(
    project: str,
    location: str,
    token: str,
    payload: dict,
) -> dict:
    endpoint = (
        "https://{location}-aiplatform.googleapis.com/v1/projects/"
        "{project}/locations/{location}/publishers/google/models/{model}:predict"
    ).format(location=location, project=project, model=MODEL_ID)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()


def save_output(response_json: dict, output_path: Path) -> None:
    predictions = response_json.get("predictions", [])
    if not predictions:
        raise SystemExit("No predictions returned from API.")

    image_payload = predictions[0].get("bytesBase64Encoded")
    if not image_payload:
        raise SystemExit("Missing image data in API response.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_payload))


def main() -> None:
    parser = argparse.ArgumentParser(description="Vertex AI Virtual Try-On demo")
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--person", required=True)
    parser.add_argument("--garment", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--access-token")

    args = parser.parse_args()

    person_path = Path(args.person)
    garment_path = Path(args.garment)

    if not person_path.exists():
        raise SystemExit(f"Person image not found: {person_path}")
    if not garment_path.exists():
        raise SystemExit(f"Garment image not found: {garment_path}")

    token = get_access_token(args.access_token)
    payload = build_payload(
        read_image_base64(person_path),
        read_image_base64(garment_path),
    )
    response_json = call_virtual_try_on(args.project, args.location, token, payload)
    save_output(response_json, Path(args.output))

    print(f"Saved try-on image to {args.output}")


if __name__ == "__main__":
    main()
