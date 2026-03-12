from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
from predict import predict
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")

async def predict_image(file: UploadFile = File(...)):

    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    overlay = predict(image)

    _, buffer = cv2.imencode(".png", overlay)

    return {
        "overlay": buffer.tobytes().hex()
    }
