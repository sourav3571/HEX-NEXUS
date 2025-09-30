from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import os
import shutil
import uuid
import numpy as np
import random 
import base64 # <-- NEW IMPORT
from typing import Union, Dict, Any, List

# -----------------------------------------------------------
# MOCK DEPENDENCIES (To make the file self-contained and runnable)
# These replace the 'from src.api.* import *' statements.
# -----------------------------------------------------------

# Mock Schemas for Pydantic (using basic classes for runtime compatibility)
class Dot:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class LinePath:
    def __init__(self, p1: Dot, p2: Dot):
        self.p1 = p1
        self.p2 = p2

class CurvePath:
    def __init__(self, p1: Dot, ctrl: Dot, p2: Dot):
        self.p1 = p1
        self.ctrl = ctrl
        self.p2 = p2

class KolamRequest:
    # This mock assumes the data passed in the API call matches the structure
    def __init__(self, dots: List[Dict[str, float]], paths: List[Dict[str, Any]]):
        self.dots = [Dot(x=d['x'], y=d['y']) for d in dots]
        # Paths mocking is simplified for demonstration purposes
        self.paths = []

# Mock src.api.llm (NEW MOCKS for LLM and SD)
def llm_image(base64_image: str, mime_type: str) -> Dict[str, Any]:
    """MOCK: Simulates calling Gemini/LLM for image-to-image enhancement."""
    print(f"MOCK LLM_IMAGE called with mime: {mime_type}")
    # Returning mock data (a placeholder for the enhanced image's base64 string)
    return {"base64_data": "mock_llm_enhanced_image_b64", "mime_type": "image/png"}

def sd_image(base64_image: str, prompt: str) -> str:
    """MOCK: Simulates calling Stable Diffusion for image-to-image enhancement."""
    print(f"MOCK SD_IMAGE called with prompt: {prompt[:30]}...")
    # Returning a mock result (a file ID/path reference)
    return f"sd_enhanced_{uuid.uuid4()}.png"

# Mock src.api.auth
class MockRouter:
    def __init__(self, prefix: str):
        self.prefix = prefix
auth_router = MockRouter(prefix="/api/auth")

# Mock src.api.recreate_logic
class KolamRecreator:
    def recreate(self, detected_dots: list[tuple[float, float]], file_path: str) -> str:
        """MOCK: Simulates complex recreation logic."""
        print(f"MOCK KolamRecreator processing {len(detected_dots)} dots.")
        return f"/img/recreated_{uuid.uuid4()}.svg"

# Mock src.api.inference
def predict(file_path: str) -> str:
    """MOCK: Simulates model prediction."""
    return "Mandala Kolam"

# Mock src.api.render
def render_kolam(dots: list[tuple[float, float]], paths: list[Union[LinePath, CurvePath]]) -> str:
    """MOCK: Simulates rendering the kolam to an SVG/PNG file."""
    print(f"MOCK Rendering {len(dots)} dots and {len(paths)} paths.")
    return f"/img/rendered_{uuid.uuid4()}.svg"

# Mock src.api.img_processing
def detect_dots_in_image(img: np.ndarray) -> list[tuple[float, float]]:
    """MOCK: Simulates dot detection."""
    if img is None: return []
    h, w, _ = img.shape
    return [(w*0.25, h*0.25), (w*0.75, h*0.25), (w*0.5, h*0.75)]

def detect_lines_and_curves(img: np.ndarray, dots: list[tuple[float, float]]) -> tuple[list[LinePath], list[CurvePath]]:
    """MOCK: Simulates path detection."""
    if len(dots) < 2: return [], []
    
    # Mock one line and one curve if enough dots exist
    dot1 = Dot(x=dots[0][0], y=dots[0][1])
    dot2 = Dot(x=dots[1][0], y=dots[1][1])
    lines = [LinePath(p1=dot1, p2=dot2)]
    
    if len(dots) >= 3:
        dot3 = Dot(x=dots[2][0], y=dots[2][1])
        ctrl_x = (dot1.x + dot3.x) / 2 + 50
        ctrl_y = (dot1.y + dot3.y) / 2 + 50
        ctrl = Dot(x=ctrl_x, y=ctrl_y)
        curves = [CurvePath(p1=dot1, ctrl=ctrl, p2=dot3)]
    else:
        curves = []
        
    return lines, curves

# Mock src.api.vector
def find_similar(file_path: str, top_k: int) -> list[tuple[str, float]]:
    """MOCK: Simulates finding similar kolams in a database."""
    return [
        (f"/imgdata/match1.png", 0.95),
        (f"/imgdata/match2.png", 0.92),
        (f"/imgdata/match3.png", 0.88),
    ]

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
        # np.clip is replaced with min/max for purity since numpy is not strictly required here
        symmetry = min(90, max(65, 90 - (dot_count / 10)))
        repetition = min(85, max(55, 85 - (len(paths) / 5)))
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


app = FastAPI(title="Kolam AI server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("img", exist_ok=True) 
os.makedirs("imgdata", exist_ok=True) # Ensure imgdata directory exists for mocks

app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/imgdata", StaticFiles(directory="imgdata"), name="imgdata")

app.include_router(auth_router, prefix="/api/auth")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------------------------------------
# NEW ROUTE: /api/llm for image enhancement via LLM
# -----------------------------------------------------------
@app.post("/api/llm")
async def get_better_image_with_llm(file: UploadFile = File(...)):
    """
    Enhances an uploaded image using an LLM (e.g., Gemini's image-to-image).
    Returns the enhanced image data (mocked as base64 string).
    """
    try:
        file_bytes = await file.read()
        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        # Call the mocked LLM image generation function
        result = llm_image(file_b64, mime_type=file.content_type)

        return {"llmRecreate": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"LLM enhancement failed: {str(e)}"})

