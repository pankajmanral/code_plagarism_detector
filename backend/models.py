"""
models.py — Pydantic request / response schemas for the FastAPI endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    """Body for ``POST /compare``."""
    code1: str = Field(..., min_length=1, description="First source code snippet")
    code2: str = Field(..., min_length=1, description="Second source code snippet")
    language: str = Field("python", description="Language of the code snippets (python, javascript, java, cpp)")


# ── Response Models ───────────────────────────────────────────────────────────

class SimilarityDetails(BaseModel):
    """Breakdown of the similarity analysis."""
    node_similarity: float = Field(..., ge=0, le=1)
    structure_similarity: float = Field(..., ge=0, le=1)
    cosine_similarity: float = Field(..., ge=0, le=1)
    knn_prediction: Optional[bool] = Field(None)
    knn_confidence: Optional[float] = Field(None, ge=0, le=1)
    knn_distance: Optional[float] = Field(None)
    ast_nodes_1: int = Field(0, description="Total AST nodes in snippet 1")
    ast_nodes_2: int = Field(0, description="Total AST nodes in snippet 2")


class CompareResponse(BaseModel):
    """Response for ``POST /compare``."""
    similarity_score: float = Field(..., ge=0, le=1, description="Combined plagiarism score (0–1)")
    plagiarism: bool = Field(..., description="True if score ≥ 0.70")
    details: SimilarityDetails


class PairResult(BaseModel):
    """One pairwise comparison result inside ``POST /upload``."""
    file1_index: int
    file2_index: int
    file1_name: str = ""
    file2_name: str = ""
    similarity_score: float = Field(..., ge=0, le=1)
    plagiarism: bool
    details: SimilarityDetails


class UploadResponse(BaseModel):
    """Response for ``POST /upload``."""
    results: list[PairResult]
    total_files: int
    total_comparisons: int


class HistoryItem(BaseModel):
    """Single record from comparison history."""
    id: int
    timestamp: str
    similarity_score: float
    plagiarism: bool
    code1_preview: str = ""
    code2_preview: str = ""


class HistoryResponse(BaseModel):
    """Response for ``GET /history``."""
    items: list[HistoryItem]
    total: int


class TrainResponse(BaseModel):
    """Response for ``POST /train``."""
    accuracy: float
    samples: int
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str = ""
