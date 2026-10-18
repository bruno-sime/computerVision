#!/usr/bin/env python3
"""Retifica imagens de um tabuleiro plano por homografia.

O caso de uso reutiliza as fotos de calibracao do T02. Os cantos internos do
tabuleiro fornecem correspondencias coplanares e permitem gerar uma vista
superior (bird's-eye view) com cv.getPerspectiveTransform/warpPerspective.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import cv2 as cv
import numpy as np


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="../T02/images/calibration", help="Imagem ou pasta de imagens")
    parser.add_argument("--output", default="results", help="Pasta de saida")
    parser.add_argument("--cols", type=int, default=9, help="Cantos internos por linha")
    parser.add_argument("--rows", type=int, default=6, help="Cantos internos por coluna")
    parser.add_argument("--square-px", type=int, default=100, help="Pixels por quadrado na saida")
    parser.add_argument("--calibration", help="Arquivo .npz de calibracao para remover distorcao antes da homografia")
    parser.add_argument("--limit", type=int, default=0, help="Processar no maximo N imagens (0 = todas)")
    return parser.parse_args()


def image_paths(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    if not source.is_dir():
        raise SystemExit(f"Entrada inexistente: {source}")
    return sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)


def detect_checkerboard(gray: np.ndarray, pattern: tuple[int, int]) -> tuple[bool, np.ndarray | None]:
    flags_sb = cv.CALIB_CB_NORMALIZE_IMAGE | cv.CALIB_CB_EXHAUSTIVE | cv.CALIB_CB_ACCURACY
    found, corners = cv.findChessboardCornersSB(gray, pattern, flags=flags_sb)
    if found:
        return True, corners.astype(np.float32)

    flags = cv.CALIB_CB_ADAPTIVE_THRESH | cv.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv.findChessboardCorners(gray, pattern, flags)
    if found:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 50, 0.001)
        corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        return True, corners.astype(np.float32)
    return False, None


def extreme_corners(corners: np.ndarray, cols: int, rows: int) -> np.ndarray:
    """Retorna TL, TR, BR, BL conforme a ordem da grade detectada."""
    grid = corners.reshape(rows, cols, 2)
    return np.float32([grid[0, 0], grid[0, -1], grid[-1, -1], grid[-1, 0]])


def destination_corners(cols: int, rows: int, square_px: int) -> tuple[np.ndarray, tuple[int, int]]:
    # 9x6 cantos internos correspondem a 10x7 quadrados. A primeira linha de
    # cantos fica a um quadrado da borda externa, e o mesmo vale para a ultima.
    width = (cols + 1) * square_px
    height = (rows + 1) * square_px
    dst = np.float32(
        [
            [square_px, square_px],
            [cols * square_px, square_px],
            [cols * square_px, rows * square_px],
            [square_px, rows * square_px],
        ]
    )
    return dst, (width, height)


def load_calibration(path: str | None) -> tuple[np.ndarray, np.ndarray] | None:
    if not path:
        return None
    calibration_path = Path(path)
    if not calibration_path.exists():
        raise SystemExit(f"Calibracao inexistente: {calibration_path}")
    data = np.load(calibration_path)
    return data["camera_matrix"], data["dist_coeffs"]


def add_label(image: np.ndarray, text: str) -> None:
    cv.rectangle(image, (0, 0), (image.shape[1], 54), (20, 24, 32), -1)
    cv.putText(image, text, (18, 37), cv.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv.LINE_AA)


def comparison(original: np.ndarray, rectified: np.ndarray) -> np.ndarray:
    target_h = 620
    left_w = round(original.shape[1] * target_h / original.shape[0])
    right_w = round(rectified.shape[1] * target_h / rectified.shape[0])
    left = cv.resize(original, (left_w, target_h), interpolation=cv.INTER_AREA)
    right = cv.resize(rectified, (right_w, target_h), interpolation=cv.INTER_AREA)
    add_label(left, "Imagem original e regiao detectada")
    add_label(right, "Vista superior retificada")
    gap = np.full((target_h, 12, 3), 245, dtype=np.uint8)
    return np.hstack([left, gap, right])


def json_matrix(matrix: np.ndarray) -> list[list[float]]:
    return [[round(float(value), 10) for value in row] for row in matrix]


def process_one(
    path: Path,
    output: Path,
    pattern: tuple[int, int],
    square_px: int,
    calibration: tuple[np.ndarray, np.ndarray] | None,
) -> dict[str, object]:
    image = cv.imread(str(path))
    if image is None:
        return {"image": path.name, "status": "read_error"}

    working = image
    used_lens_correction = False
    if calibration is not None:
        camera_matrix, dist_coeffs = calibration
        working = cv.undistort(image, camera_matrix, dist_coeffs)
        used_lens_correction = True

    gray = cv.cvtColor(working, cv.COLOR_BGR2GRAY)
    found, corners = detect_checkerboard(gray, pattern)
    # Em poses muito obliquas, a interpolacao da remocao de distorcao pode
    # dificultar a deteccao. A imagem original continua sendo uma entrada
    # valida para a homografia e serve como alternativa automatica.
    if (not found or corners is None) and calibration is not None:
        working = image
        used_lens_correction = False
        gray = cv.cvtColor(working, cv.COLOR_BGR2GRAY)
        found, corners = detect_checkerboard(gray, pattern)
    if not found or corners is None:
        return {"image": path.name, "status": "not_detected"}

    src = extreme_corners(corners, *pattern)
    dst, output_size = destination_corners(*pattern, square_px)
    homography = cv.getPerspectiveTransform(src, dst)
    rectified = cv.warpPerspective(
        working,
        homography,
        output_size,
        flags=cv.INTER_CUBIC,
        borderMode=cv.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )

    annotated = working.copy()
    cv.drawChessboardCorners(annotated, pattern, corners, True)
    polygon = np.round(src).astype(np.int32).reshape(-1, 1, 2)
    cv.polylines(annotated, [polygon], True, (0, 70, 255), 5, cv.LINE_AA)

    stem = path.stem
    annotated_path = output / "annotated" / f"{stem}_corners.jpg"
    rectified_path = output / "rectified" / f"{stem}_topdown.jpg"
    comparison_path = output / "comparisons" / f"{stem}_comparison.jpg"
    cv.imwrite(str(annotated_path), annotated, [cv.IMWRITE_JPEG_QUALITY, 94])
    cv.imwrite(str(rectified_path), rectified, [cv.IMWRITE_JPEG_QUALITY, 94])
    cv.imwrite(str(comparison_path), comparison(annotated, rectified), [cv.IMWRITE_JPEG_QUALITY, 92])

    projected = cv.perspectiveTransform(src.reshape(-1, 1, 2), homography).reshape(-1, 2)
    rmse = float(np.sqrt(np.mean(np.sum((projected - dst) ** 2, axis=1))))
    return {
        "image": path.name,
        "status": "ok",
        "lens_distortion_corrected": used_lens_correction,
        "input_size_px": [int(image.shape[1]), int(image.shape[0])],
        "output_size_px": list(output_size),
        "source_corners_px": src.round(3).tolist(),
        "destination_corners_px": dst.tolist(),
        "homography": json_matrix(homography),
        "control_point_rmse_px": rmse,
        "annotated": str(annotated_path),
        "rectified": str(rectified_path),
        "comparison": str(comparison_path),
    }


def prepare_directories(output: Path) -> None:
    for name in ("annotated", "rectified", "comparisons"):
        (output / name).mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    if args.cols < 2 or args.rows < 2 or args.square_px < 10:
        raise SystemExit("Use pelo menos 2x2 cantos e 10 pixels por quadrado.")

    source = Path(args.input)
    paths = image_paths(source)
    if args.limit > 0:
        paths = paths[: args.limit]
    if not paths:
        raise SystemExit(f"Nenhuma imagem encontrada em {source}")

    output = Path(args.output)
    prepare_directories(output)
    pattern = (args.cols, args.rows)
    calibration = load_calibration(args.calibration)

    records: list[dict[str, object]] = []
    for index, path in enumerate(paths, start=1):
        record = process_one(path, output, pattern, args.square_px, calibration)
        records.append(record)
        print(f"[{index:02d}/{len(paths):02d}] {path.name}: {record['status']}")

    successes = [record for record in records if record["status"] == "ok"]
    summary = {
        "application": "Retificacao perspectiva de tabuleiro plano",
        "input": str(source),
        "calibration": args.calibration,
        "lens_distortion_corrected": calibration is not None,
        "pattern_inner_corners": [args.cols, args.rows],
        "board_squares": [args.cols + 1, args.rows + 1],
        "square_px": args.square_px,
        "images_total": len(paths),
        "images_successful": len(successes),
        "images_failed": len(paths) - len(successes),
        "records": records,
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nConcluido: {len(successes)}/{len(paths)} imagens retificadas.")
    print(f"Resumo: {summary_path}")
    if not successes:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

