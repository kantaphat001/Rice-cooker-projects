"""
snapshot_manager.py - Smart Rice Cooker Adherence Snapshot Processor
Handles intelligent face cropping, resizing, and high-efficiency WebP compression.
Features:
- Face + Upper body context cropping (1.8x padding around detected face)
- Max dimension resize (default 400px) keeping original aspect ratio
- WebP encoding with 75% quality (~12-18 KB per snapshot vs 200+ KB JPEG)
- Automatic background retention cleanup (keeps latest 300 snapshots / 30 days)
- Atomic disk writes & RAM-disk caching (/dev/shm) for flash wear protection
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def crop_and_resize_face(
    frame: np.ndarray,
    face_box: Optional[np.ndarray] = None,
    target_max_dim: int = 400
) -> np.ndarray:
    """
    Intelligently crops face with upper torso context and resizes to target_max_dim.
    
    Args:
        frame: BGR numpy image array.
        face_box: Detection box [x, y, w, h, ...] from YuNet detector.
        target_max_dim: Maximum width or height of the output image.
    
    Returns:
        Cropped and resized BGR numpy image array.
    """
    if frame is None or frame.size == 0:
        return frame

    frame_h, frame_w = frame.shape[:2]
    cropped = frame

    # 1. Calculate Crop Box with Context Margin (1.8x face size for head & shoulders)
    if face_box is not None and len(face_box) >= 4:
        try:
            x, y, w, h = int(face_box[0]), int(face_box[1]), int(face_box[2]), int(face_box[3])
            if w > 10 and h > 10:
                cx = x + w // 2
                cy = y + h // 2
                # Generous bounding box for natural portrait context
                box_size = int(max(w, h) * 1.8)
                x1 = max(0, cx - box_size // 2)
                y1 = max(0, cy - box_size // 2)
                x2 = min(frame_w, cx + box_size // 2)
                y2 = min(frame_h, cy + box_size // 2)

                if (x2 - x1) > 20 and (y2 - y1) > 20:
                    cropped = frame[y1:y2, x1:x2]
        except Exception as e:
            logger.debug(f"[SnapshotManager] Face crop fallback to full frame: {e}")
            cropped = frame

    # 2. Resize to target_max_dim (Proportional downscale)
    cur_h, cur_w = cropped.shape[:2]
    if max(cur_h, cur_w) > target_max_dim:
        scale = target_max_dim / float(max(cur_h, cur_w))
        new_w = max(1, int(cur_w * scale))
        new_h = max(1, int(cur_h * scale))
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        resized = cropped

    return resized


def save_adherence_snapshot(
    frame: np.ndarray,
    face_box: Optional[np.ndarray],
    member_id: str,
    slot_key: str,
    snapshots_dir: Path,
    target_max_dim: int = 400,
    quality: int = 75
) -> Optional[str]:
    """
    Processes frame, encodes as WebP, saves to snapshots_dir, and triggers retention cleanup.
    
    Returns:
        The generated filename (e.g. 'snapshot_grandma_morning_1741004520.webp') or None on failure.
    """
    if frame is None or frame.size == 0:
        return None

    try:
        snapshots_dir = Path(snapshots_dir)
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        # 1. Crop & Resize
        processed = crop_and_resize_face(frame, face_box, target_max_dim=target_max_dim)

        # 2. Encode to WebP
        timestamp = int(time.time())
        clean_member = "".join(c for c in member_id if c.isalnum() or c in ("-", "_")).lower()
        clean_slot = "".join(c for c in slot_key if c.isalnum() or c in ("-", "_")).lower()
        filename = f"snapshot_{clean_member}_{clean_slot}_{timestamp}.webp"
        filepath = snapshots_dir / filename

        # Try WebP first (preferred for web performance and minimal disk usage)
        success, encoded = cv2.imencode(".webp", processed, [cv2.IMWRITE_WEBP_QUALITY, quality])
        if not success:
            # Fallback to JPEG if WebP encoder unavailable
            filename = f"snapshot_{clean_member}_{clean_slot}_{timestamp}.jpg"
            filepath = snapshots_dir / filename
            success, encoded = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, quality])

        if not success or encoded is None:
            logger.error("[SnapshotManager] Image encoding failed.")
            return None

        # 3. Atomic write to disk
        temp_path = filepath.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(encoded.tobytes())
        temp_path.replace(filepath)

        logger.info(f"[SnapshotManager] 📸 Saved WebP adherence snapshot: {filename} ({len(encoded)} bytes)")

        # 4. Optional cache in /dev/shm for instant zero-lag RAM read
        shm_dir = Path("/dev/shm")
        if shm_dir.exists():
            try:
                (shm_dir / "last_adherence_snapshot.webp").write_bytes(encoded.tobytes())
            except Exception:
                pass

        # 5. Background retention cleanup
        threading.Thread(
            target=cleanup_old_snapshots,
            args=(snapshots_dir,),
            daemon=True,
            name="SnapshotCleanup"
        ).start()

        return filename

    except Exception as e:
        logger.error(f"[SnapshotManager] Failed to process adherence snapshot: {e}")
        return None


def cleanup_old_snapshots(
    snapshots_dir: Path,
    max_files: int = 300,
    max_days: int = 30
):
    """
    Enforces rolling retention policy to protect Raspberry Pi storage:
    - Removes snapshots older than max_days.
    - Limits total snapshot files to max_files (keeps newest).
    """
    try:
        snapshots_dir = Path(snapshots_dir)
        if not snapshots_dir.is_dir():
            return

        now = time.time()
        max_age_sec = max_days * 86400

        files = []
        for p in snapshots_dir.glob("snapshot_*.*"):
            if p.is_file():
                try:
                    st = p.stat()
                    # Age check
                    if (now - st.st_mtime) > max_age_sec:
                        p.unlink(missing_ok=True)
                        logger.debug(f"[SnapshotManager] Purged expired snapshot: {p.name}")
                    else:
                        files.append((st.st_mtime, p))
                except Exception:
                    pass

        # Count check: keep only max_files newest
        if len(files) > max_files:
            files.sort(key=lambda x: x[0])  # Oldest first
            excess = len(files) - max_files
            for _, p in files[:excess]:
                try:
                    p.unlink(missing_ok=True)
                    logger.debug(f"[SnapshotManager] Purged excess snapshot: {p.name}")
                except Exception:
                    pass

    except Exception as e:
        logger.debug(f"[SnapshotManager] Retention cleanup error: {e}")
