# FILE: server/src/api/enhancement.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import base64
from .llm import llm_image  # <-- Correct relative import
from .sd import sd_image    # <-- Correct relative import

enhancement_router = APIRouter()

@enhancement_router.post("/llm")
async def get_better_image_with_llm(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        result = llm_image(file_b64, mime_type=file.content_type)
        return {"llmRecreate": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"LLM enhancement failed: {str(e)}"})


@enhancement_router.post("/stability")
async def get_better_image_with_stability(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        prompt = "Make this rangoli (kolam) design more aesthetic, colorful, and traditional."
        result = sd_image(file_b64, prompt=prompt)
        return {"llmRecreate": f"/img/{result}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Stability enhancement failed: {str(e)}"})