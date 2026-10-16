"""
face_database.py - Family Member Face Database Manager
Stores known face embeddings for family members (e.g. grandpa, grandma).
Matches incoming frames against known profiles using Cosine Similarity.
"""

import os
import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, List

from .yunet_detector import YuNetDetector
from .sface_recognizer import SFaceRecognizer

logger = logging.getLogger(__name__)

class FaceDatabase:
    def __init__(self, dataset_dir: Path, detector: YuNetDetector, recognizer: SFaceRecognizer,
                 match_threshold: float = 0.85):
        self.dataset_dir = Path(dataset_dir)
        self.detector = detector
        self.recognizer = recognizer
        self.match_threshold = match_threshold

        self.cache_file = self.dataset_dir / "embeddings.npz"
        self._members_embeddings: Dict[str, List[np.ndarray]] = {}
        self.load_or_rebuild()

    def load_or_rebuild(self):
        if self.cache_file.is_file():
            try:
                data = np.load(str(self.cache_file), allow_pickle=True)
                loaded = {}
                for k in data.files:
                    loaded[k] = list(data[k])
                self._members_embeddings = loaded
                logger.info(f"[FaceDB] Loaded {len(self._members_embeddings)} family members from cache.")
                return
            except Exception as e:
                logger.warning(f"[FaceDB] Cache file corrupted, rebuilding: {e}")

        self.rebuild_database()

    def rebuild_database(self):
        """Scans dataset/<member_id>/*.jpg, extracts features and saves cache."""
        logger.info("[FaceDB] Rebuilding face database from images...")
        self._members_embeddings = {}

        if not self.dataset_dir.is_dir():
            self.dataset_dir.mkdir(parents=True, exist_ok=True)
            return

        for member_dir in self.dataset_dir.iterdir():
            if not member_dir.is_dir():
                continue

            member_id = member_dir.name
            embeddings = []

            for img_path in member_dir.glob("*.jpg"):
                img = cv2.imread(str(img_path))
                if img is None:
                    continue

                faces = self.detector.detect(img)
                if faces is not None and len(faces) > 0:
                    best_face = faces[0]
                    feat = self.recognizer.extract_feature(img, best_face)
                    if feat is not None:
                        embeddings.append(feat)

            if embeddings:
                self._members_embeddings[member_id] = embeddings
                logger.info(f"[FaceDB] Enrolled '{member_id}' with {len(embeddings)} image samples.")

        # Save to cache
        if self._members_embeddings:
            np.savez(str(self.cache_file), **self._members_embeddings)
            logger.info(f"[FaceDB] Saved embeddings cache to {self.cache_file}")

    def identify(self, frame: np.ndarray) -> Tuple[Optional[str], float, Optional[np.ndarray]]:
        """
        Detects and recognizes face in frame.
        Returns:
            (member_id, confidence, face_box)
            or ("unknown", confidence, face_box)
            or (None, 0.0, None) if no face detected.
        """
        if frame is None or not self.detector.is_ready or not self.recognizer.is_ready:
            return None, 0.0, None

        faces = self.detector.detect(frame)
        if faces is None or len(faces) == 0:
            return None, 0.0, None

        # Take largest detected face
        best_face = faces[0]
        feat = self.recognizer.extract_feature(frame, best_face)
        if feat is None:
            return None, 0.0, None

        best_member = "unknown"
        highest_score = 0.0

        for member_id, feats in self._members_embeddings.items():
            for stored_feat in feats:
                score = self.recognizer.match(feat, stored_feat)
                if score > highest_score:
                    highest_score = score
                    best_member = member_id

        if highest_score >= self.match_threshold:
            logger.info(f"[FaceDB] Identified: {best_member} (Confidence: {highest_score:.2f})")
            return best_member, highest_score, best_face
        else:
            logger.debug(f"[FaceDB] Face below threshold: {best_member} (Confidence: {highest_score:.2f})")
            return "unknown", highest_score, best_face
