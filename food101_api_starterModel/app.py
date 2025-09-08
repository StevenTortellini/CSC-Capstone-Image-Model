from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
import io

APP_TITLE = "Food-101 Classifier API"
APP_DESC = "FastAPI service that uses a Hugging Face Food-101 model for image classification."

app = FastAPI(title=APP_TITLE, description=APP_DESC)

# --- CORS (adjust in production) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load model on startup (Hugging Face: nateraw/food) ---
MODEL_ID = "nateraw/food"
device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
processor = None
model = None

@app.on_event("startup")
def load_model():
    global processor, model
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForImageClassification.from_pretrained(MODEL_ID)
    model.to(device)
    model.eval()

@app.get("/health")
def health():
    return {"status": "ok", "device": device, "model": MODEL_ID}

@app.post("/predict_food")
async def predict_food(file: UploadFile = File(...), top_k: int = 5):
    if top_k < 1 or top_k > 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        # Read file bytes and open image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image.")

    # Preprocess and move to device
    inputs = processor(images=image, return_tensors="pt")
    for k in inputs:
        inputs[k] = inputs[k].to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        values, indices = torch.topk(probs, k=top_k)

    id2label = model.config.id2label
    predictions = [
        {"label": id2label[idx.item()], "confidence": float(val.item())}
        for idx, val in zip(indices, values)
    ]

    return {"predictions": predictions}
