#!/usr/bin/env python3
"""3D->2D projection experiment using the checkerboard as world reference.

For each selected calibration image:
- detect the 9x6 inner corners;
- estimate board pose with solvePnP;
- project a 50 mm cube and XYZ axes using projectPoints;
- save the projected 2D pixel coordinates to CSV;
- compare reprojection of known checkerboard corners with detected corners.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2 as cv
import numpy as np


def detect_checkerboard(gray, pattern):
    flags_sb = cv.CALIB_CB_NORMALIZE_IMAGE | cv.CALIB_CB_EXHAUSTIVE | cv.CALIB_CB_ACCURACY
    ok, corners = cv.findChessboardCornersSB(gray, pattern, flags=flags_sb)
    if ok:
        return True, corners.astype(np.float32)
    ok, corners = cv.findChessboardCorners(gray, pattern, cv.CALIB_CB_ADAPTIVE_THRESH | cv.CALIB_CB_NORMALIZE_IMAGE)
    if ok:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 40, 0.001)
        corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    return ok, corners


def draw_cube(img, pts):
    p = np.int32(np.round(pts.reshape(-1, 2)))
    # bottom square 0..3, top square 4..7
    for a, b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
        cv.line(img, tuple(p[a]), tuple(p[b]), (255, 0, 255), 3, cv.LINE_AA)
    for i, q in enumerate(p):
        cv.circle(img, tuple(q), 6, (0, 255, 255), -1, cv.LINE_AA)
        cv.putText(img, str(i), tuple(q + np.array([8, -8])), cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv.LINE_AA)


def draw_axes(img, pts):
    p = np.int32(np.round(pts.reshape(-1, 2)))
    o, x, y, z = map(tuple, p)
    cv.line(img, o, x, (0, 0, 255), 4, cv.LINE_AA)   # X
    cv.line(img, o, y, (0, 255, 0), 4, cv.LINE_AA)   # Y
    cv.line(img, o, z, (255, 0, 0), 4, cv.LINE_AA)   # Z
    cv.putText(img, "X", x, cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv.LINE_AA)
    cv.putText(img, "Y", y, cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2, cv.LINE_AA)
    cv.putText(img, "Z", z, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2, cv.LINE_AA)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--calibration", default="results/calibration.npz")
    p.add_argument("--images", default="images/calibration")
    p.add_argument("--output", default="results/projection")
    p.add_argument("--limit", type=int, default=5, help="Maximo de imagens para o experimento")
    p.add_argument("--cube-mm", type=float, default=50.0)
    args = p.parse_args()

    data = np.load(args.calibration)
    K = data["camera_matrix"]
    dist = data["dist_coeffs"]
    pattern = tuple(int(x) for x in data["pattern_size"])
    square_mm = float(data["square_mm"])
    cols, rows = pattern

    objp = np.zeros((rows * cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    objp *= square_mm

    s = args.cube_mm
    cube = np.float32([
        [0, 0, 0], [s, 0, 0], [s, s, 0], [0, s, 0],
        [0, 0, -s], [s, 0, -s], [s, s, -s], [0, s, -s],
    ])
    axes = np.float32([[0,0,0], [s,0,0], [0,s,0], [0,0,-s]])

    image_dir = Path(args.images)
    paths = sorted([*image_dir.glob("*.jpg"), *image_dir.glob("*.jpeg"), *image_dir.glob("*.png")])
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    done = 0
    for path in paths:
        if done >= args.limit:
            break
        img = cv.imread(str(path))
        if img is None:
            continue
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        found, corners = detect_checkerboard(gray, pattern)
        if not found:
            continue

        success, rvec, tvec = cv.solvePnP(objp, corners, K, dist, flags=cv.SOLVEPNP_ITERATIVE)
        if not success:
            continue

        projected_board, _ = cv.projectPoints(objp, rvec, tvec, K, dist)
        err_vec = np.linalg.norm(corners.reshape(-1,2) - projected_board.reshape(-1,2), axis=1)
        rmse = float(np.sqrt(np.mean(err_vec ** 2)))
        mean_err = float(np.mean(err_vec))

        projected_cube, _ = cv.projectPoints(cube, rvec, tvec, K, dist)
        projected_axes, _ = cv.projectPoints(axes, rvec, tvec, K, dist)

        vis = img.copy()
        draw_cube(vis, projected_cube)
        draw_axes(vis, projected_axes)
        cv.putText(vis, f"Reprojection RMSE: {rmse:.3f} px", (20, 42), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 2, cv.LINE_AA)
        out_image = out_dir / f"{path.stem}_projection.jpg"
        cv.imwrite(str(out_image), vis)

        csv_path = out_dir / f"{path.stem}_projected_points.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["point", "X_mm", "Y_mm", "Z_mm", "u_px", "v_px"])
            for i, (p3, p2) in enumerate(zip(cube, projected_cube.reshape(-1,2))):
                writer.writerow([f"cube_{i}", *map(float, p3), float(p2[0]), float(p2[1])])

        # A small sample of detected vs projected known checkerboard points.
        compare_path = out_dir / f"{path.stem}_verification.csv"
        sample_idx = np.linspace(0, len(objp)-1, num=min(10, len(objp)), dtype=int)
        with compare_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["index", "X_mm", "Y_mm", "Z_mm", "detected_u", "detected_v", "projected_u", "projected_v", "error_px"])
            det = corners.reshape(-1,2)
            proj = projected_board.reshape(-1,2)
            for idx in sample_idx:
                writer.writerow([
                    int(idx), *map(float, objp[idx]),
                    float(det[idx,0]), float(det[idx,1]),
                    float(proj[idx,0]), float(proj[idx,1]),
                    float(np.linalg.norm(det[idx] - proj[idx]))
                ])

        summary_rows.append([path.name, rmse, mean_err, str(out_image.name)])
        print(f"{path.name}: RMSE={rmse:.4f}px -> {out_image}")
        done += 1

    if done == 0:
        raise SystemExit("Nenhuma imagem adequada encontrada para o experimento.")

    with (out_dir / "projection_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "reprojection_rmse_px", "mean_error_px", "output_image"])
        writer.writerows(summary_rows)

    print(f"Experimento concluido em {done} imagem(ns). Resultados: {out_dir}")


if __name__ == "__main__":
    main()