# -----------------------------------------------------------
# NEW ROUTE: /api/stability for image enhancement via Stable Diffusion
# -----------------------------------------------------------
@app.post("/api/stability")
async def get_better_image_with_stability(file: UploadFile = File(...)):
    """
    Enhances an uploaded image using a Stable Diffusion model 
    with a fixed prompt for aesthetic, traditional rangoli style.
    Returns a file path reference to the enhanced image.
    """
    try:
        file_bytes = await file.read()
        file_b64 = base64.b64encode(file_bytes).decode("utf-8")

        prompt = "Make this rangoli (kolam) design more aesthetic, colorful, and traditional."
        # Call the mocked SD image generation function
        result = sd_image(file_b64, prompt=prompt)

        # Assuming result is a filename that will be served from the /img directory
        return {"llmRecreate": f"/img/{result}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Stability enhancement failed: {str(e)}"})
# -----------------------------------------------------------


@app.post("/api/create_kolam")
def create_kolam(data: KolamRequest):
    """Creates a kolam image based on provided dot and path coordinates."""
    
    # Convert Dot objects to tuples (x, y) for the rendering mock
    dot_tuples = [(dot.x, dot.y) for dot in data.dots]
    
    filename = render_kolam(
        dot_tuples,
        data.paths
    )
    return {"message": "Kolam created", "file": filename}


@app.post("/api/know-your-kolam")
async def know_your_kolam(file: UploadFile = File(...)):
    """Uploads an image, detects dots and paths, and calculates metrics."""
    tmp_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}_{file.filename}")
    try:
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = cv2.imread(tmp_path, cv2.IMREAD_COLOR)
        if img is None:
            return JSONResponse(status_code=400, content={"error": "Could not load image"})
        
        # --- ENHANCEMENT FOR DOT DETECTION: Applying contrast equalization ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        enhanced_img = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        
        detected_dots = detect_dots_in_image(enhanced_img)
        # --------------------------------------------------------------------
        
        dots = [Dot(x=float(x), y=float(y)) for x, y in detected_dots]
        
        lines, curves = detect_lines_and_curves(img, detected_dots)
        
        all_paths = []
        all_paths.extend(lines)
        all_paths.extend(curves)
        
        metrics = calculate_kolam_metrics(dots, all_paths)

        result = {
            "dots": [{"x": dot.x, "y": dot.y} for dot in dots],
            "paths": [],
            "metrics": metrics 
        }
        
        # Structure the paths for JSON response
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
        # Ensure proper logging of the error
        print(f"Error in /api/know-your-kolam: {e}")
        return JSONResponse(status_code=500, content={"error": f"Error processing image: {str(e)}"})
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/api/recreate")
async def recreate_kolam(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, runs dot detection, and uses the 
    KolamRecreator to generate a symmetric, clean SVG.
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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        enhanced_img = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
            
        detected_dots = detect_dots_in_image(enhanced_img)
        # --------------------------------------------------------------------
        
        # --- ATTEMPT COMPLEX RECREATION ---
        try:
            recreator = KolamRecreator()
            recreated_image_path = recreator.recreate(detected_dots, file_path) 
            return {"recreatedImage": recreated_image_path}
            
        except Exception as e:
            # --- FALLBACK: Generate Random Rangoli ---
            print(f"Kolam recreation failed ({str(e)}). Falling back to random rendering.")
            
            if not detected_dots:
                raise Exception("Kolam recreation failed and no dots were detected for fallback.")

            num_dots_to_connect = min(15, len(detected_dots))
            
            active_dots = random.sample(detected_dots, num_dots_to_connect)
            random_paths = []
            
            if len(active_dots) >= 2:
                # Loop through the dots and create LinePaths between them
                for i in range(len(active_dots)):
                    p1_tuple = active_dots[i]
                    p2_tuple = active_dots[(i + 1) % len(active_dots)] 
                    
                    p1 = Dot(x=p1_tuple[0], y=p1_tuple[1])
                    p2 = Dot(x=p2_tuple[0], y=p2_tuple[1])
                    
                    line_path = LinePath(p1=p1, p2=p2)
                    random_paths.append(line_path)
            
            # Use the original list of tuples (detected_dots) for rendering
            fallback_filename = render_kolam(
                detected_dots,
                random_paths
            )
            return {"recreatedImage": fallback_filename}

    except Exception as e:
        print(f"Error in /api/recreate: {e}")
        return JSONResponse(status_code=500, content={"error": f"Kolam processing failed: {str(e)}"})
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/api/predict")
async def predict_image(file: UploadFile = File(...)):
    """Predicts the type of kolam from the uploaded image."""
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = predict(file_path)
    os.remove(file_path)
    return {"prediction": result}

@app.post("/api/search")
async def search_similar(file: UploadFile = File(...)):
    """Searches for similar kolams in the database using vector embeddings."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = find_similar(file_path, top_k=5)
    os.remove(file_path)
    return {"matches": [p for p, d in results]}


if __name__ == "__main__":
    # Ensure UPLOAD_DIR is clear before running
    # This is useful for development but might be removed in production
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    
    # Mock file for /imgdata/match1.png etc. to prevent 404s for the search endpoint
    with open(os.path.join("imgdata", "match1.png"), "w") as f: f.write("") 
    with open(os.path.join("imgdata", "match2.png"), "w") as f: f.write("") 
    with open(os.path.join("imgdata", "match3.png"), "w") as f: f.write("") 

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
