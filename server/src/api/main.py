from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from src.api.auth import router as auth_router
import uvicorn
import cv2
import os
import shutil
import uuid
import numpy as np
import base64
import random 
from src.api.recreate_logic import KolamRecreator 
from src.api.inference import predict
from src.api.render import render_kolam, reconstruct_paths
from src.api.schemas import KolamRequest, Dot, LinePath, CurvePath
from src.api.img_processing import detect_dots_in_image, detect_lines_and_curves
from src.api.vector import find_similar
from src.api.llm import llm_image, llm_prompt_for_kolam
from src.api.llm import sd_image
from typing import Union
import tempfile
import json

app = FastAPI(title="Kolam AI server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("img", exist_ok=True) 

app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/imgdata", StaticFiles(directory="imgdata"), name="imgdata")

app.include_router(auth_router, prefix="/api/auth")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------------------------------------
# Placeholder for Mathematical Metric Calculation
# -----------------------------------------------------------
def calculate_kolam_metrics(dots: list[Dot], paths: list[Union[LinePath, CurvePath]]) -> dict:
    """
    Simulates the calculation of complex geometric metrics.
    """
    dot_count = len(dots)
    
    # Simple heuristic for symmetry/repetition simulation
    if dot_count > 0 and dot_count % 9 == 0:
        symmetry = 98.5
        repetition = 95.0
        pattern_type = "Rotational C4/Reflectional"
    elif dot_count > 0:
        symmetry = np.clip(90 - (dot_count / 10), 65, 90)
        repetition = np.clip(85 - (len(paths) / 5), 55, 85)
        pattern_type = "Bilateral/Flowing"
    else:
        symmetry = 0.0
        repetition = 0.0
        pattern_type = "Undefined"
        
    return {
        "dot_count": dot_count,
        "path_count": len(paths),
        "symmetry_percentage": round(float(symmetry), 2),
        "repetition_percentage": round(float(repetition), 2),
        "pattern_type": pattern_type
    }

# -----------------------------------------------------------


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

@app.post("/api/know-and-create-kolam")
async def know_and_create_kolam(file: UploadFile = File(...)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(await file.read())
    tmp.close()

    try:
        # Step 1: Load image
        img = cv2.imread(tmp.name, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "Could not load image"}

        # Step 2: Detect dots + paths
        detected_dots = detect_dots_in_image(img)
        dots = [Dot(x=float(x), y=float(y)) for x, y in detected_dots]
        lines, curves = detect_lines_and_curves(img, detected_dots)

        kolam_json = {
            "dots": [{"x": d.x, "y": d.y} for d in dots],
            "paths": []
        }

        for path in [*lines, *curves]:
            if isinstance(path, LinePath):
                kolam_json["paths"].append({
                    "type": "line",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })
            elif isinstance(path, CurvePath):
                kolam_json["paths"].append({
                    "type": "curve",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "ctrl": {"x": path.ctrl.x, "y": path.ctrl.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })

        # Step 3: Improve with LLM (safe)
        improved_json = llm_prompt_for_kolam(kolam_json)

        # Step 4: Validate and render
        validated = KolamRequest(**improved_json)
        output_filename = render_kolam(
            [(dot.x, dot.y) for dot in validated.dots],
            validated.paths
        )

        # Optional: Validate against schema
        try:
            validated = KolamRequest(**improved_json)
        except Exception as e:
            print(f"⚠️ Invalid LLM schema: {e}")
            validated = KolamRequest(**kolam_json)

        # Step 5: Render final enhanced kolam
        output_filename = render_kolam(
            [(dot.x, dot.y) for dot in validated.dots],
            validated.paths
        )

        return {
            "message": "Kolam analyzed, enhanced by LLM, and created successfully",
            "image_url": output_filename,
        }

    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

    finally:
        os.remove(tmp.name)

# -----------------------------------------------------------
# FIXED ROUTE: /api/recreate endpoint using KolamRecreator
# -----------------------------------------------------------
@app.post("/api/recreate")
async def recreate_kolam(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, runs dot detection, and uses the 
    KolamRecreator to generate a symmetric, clean SVG. Includes a random 
    fallback if the complex recreation logic fails.
    """
    
    file_id = uuid.uuid4()
    file_path = os.path.join(UPLOAD_DIR, f"original_{file_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if img is None:
            raise Exception("Could not load image for recreation")

        # --- ENHANCEMENT FOR DOT DETECTION: Applying contrast equalization ---
        # Convert to grayscale for robust processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply contrast enhancement (CLAHE) to handle uneven lighting/faint dots
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        # Convert back to 3-channel BGR as detect_dots_in_image may expect it
        enhanced_img = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
            
        detected_dots = detect_dots_in_image(enhanced_img)
        # --------------------------------------------------------------------
        
        # --- ATTEMPT COMPLEX RECREATION ---
        try:
            recreator = KolamRecreator()
            # detected_dots is List[Tuple[float, float]]
            # Pass the path to the original file for the recreation logic to read
            recreated_image_path = recreator.recreate(detected_dots, file_path) 
            return {"recreatedImage": recreated_image_path}
            
        except Exception as e:
            # --- FALLBACK: Generate Random Rangoli ---
            print(f"Kolam recreation failed ({str(e)}). Falling back to random rendering.")
            
            if not detected_dots:
                raise Exception("Kolam recreation failed and no dots were detected for fallback.")

            num_dots_to_connect = min(15, len(detected_dots))
            
            # Select dots to be part of the random pattern
            active_dots = random.sample(detected_dots, num_dots_to_connect)
            random_paths = []
            
            if len(active_dots) >= 2:
                # Loop through the dots and create LinePaths between them
                for i in range(len(active_dots)):
                    p1_tuple = active_dots[i]
                    p2_tuple = active_dots[(i + 1) % len(active_dots)] 
                    
                    # Create Dot objects for LinePath
                    p1 = Dot(x=p1_tuple[0], y=p1_tuple[1])
                    p2 = Dot(x=p2_tuple[0], y=p2_tuple[1])
                    
                    # NOTE: Using LinePath for the simple random fallback
                    line_path = LinePath(p1=p1, p2=p2)
                    random_paths.append(line_path)
            
            # Use the original list of tuples (detected_dots) for rendering
            fallback_filename = render_kolam(
                detected_dots,
                random_paths
            )
            return {"recreatedImage": fallback_filename}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Kolam processing failed: {str(e)}"})
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/api/predict")
async def predict_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = predict(file_path)
    os.remove(file_path)
    return {"prediction": result}

@app.post("/api/llm")
async def get_better_image_with_llm(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_b64 = base64.b64encode(file_bytes).decode("utf-8")
    result = llm_image(file_b64, mime_type=file.content_type)

    return {"llmRecreate": result}

@app.post("/api/stability")
async def get_better_image_with_stability(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_b64 = base64.b64encode(file_bytes).decode("utf-8")

    prompt = "Make this rangoli (kolam) design more aesthetic, colorful, and traditional."
    result = sd_image(file_b64, prompt=prompt)

    return {"llmRecreate": f"/img/{result}"}

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