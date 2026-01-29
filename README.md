# Virtual Try-On Prototype (Vertex AI)

This repo contains a tiny, rough working example that calls Google's Vertex AI Virtual Try-On API to generate a preview image of a person wearing a garment. The goal is to **vibe-code** a minimal flow that could power an in-store AR mirror experience (capture → generate → display).

## What this does

- Takes a **person photo** and a **garment photo**.
- Sends both to the Vertex AI Virtual Try-On endpoint.
- Saves the generated image to disk (for display on a kiosk / mirror screen).

## Quick start

1. **Install deps**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Authenticate**

You can use `gcloud` to grab an access token:

```bash
gcloud auth application-default login
gcloud auth print-access-token
```

3. **Run the demo**

```bash
python virtual_try_on_demo.py \
  --project YOUR_GCP_PROJECT \
  --location us-central1 \
  --person ./samples/person.jpg \
  --garment ./samples/garment.jpg \
  --output ./out/try_on.png
```

You can also pass an access token explicitly:

```bash
python virtual_try_on_demo.py \
  --project YOUR_GCP_PROJECT \
  --location us-central1 \
  --person ./samples/person.jpg \
  --garment ./samples/garment.jpg \
  --output ./out/try_on.png \
  --access-token "$(gcloud auth print-access-token)"
```

## Notes

- This is intentionally a **rough example** to validate the workflow.
- The same flow can be wired to an in-store camera capture + large display to simulate an AR mirror.
- Swap `MODEL_ID` in the script if your org uses a different model name.

## When to add a product catalog

Start by validating that **one person image + one garment image** can successfully return a try-on render. Once that API round-trip works reliably, layer in a catalog service so you can pick garments by ID and map them to image assets (or URLs). This avoids debugging catalog plumbing while the core model call is still unproven.

If you want to stub this now, there's a small mock catalog you can adapt (`samples_catalog.json`) that mirrors the structure you shared and adds a single field (`garmentImagePath`) you can map to the `--garment` input for the demo script. You can then build a thin UI/API layer (Node + Express or similar) that:

1. Lists products from the catalog (or client API).
2. Lets a user pick an item.
3. Resolves the selected item to a garment image path/URL.
4. Calls the Python try-on script or a small wrapper service.
