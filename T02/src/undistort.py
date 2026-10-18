#!/usr/bin/env python3
"""Undistort one image or all images in a directory using saved calibration."""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2 as cv
import numpy as np


def process(path: Path, out_dir: Path, K, dist, alpha: float) -> None:
    img = cv.imread(str(path))
    if img is None:
        print(f"Ignorando {path}: nao abriu")
        return
    h, w = img.shape[:2]
    newK, roi = cv.getOptimalNewCameraMatrix(K, dist, (w, h), alpha, (w, h))
    und = cv.undistort(img, K, dist, None, newK)

    # Save full corrected image and a side-by-side comparison.
    out_dir.mkdir(parents=True, exist_ok=True)
    cv.imwrite(str(out_dir / f"{path.stem}_undistorted.jpg"), und)

    left = img.copy()
    right = und.copy()
    cv.putText(left, "Original", (20, 45), cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3, cv.LINE_AA)
    cv.putText(right, "Corrigida", (20, 45), cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3, cv.LINE_AA)
    comparison = np.hstack([left, right])
    cv.imwrite(str(out_dir / f"{path.stem}_comparison.jpg"), comparison)

    x, y, rw, rh = roi
    print(f"{path.name}: ROI recomendado x={x}, y={y}, w={rw}, h={rh}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--calibration", default="results/calibration.npz")
    p.add_argument("--input", default="images/calibration", help="Arquivo ou pasta")
    p.add_argument("--output", default="results/undistorted")
    p.add_argument("--alpha", type=float, default=1.0, help="1 preserva mais FOV; 0 reduz bordas pretas")
    args = p.parse_args()

    data = np.load(args.calibration)
    K = data["camera_matrix"]
    dist = data["dist_coeffs"]

    inp = Path(args.input)
    if inp.is_file():
        paths = [inp]
    else:
        paths = sorted([*inp.glob("*.jpg"), *inp.glob("*.jpeg"), *inp.glob("*.png")])
    if not paths:
        raise SystemExit(f"Nenhuma imagem encontrada em {inp}")

    out_dir = Path(args.output)
    for path in paths:
        process(path, out_dir, K, dist, args.alpha)


if __name__ == "__main__":
    main()
