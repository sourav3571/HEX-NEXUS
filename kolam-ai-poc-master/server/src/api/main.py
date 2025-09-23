from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import cv2
import tempfile
import os
import shutil
import uuid

from src.api.inference import predict
from src.api.render import render_kolam
from src.api.schemas import KolamRequest, Dot, LinePath, CurvePath
from src.api.img_processing import detect_dots_in_image, detect_lines_and_curves
from src.api.vector import find_similar

app = FastAPI(title="Kolam AI server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/imgdata", StaticFiles(directory="imgdata"), name="imgdata")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/create_kolam")
def create_kolam(data: KolamRequest):
    filename = render_kolam(
        [(dot.x, dot.y) for dot in data.dots],
        data.paths
    )
    return {"message": "Kolam created", "file": filename}


@app.post("/api/know-your-kolam")
async def know_your_kolam(file: UploadFile = File(...)):
    # Save uploaded file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(await file.read())
    tmp.close()
    
    try:
        # Load and process image
        img = cv2.imread(tmp.name, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "Could not load image"}
        
        h, w = img.shape[:2]
        
        # Step 1: Detect dots in the image
        detected_dots = detect_dots_in_image(img)
        
        # Convert to Dot objects
        dots = [Dot(x=float(x), y=float(y)) for x, y in detected_dots]
        
        # Step 2: Detect lines and curves
        lines, curves = detect_lines_and_curves(img, detected_dots)
        
        # Combine all paths
        all_paths = []
        for line in lines:
            all_paths.append(line)
        for curve in curves:
            all_paths.append(curve)
        
        # Step 3: Return formatted response that matches KolamRequest schema
        result = {
            "dots": [{"x": dot.x, "y": dot.y} for dot in dots],
            "paths": []
        }
        
        # Format paths according to schema
        for path in all_paths:
            if isinstance(path, LinePath):
                result["paths"].append({
                    "type": "line",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })
            elif isinstance(path, CurvePath):
                result["paths"].append({
                    "type": "curve",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "ctrl": {"x": path.ctrl.x, "y": path.ctrl.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })
        
        return result
        
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}
    
@app.post("/api/predict")
async def predict_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = predict(file_path)
    os.remove(file_path)
    return {"prediction": result}

@app.post("/api/search")
async def search_similar(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = find_similar(file_path, top_k=5)
    os.remove(file_path)
    return {"matches": [p for p, d in results]}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)