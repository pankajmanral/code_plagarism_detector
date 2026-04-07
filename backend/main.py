"""
main.py — FastAPI application for the Code Plagiarism Detector.

Endpoints
---------
POST /compare    — Compare two code snippets
POST /upload     — Upload multiple files for pairwise comparison
GET  /history    — Retrieve past comparison results
POST /train      — (Re-)train the KNN model
DELETE /history  — Clear comparison history
GET  /health     — Health check
"""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CompareRequest, CompareResponse, SimilarityDetails,
    UploadResponse, PairResult,
    HistoryResponse, HistoryItem,
    TrainResponse, ErrorResponse,
)
from similarity import SimilarityEngine
from database import init_db, save_comparison, get_history, count_history, clear_history
from training_data import generate_training_pairs
from utils import validate_code


# ── Lifespan — initialise DB and optionally train KNN on startup ──────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic."""
    init_db()
    # Auto-train KNN if no saved model exists
    engine = get_engine()
    if engine.knn is None:
        print("⏳  Training KNN model on startup …")
        pairs, labels = generate_training_pairs()
        info = engine.train_knn(pairs, labels, n_neighbors=5)
        print(f"✅  KNN trained — accuracy {info['accuracy']:.2%} on {info['samples']} samples")
    yield
    print("👋  Shutting down.")


app = FastAPI(
    title="Code Plagiarism Detector",
    version="1.0.0",
    description="Detect code plagiarism using AST analysis + ML.",
    lifespan=lifespan,
)

# ── CORS — allow the React dev server ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Singleton engine ──────────────────────────────────────────────────────────
_engine: SimilarityEngine | None = None

def get_engine() -> SimilarityEngine:
    global _engine
    if _engine is None:
        _engine = SimilarityEngine()
    return _engine


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Simple health check."""
    engine = get_engine()
    return {
        "status": "ok",
        "knn_loaded": engine.knn is not None,
    }


@app.post("/compare", response_model=CompareResponse)
async def compare_code(req: CompareRequest):
    """
    Compare two code snippets and return a plagiarism verdict.
    """
    # Validate both inputs
    ok1, err1 = validate_code(req.code1, req.language)
    ok2, err2 = validate_code(req.code2, req.language)
    if not ok1:
        raise HTTPException(status_code=400, detail=f"Code 1 is invalid: {err1}")
    if not ok2:
        raise HTTPException(status_code=400, detail=f"Code 2 is invalid: {err2}")

    try:
        engine = get_engine()
        result = engine.compare(req.code1, req.code2, language=req.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # Persist to DB
    save_comparison(
        req.code1, req.code2,
        result["similarity_score"],
        result["plagiarism"],
        result["details"],
    )

    return CompareResponse(
        similarity_score=result["similarity_score"],
        plagiarism=result["plagiarism"],
        details=SimilarityDetails(**result["details"]),
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_files(language: str = "python", files: list[UploadFile] = File(...)):
    """
    Upload multiple files and compare every pair.
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Upload at least 2 files.")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files at once.")

    # Read file contents
    codes: list[str] = []
    names: list[str] = []
    for f in files:
        raw = await f.read()
        try:
            code = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' is not valid UTF-8 text.",
            )
        ok, err = validate_code(code, language)
        if not ok:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' contains invalid {language}: {err}",
            )
        codes.append(code)
        names.append(f.filename or f"file_{len(names)}")

    # Pairwise comparison
    engine = get_engine()
    raw_results = engine.compare_multiple(codes, language=language)

    pair_results: list[PairResult] = []
    for r in raw_results:
        i, j = r["file1_index"], r["file2_index"]
        save_comparison(
            codes[i], codes[j],
            r["similarity_score"], r["plagiarism"], r["details"],
        )
        pair_results.append(PairResult(
            file1_index=i,
            file2_index=j,
            file1_name=names[i],
            file2_name=names[j],
            similarity_score=r["similarity_score"],
            plagiarism=r["plagiarism"],
            details=SimilarityDetails(**r["details"]),
        ))

    return UploadResponse(
        results=pair_results,
        total_files=len(codes),
        total_comparisons=len(pair_results),
    )


@app.get("/history", response_model=HistoryResponse)
async def get_comparison_history(limit: int = 50, offset: int = 0):
    """Retrieve past comparison results."""
    items = get_history(limit, offset)
    total = count_history()
    return HistoryResponse(
        items=[HistoryItem(**item) for item in items],
        total=total,
    )


@app.delete("/history")
async def delete_history():
    """Clear all comparison history."""
    clear_history()
    return {"message": "History cleared."}


@app.post("/train", response_model=TrainResponse)
async def train_model():
    """(Re-)train the KNN model on the built-in dataset."""
    try:
        engine = get_engine()
        pairs, labels = generate_training_pairs()
        info = engine.train_knn(pairs, labels, n_neighbors=5)
        return TrainResponse(
            accuracy=info["accuracy"],
            samples=info["samples"],
            message="KNN model trained successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Training failed: {exc}")


# ── Run with:  python main.py  ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
