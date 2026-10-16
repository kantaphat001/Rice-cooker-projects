"""
yunet_detector.py - OpenCV YuNet ONNX Face Detector
Ultra-lightweight (~300KB) fast neural face detector running on OpenCV DNN.
"""

import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class YuNetDetector:
    def __init__(self, model_path: Path, conf_threshold: float = 0.8, nms_threshold: float = 0.3):
        self.model_path = str(model_path)
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self._detector = None

        if Path(self.model_path).is_file():
            try:
                # Initialize with a nominal size (640x480)
                self._detector = cv2.FaceDetectorYN.create(
                    self.model_path,
                    "",
                    (640, 480),
                    score_threshold=self.conf_threshold,
                    nms_threshold=self.nms_threshold,
                    top_k=5000
                )
                self._input_size = (640, 480)
                logger.info(f"[YuNet] Loaded model from {self.model_path}")
            except Exception as e:
                logger.error(f"[YuNet] Failed to initialize FaceDetectorYN: {e}")
        else:
            logger.warning(f"[YuNet] Model file not found at {self.model_path}")

    @property
    def is_ready(self) -> bool:
        return self._detector is not None

    def detect(self, image: np.ndarray):
        """
        Detects faces in BGR image.
        Returns:
            faces: numpy array where each row represents:
                   [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rc, y_rc, x_lc, y_lc, score]
        """
        if not self.is_ready or image is None:
            return None

        h, w = image.shape[:2]
        if self._input_size != (w, h):
            self._detector.setInputSize((w, h))
            self._input_size = (w, h)

        _, faces = self._detector.detect(image)
        return faces
