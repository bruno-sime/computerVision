#!/usr/bin/env python3
"""Calibrate one camera from checkerboard images and save parameters/results."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2 as cv
import numpy as np


def detect_checkerboard(gray, pattern_size):
    flags_sb = cv.CALIB_CB_NORMALIZE_IMAGE | cv.CALIB_CB_EXHAUSTIVE | cv.CALIB_CB_ACCURACY
    found, corners = cv.findChessboardCornersSB(gray, pattern_size, flags=flags_sb)
    if found:
        return True, corners.astype(np.float32)

    flags = cv.CALIB_CB_ADAPTIVE_THRESH | cv.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv.findChessboardCorners(gray, pattern_size, flags)
    if found:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 40, 0.001)
        corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    return found, corners


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--images", default="images/calibration")
    p.add_argument("--cols", type=int, default=9)
    p.add_argument("--rows", type=int, default=6)
    p.add_argument("--square-mm", type=float, default=25.0)
    p.add_argument("--output", default="results/calibration.npz")
    p.add_argument("--json", default="results/calibration.json")
    p.add_argument("--corners-dir", default="results/corners")
    args = p.parse_args()

    pattern = (args.cols, args.rows)
    image_dir = Path(args.images)
    paths = sorted([*image_dir.glob("*.jpg"), *image_dir.glob("*.jpeg"), *image_dir.glob("*.png")])
    if not paths:
        raise SystemExit(f"Nenhuma imagem encontrada em {image_dir}")

    objp = np.zeros((args.rows * args.cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2)
    objp *= args.square_mm

    object_points = []
    image_points = []
    used_paths = []
    image_size = None

    corners_dir = Path(args.corners_dir)
    corners_dir.mkdir(parents=True, exist_ok=True)

    for path in paths:
        image = cv.imread(str(path))
        if image is None:
            continue
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        current_size = gray.shape[::-1]
        if image_size is None:
            image_size = current_size
        elif current_size != image_size:
            print(f"Ignorando {path.name}: resolucao {current_size}, esperada {image_size}")
            continue

        found, corners = detect_checkerboard(gray, pattern)
        if not found:
            print(f"NAO detectado: {path.name}")
            continue

        object_points.append(objp.copy())
        image_points.append(corners)
        used_paths.append(path)
        annotated = image.copy()
        cv.drawChessboardCorners(annotated, pattern, corners, True)
        cv.imwrite(str(corners_dir / path.name), annotated)
        print(f"OK: {path.name}")

    if len(object_points) < 10:
        raise SystemExit(f"Somente {len(object_points)} imagens validas. Recomenda-se pelo menos 10-15; capture mais poses.")

    rms, K, dist, rvecs, tvecs = cv.calibrateCamera(
        object_points, image_points, image_size, None, None
    )

    per_view_errors = []
    all_sq_error = 0.0
    all_points = 0
    for i, (obj, img_pts) in enumerate(zip(object_points, image_points)):
        projected, _ = cv.projectPoints(obj, rvecs[i], tvecs[i], K, dist)
        diff = img_pts.reshape(-1, 2) - projected.reshape(-1, 2)
        errors = np.linalg.norm(diff, axis=1)
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mean = float(np.mean(errors))
        per_view_errors.append((used_paths[i].name, rmse, mean))
        all_sq_error += float(np.sum(errors ** 2))
        all_points += len(errors)

    global_rmse = float(np.sqrt(all_sq_error / all_points))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out_path,
        camera_matrix=K,
        dist_coeffs=dist,
        rvecs=np.array(rvecs),
        tvecs=np.array(tvecs),
        image_size=np.array(image_size),
        pattern_size=np.array(pattern),
        square_mm=np.array(args.square_mm),
    )

    report = {
        "image_size": list(image_size),
        "checkerboard_inner_corners": [args.cols, args.rows],
        "square_size_mm": args.square_mm,
        "images_found": len(paths),
        "images_used": len(used_paths),
        "opencv_rms": float(rms),
        "reprojection_global_rmse_px": global_rmse,
        "camera_matrix": K.tolist(),
        "distortion_coefficients": dist.reshape(-1).tolist(),
        "used_images": [p.name for p in used_paths],
    }
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    csv_path = Path(args.json).with_name("reprojection_errors.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "rmse_px", "mean_error_px"])
        writer.writerows(per_view_errors)

    print("\n=== RESULTADO ===")
    print(f"Imagens utilizadas: {len(used_paths)}/{len(paths)}")
    print(f"Resolucao: {image_size[0]}x{image_size[1]}")
    print(f"OpenCV RMS: {rms:.6f}")
    print(f"RMSE global de reprojecao: {global_rmse:.6f} px")
    print("\nMatriz intrinseca K:\n", K)
    print("\nCoeficientes de distorcao:\n", dist.reshape(-1))
    print(f"\nSalvo em: {out_path}, {args.json}, {csv_path}")


if __name__ == "__main__":
    main()
