from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
from sahi import AutoDetectionModel
from PIL import Image
import io
import os

from src.infer_app import sahi_single_inference  # update if needed

app = FastAPI()

# Add CORS (unchanged)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once
detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov5',
    model_path='models/best.pt',
    confidence_threshold=0.2,
    device='cpu'
)

@app.post("/predict-image/")
async def predict_image(file: UploadFile = File(...)):
    # Save uploaded image to temp location
    os.makedirs("../frontend/api_temp", exist_ok=True)
    image_path = f"../frontend/api_temp/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())

    # Run inference
    output_path = "../frontend/api_temp/predicted.png"
    sahi_single_inference(
        image_path=image_path,
        detection_model=detection_model,
        output_path=output_path,
        font_path="Arial_Bold.ttf"
    )

    return FileResponse(output_path, media_type="image/png") 
