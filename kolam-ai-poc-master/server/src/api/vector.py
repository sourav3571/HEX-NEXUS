# src/api/vector.py
import os
import pickle
from typing import List, Tuple
import numpy as np
import torch
import clip
from PIL import Image
import faiss

DATA_DIR = "imgdata"
INDEX_FILE = "image_index.faiss"
META_FILE = "image_paths.pkl"

# Load CLIP model (cached on first use)
device = "cuda" if torch.cuda.is_available() else "cpu"
_model, _preprocess = clip.load("ViT-B/32", device=device)

# Global FAISS index + metadata
_index = None
_image_paths: List[str] = []


def _get_embedding(image_path: str) -> np.ndarray:
    """Convert image to CLIP embedding."""
    image = _preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = _model.encode_image(image)
    return embedding.cpu().numpy().astype("float32")


def build_index(save: bool = True) -> None:
    """Build FAISS index from all images in data folder."""
    global _index, _image_paths
    _image_paths = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not _image_paths:
        raise RuntimeError(f"No images found in {DATA_DIR}/ folder.")

    embeddings = [_get_embedding(p) for p in _image_paths]
    embeddings = np.vstack(embeddings)

    d = embeddings.shape[1]
    _index = faiss.IndexFlatL2(d)
    _index.add(embeddings)

    if save:
        save_index()


def save_index() -> None:
    """Persist FAISS index and metadata to disk."""
    if _index is None:
        raise RuntimeError("No index to save. Build it first.")

    faiss.write_index(_index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(_image_paths, f)


def load_index() -> None:
    """Load FAISS index and metadata from disk if available."""
    global _index, _image_paths
    if not (os.path.exists(INDEX_FILE) and os.path.exists(META_FILE)):
        raise RuntimeError("No saved index found. Build it first.")

    _index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        _image_paths = pickle.load(f)


def find_similar(image_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Find top_k similar images from the dataset.
    Returns list of (image_path, distance).
    """
    global _index
    if _index is None:
        try:
            load_index()
        except RuntimeError:
            build_index()

    query_vec = _get_embedding(image_path)
    distances, indices = _index.search(query_vec, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        results.append((_image_paths[idx], float(dist)))

    return results
