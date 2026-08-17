import streamlit as st
from PIL import Image, ImageDraw, ImageFont

NATIVE_MODEL_ID = "florence-community/Florence-2-base"
LEGACY_MODEL_ID = "microsoft/Florence-2-base"

PALETTE = ["#8b5cf6", "#22c55e", "#3b82f6", "#f59e0b", "#ec4899",
           "#14b8a6", "#f97316", "#ef4444", "#38bdf8", "#a3e635"]


@st.cache_resource(show_spinner=False)
def load_model():
    """Load Florence-2 with the modern native API, falling back to the legacy
    trust_remote_code path on older transformers installs. Returns
    (model, processor, device, dtype, backend_label)."""
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    # --- Preferred: native integration ---------------------------------------
    try:
        from transformers import AutoProcessor, Florence2ForConditionalGeneration

        model = Florence2ForConditionalGeneration.from_pretrained(
            NATIVE_MODEL_ID, dtype=dtype, device_map="auto" if device == "cuda" else None,
        )
        if device == "cpu":
            model = model.to(device)
        processor = AutoProcessor.from_pretrained(NATIVE_MODEL_ID)
        return model, processor, device, dtype, f"native ({NATIVE_MODEL_ID})"
    except Exception as native_err:
        # --- Fallback: legacy remote-code path --------------------------------
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM

            model = AutoModelForCausalLM.from_pretrained(
                LEGACY_MODEL_ID, trust_remote_code=True, torch_dtype=dtype,
                attn_implementation="eager",
            ).to(device)
            processor = AutoProcessor.from_pretrained(LEGACY_MODEL_ID, trust_remote_code=True)
            return model, processor, device, dtype, f"legacy ({LEGACY_MODEL_ID})"
        except Exception as legacy_err:
            raise RuntimeError(
                f"Could not load Florence-2 via the native API ({native_err!r}) "
                f"or the legacy trust_remote_code API ({legacy_err!r}). "
                "Check your internet connection and transformers/torch versions."
            )


def run_florence(image: Image.Image, task_prompt: str, text_input: str = None,
                  max_new_tokens: int = 1024, num_beams: int = 3):
    """Run a Florence-2 task prompt (optionally with extra text input) on an image."""
    import torch

    model, processor, device, dtype, _backend = load_model()
    prompt = task_prompt if text_input is None else task_prompt + text_input

    inputs = processor(text=prompt, images=image, return_tensors="pt")
    inputs = inputs.to(device=model.device, dtype=dtype) if device == "cuda" else inputs.to(device)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            do_sample=False,
        )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed = processor.post_process_generation(
        generated_text, task=task_prompt, image_size=(image.width, image.height)
    )
    return parsed[task_prompt]


def _font(size=14):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_boxes(image: Image.Image, bboxes, labels, box_width=3):
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    f = _font(14)
    for i, (box, label) in enumerate(zip(bboxes, labels)):
        color = PALETTE[i % len(PALETTE)]
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=box_width)
        text = str(label)
        tb = draw.textbbox((0, 0), text, font=f)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        ty = max(0, y1 - th - 8)
        draw.rectangle([x1, ty, x1 + tw + 10, ty + th + 6], fill=color)
        draw.text((x1 + 5, ty + 2), text, fill="black", font=f)
    return img


def draw_quad_boxes(image: Image.Image, quad_boxes, labels, box_width=2):
    """Used for OCR_WITH_REGION — polygons given as flat [x1,y1,x2,y2,x3,y3,x4,y4]."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    f = _font(12)
    for i, (quad, label) in enumerate(zip(quad_boxes, labels)):
        color = PALETTE[i % len(PALETTE)]
        pts = [(quad[j], quad[j + 1]) for j in range(0, len(quad), 2)]
        draw.polygon(pts, outline=color, width=box_width)
        x1, y1 = pts[0]
        draw.text((x1, max(0, y1 - 16)), str(label), fill=color, font=f)
    return img


TASK_REGISTRY = {
    "caption": {"title": "Image Captioning", "prompt": "<CAPTION>", "kind": "text"},
    "detailed_caption": {"title": "Detailed Caption", "prompt": "<DETAILED_CAPTION>", "kind": "text"},
    "more_detailed_caption": {"title": "More Detailed Caption", "prompt": "<MORE_DETAILED_CAPTION>", "kind": "text"},
    "od": {"title": "Object Detection", "prompt": "<OD>", "kind": "boxes"},
    "dense_region_caption": {"title": "Dense Region Caption", "prompt": "<DENSE_REGION_CAPTION>", "kind": "boxes"},
    "region_proposal": {"title": "Region Proposal", "prompt": "<REGION_PROPOSAL>", "kind": "boxes"},
    "ocr": {"title": "OCR", "prompt": "<OCR>", "kind": "text"},
    "ocr_region": {"title": "OCR with Region", "prompt": "<OCR_WITH_REGION>", "kind": "quad"},
    "phrase_grounding": {"title": "Caption-to-Phrase Grounding", "prompt": "<CAPTION_TO_PHRASE_GROUNDING>",
                          "kind": "boxes", "needs_text": True},
    "open_vocab": {"title": "Open Vocabulary Detection", "prompt": "<OPEN_VOCABULARY_DETECTION>",
                   "kind": "boxes", "needs_text": True},
}


def execute_task(image, key, text_input=None, max_new_tokens=1024, num_beams=3):
    """Run a task by key and return a normalized dict describing the result."""
    spec = TASK_REGISTRY[key]
    result = run_florence(image, spec["prompt"], text_input=text_input,
                           max_new_tokens=max_new_tokens, num_beams=num_beams)

    if spec["kind"] == "text":
        return {"kind": "text", "raw": result, "text": result}

    if spec["kind"] == "boxes":
        bboxes = result.get("bboxes", [])
        labels = result.get("labels", result.get("bboxes_labels", [""] * len(bboxes)))
        annotated = draw_boxes(image, bboxes, labels)
        return {"kind": "boxes", "raw": result, "bboxes": bboxes, "labels": labels, "annotated_image": annotated}

    if spec["kind"] == "quad":
        quads = result.get("quad_boxes", [])
        labels = result.get("labels", [""] * len(quads))
        annotated = draw_quad_boxes(image, quads, labels)
        return {"kind": "quad", "raw": result, "quad_boxes": quads, "labels": labels, "annotated_image": annotated}

    return {"kind": "unknown", "raw": result}


def backend_label():
    try:
        _, _, _, _, label = load_model()
        return label
    except Exception:
        return "not loaded"
