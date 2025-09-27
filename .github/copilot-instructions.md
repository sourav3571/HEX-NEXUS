# AI Development Guide for Kolam Image Processing Project

This guide helps AI agents understand the key architecture, patterns and workflows of the Kolam image processing project.

## Project Architecture

### Frontend (React + TypeScript + Vite)
- Located in `/client`
- Core components in `/client/src/components`
- API integration through `/client/src/lib/axios` and `/client/src/lib/api`
- Main interface in `Home.tsx` handles image uploads and API interactions

### Backend (Python FastAPI)
- Located in `/server`
- Core APIs in `/server/src/api/main.py`
- Image processing in `/server/src/api/vector.py` 
- Uses CLIP + FAISS for image similarity search

## Key Integration Points

### API Endpoints
- `POST /api/know-your-kolam`: Analyzes kolam patterns in uploaded images
- `POST /api/predict`: Image classification 
- `POST /api/search`: Finds similar images using CLIP embeddings
- `POST /api/create_kolam`: Renders kolam based on dots and paths data

### Data Flow
1. Frontend uploads images as `FormData` with `multipart/form-data` content type
2. Backend processes images using OpenCV for pattern detection
3. CLIP model generates image embeddings for similarity search
4. Results returned as JSON with paths to processed/generated images

## Development Workflows

### Server Setup
```bash
cd server
pip install -r requirements.txt
# Start server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Client Setup 
```bash
cd client
npm install
npm run dev
```

### Image Processing Pipeline
1. Image uploads stored temporarily in `server/uploads/`
2. Pattern detection extracts dots and paths
3. CLIP embeddings stored in FAISS index at `server/image_index.faiss`
4. Generated kolams saved in `server/img/`

## Project Conventions

### Backend
- Use `tempfile` for handling uploaded files
- Clean up temporary files after processing
- Update FAISS index when adding new images to dataset
- Handle image processing errors gracefully

### Frontend
- Use React Query mutations for API calls
- Maintain operation history for user actions
- Handle multipart/form-data uploads appropriately
- Preview images before upload

## Important Files to Reference
- Frontend API setup: `client/src/lib/axios/axios.ts`
- Image processing: `server/src/api/vector.py`
- Main API routes: `server/src/api/main.py`
- Core UI: `client/src/components/pages/Home.tsx`