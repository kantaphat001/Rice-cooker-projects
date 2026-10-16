"""
sface_recognizer.py - OpenCV SFace ONNX Feature Extractor
Extracts 128-dimensional L2-normalized embeddings from aligned facial crops.
Matches faces via Cosine Similarity.
"""

import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SFaceRecognizer:
    def __init__(self, model_path: Path):
        self.model_path = str(model_path)
        self._recognizer = None

        if Path(self.model_path).is_file():
            try:
                self._recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")
                logger.info(f"[SFace] Loaded model from {self.model_path}")
            except Exception as e:
                logger.error(f"[SFace] Failed to initialize FaceRecognizerSF: {e}")
        else:
            logger.warning(f"[SFace] Model file not found at {self.model_path}")

    @property
    def is_ready(self) -> bool:
        return self._recognizer is not None

    def extract_feature(self, image: np.ndarray, face_box_with_landmarks: np.ndarray) -> np.ndarray:
        """
        Aligns cropped face and extracts 128-D embedding vector.
        """
        if not self.is_ready or image is None or face_box_with_landmarks is None:
            return None

        try:
            aligned_face = self._recognizer.alignCrop(image, face_box_with_landmarks)
            feature = self._recognizer.feature(aligned_face)
            return feature
        except Exception as e:
            logger.error(f"[SFace] Feature extraction error: {e}")
            return None

    def match(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """
        Computes cosine similarity between two 128-D feature vectors.
        Returns value between 0.0 and 1.0.
        """
        if not self.is_ready or feat1 is None or feat2 is None:
            return 0.0

        try:
            score = self._recognizer.match(feat1, feat2, cv2.FaceRecognizerSF_FR_COSINE)
            return float(score)
        except Exception as e:
            logger.error(f"[SFace] Match calculation error: {e}")
            return 0.0
