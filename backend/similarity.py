"""
similarity.py — Plagiarism detection engine.

Provides two complementary approaches:
  1. **Cosine Similarity** — direct vector comparison (unsupervised)
  2. **KNN Classifier**   — trained on labelled pairs (supervised)

The public API is the ``SimilarityEngine`` class.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from feature_extractor import FeatureExtractor


# ── Paths ─────────────────────────────────────────────────────────────────────
_MODEL_DIR = Path(__file__).parent / "saved_models"
_KNN_MODEL_PATH = _MODEL_DIR / "knn_model.pkl"
_SCALER_PATH = _MODEL_DIR / "scaler.pkl"


class SimilarityEngine:
    """
    Compare two pieces of Python source code and return a plagiarism verdict.

    Usage
    -----
    >>> engine = SimilarityEngine()
    >>> result = engine.compare(code_a, code_b)
    >>> result["similarity_score"]   # 0.0 – 1.0
    >>> result["plagiarism"]         # True / False
    """

    PLAGIARISM_THRESHOLD = 0.70  # ≥ 70 % → plagiarism

    def __init__(self, extractor: Optional[FeatureExtractor] = None):
        self.extractor = extractor or FeatureExtractor()
        self.knn: Optional[KNeighborsClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self._load_model()
        # Cache for extractors per language
        self._extractors: dict[str, FeatureExtractor] = {}
        if extractor:
            self._extractors[extractor.language] = extractor

    # ── Public API ────────────────────────────────────────────────────────
    def compare(self, code1: str, code2: str, language: str = 'python') -> dict:
        """
        Full comparison pipeline.
        """
        extractor = self._get_extractor(language)
        
        # 1. Parse and extract metadata (needed for counts)
        tree1 = extractor.parser.parse(code1)
        tree2 = extractor.parser.parse(code2)
        n1 = extractor.parser.count_nodes(tree1)
        n2 = extractor.parser.count_nodes(tree2)

        # 2. Extract feature vectors
        vec1 = extractor.extract(code1)
        vec2 = extractor.extract(code2)

        # ── Cosine similarity on the full vector ──────────────────────────
        cos_sim = self._cosine_similarity(vec1, vec2)

        # ── Component-level similarities ──────────────────────────────────
        node_sim = self._node_similarity(vec1, vec2)
        struct_sim = self._structure_similarity(vec1, vec2)

        # ── KNN prediction (if model is loaded) ──────────────────────────
        knn_pred: Optional[bool] = None
        knn_conf: float = 0.0
        knn_dist: Optional[float] = None
        
        if self.knn is not None and self.scaler is not None:
            knn_pred, knn_conf = self._knn_predict(vec1, vec2)
            # Fetch actual distance to neighbors
            diff = np.abs(vec1 - vec2).reshape(1, -1)
            diff_scaled = self.scaler.transform(diff)
            dists, _ = self.knn.kneighbors(diff_scaled)
            knn_dist = float(np.mean(dists))

        # ── Combined score ────────────────────────────────────────────────
        # Weighted blend: 60 % cosine, 25 % node, 15 % structure
        combined = 0.60 * cos_sim + 0.25 * node_sim + 0.15 * struct_sim

        # If KNN is available, blend its confidence in
        if knn_pred is not None:
            knn_score = knn_conf if knn_pred else (1.0 - knn_conf)
            combined = 0.50 * combined + 0.50 * knn_score

        combined = float(np.clip(combined, 0.0, 1.0))
        is_plagiarism = combined >= self.PLAGIARISM_THRESHOLD

        return {
            "similarity_score": round(combined, 4),
            "plagiarism": is_plagiarism,
            "details": {
                "node_similarity": round(float(node_sim), 4),
                "structure_similarity": round(float(struct_sim), 4),
                "cosine_similarity": round(float(cos_sim), 4),
                "knn_prediction": knn_pred,
                "knn_confidence": round(float(knn_conf), 4) if knn_pred is not None else None,
                "knn_distance": round(float(knn_dist), 4) if knn_dist is not None else None,
                "ast_nodes_1": n1,
                "ast_nodes_2": n2,
            },
        }

    def compare_multiple(self, codes: list[str], language: str = 'python') -> list[dict]:
        """
        Pairwise comparison of *codes*.
        """
        n = len(codes)
        results: list[dict] = []
        for i in range(n):
            for j in range(i + 1, n):
                result = self.compare(codes[i], codes[j], language=language)
                result["file1_index"] = i
                result["file2_index"] = j
                results.append(result)
        return results

    # ── Training ──────────────────────────────────────────────────────────
    def train_knn(
        self,
        pairs: list[tuple[str, str]],
        labels: list[int],
        language: str = 'python',
        n_neighbors: int = 5,
    ) -> dict:
        """
        Train the KNN model on labelled code pairs.
        """
        X = self._pairs_to_features(pairs, language=language)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.knn = KNeighborsClassifier(
            n_neighbors=min(n_neighbors, len(labels)),
            weights='distance',
            metric='euclidean',
        )
        self.knn.fit(X_scaled, labels)

        accuracy = float(self.knn.score(X_scaled, labels))
        self._save_model()

        return {"accuracy": round(accuracy, 4), "samples": len(labels)}

    # ── Internals ─────────────────────────────────────────────────────────
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Cosine similarity between two feature vectors."""
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        sim = cosine_similarity(v1.reshape(1, -1), v2.reshape(1, -1))
        return float(sim[0, 0])

    def _node_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Cosine similarity on node-frequency features only
        (first 40 dimensions of the vector).
        """
        from feature_extractor import NUM_NODE_FEATURES
        n1 = v1[:NUM_NODE_FEATURES]
        n2 = v2[:NUM_NODE_FEATURES]
        if np.linalg.norm(n1) == 0 or np.linalg.norm(n2) == 0:
            return 0.0
        sim = cosine_similarity(n1.reshape(1, -1), n2.reshape(1, -1))
        return float(sim[0, 0])

    def _structure_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Similarity based on structural + semantic features
        (dimensions beyond node frequencies).
        """
        from feature_extractor import NUM_NODE_FEATURES
        s1 = v1[NUM_NODE_FEATURES:]
        s2 = v2[NUM_NODE_FEATURES:]
        if np.linalg.norm(s1) == 0 or np.linalg.norm(s2) == 0:
            return 0.0
        # Use 1 - normalised Euclidean distance
        diff = np.linalg.norm(s1 - s2)
        max_norm = max(np.linalg.norm(s1), np.linalg.norm(s2), 1e-10)
        return float(max(0.0, 1.0 - diff / max_norm))

    def _knn_predict(self, v1: np.ndarray, v2: np.ndarray) -> tuple[bool, float]:
        """Run KNN prediction on the difference vector of two samples."""
        diff = np.abs(v1 - v2).reshape(1, -1)
        diff_scaled = self.scaler.transform(diff)
        pred = self.knn.predict(diff_scaled)[0]
        proba = self.knn.predict_proba(diff_scaled)[0]
        confidence = float(max(proba))
        return bool(pred == 1), confidence

    def _pairs_to_features(self, pairs: list[tuple[str, str]], language: str = 'python') -> np.ndarray:
        """Convert code pairs into difference-vector feature matrix."""
        rows: list[np.ndarray] = []
        extractor = self._get_extractor(language)
        for code_a, code_b in pairs:
            va = extractor.extract(code_a)
            vb = extractor.extract(code_b)
            rows.append(np.abs(va - vb))
        return np.array(rows)

    def _get_extractor(self, language: str) -> FeatureExtractor:
        """Get or create an extractor for the given language."""
        if language not in self._extractors:
            self._extractors[language] = FeatureExtractor(language=language)
        return self._extractors[language]

    # ── Persistence ───────────────────────────────────────────────────────
    def _save_model(self) -> None:
        _MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(_KNN_MODEL_PATH, 'wb') as f:
            pickle.dump(self.knn, f)
        with open(_SCALER_PATH, 'wb') as f:
            pickle.dump(self.scaler, f)

    def _load_model(self) -> None:
        """Load the KNN and Scaler models, validating feature counts."""
        if _KNN_MODEL_PATH.exists() and _SCALER_PATH.exists():
            try:
                with open(_KNN_MODEL_PATH, 'rb') as f:
                    knn = pickle.load(f)
                with open(_SCALER_PATH, 'rb') as f:
                    scaler = pickle.load(f)
                
                # Validate feature dimensions
                expected = len(self.extractor.feature_names())
                # StandardScaler in recent sklearn has n_features_in_
                actual = getattr(scaler, 'n_features_in_', None)
                
                if actual is not None and actual != expected:
                    print(f"⚠️  Model feature mismatch: expected {expected}, got {actual}. Trashing old model.")
                    self.knn = None
                    self.scaler = None
                else:
                    self.knn = knn
                    self.scaler = scaler
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")
                self.knn = None
                self.scaler = None
