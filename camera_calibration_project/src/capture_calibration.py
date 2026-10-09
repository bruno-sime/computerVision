#!/usr/bin/env python3
"""Capture calibration images from a webcam on macOS.

Default checkerboard: 9x6 INNER corners (10x7 squares), 25 mm squares.
Controls:
  SPACE or c : save current frame (only when checkerboard is detected)
  f          : save frame even if checkerboard is not detected
  r          : delete all images captured in this session
  q or ESC   : quit

Examples:
  python src/capture_calibration.py --camera 1
  python src/capture_calibration.py --scan
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2 as cv


def open_camera(index: int, width: int, height: int) -> cv.VideoCapture:
    # CAP_AVFOUNDATION is the native macOS camera backend.
    cap = cv.VideoCapture(index, cv.CAP_AVFOUNDATION)
    if not cap.isOpened():
        # Fallback for environments where OpenCV chooses a backend automatically.
        cap.release()
        cap = cv.VideoCapture(index)

    if cap.isOpened():
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        # Not all webcams/backends honor these values; this is fine.
        cap.set(cv.CAP_PROP_FPS, 30)
    return cap


def scan_cameras(max_index: int, width: int, height: int) -> None:
    print("Procurando cameras disponiveis...")
    found = []
    for idx in range(max_index + 1):
        cap = open_camera(idx, width, height)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                h, w = frame.shape[:2]
                found.append((idx, w, h))
                print(f"  indice {idx}: abriu com {w}x{h}")
        cap.release()
    if not found:
        print("Nenhuma camera foi aberta. Verifique permissao de Camera para Terminal/Python no macOS.")
    else:
        print("\nUse o indice da Logitech, por exemplo: --camera 1")
        print("Se houver FaceTime + Logitech, a Logitech costuma ser um indice diferente da camera interna.")


def detect_checkerboard(gray, pattern_size: tuple[int, int]):
    # SB is typically more robust for modern OpenCV versions.
    flags_sb = cv.CALIB_CB_NORMALIZE_IMAGE | cv.CALIB_CB_EXHAUSTIVE | cv.CALIB_CB_ACCURACY
    found, corners = cv.findChessboardCornersSB(gray, pattern_size, flags=flags_sb)
    if found:
        return True, corners

    flags = cv.CALIB_CB_ADAPTIVE_THRESH | cv.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv.findChessboardCorners(gray, pattern_size, flags)
    if found:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 40, 0.001)
        corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    return found, corners


def main() -> None:
    parser = argparse.ArgumentParser(description="Captura 30 imagens para calibracao de camera.")
    parser.add_argument("--camera", type=int, default=1, help="Indice da camera. No Mac, tente 1 para Logitech externa.")
    parser.add_argument("--scan", action="store_true", help="Testa indices de camera e sai.")
    parser.add_argument("--max-index", type=int, default=5, help="Maior indice testado com --scan.")
    parser.add_argument("--count", type=int, default=30, help="Numero alvo de imagens.")
    parser.add_argument("--cols", type=int, default=9, help="Cantos internos por linha.")
    parser.add_argument("--rows", type=int, default=6, help="Cantos internos por coluna.")
    parser.add_argument("--width", type=int, default=1920, help="Largura desejada da captura.")
    parser.add_argument("--height", type=int, default=1080, help="Altura desejada da captura.")
    parser.add_argument("--output", default="images/calibration", help="Pasta de saida.")
    args = parser.parse_args()

    if args.scan:
        scan_cameras(args.max_index, args.width, args.height)
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = open_camera(args.camera, args.width, args.height)
    if not cap.isOpened():
        raise SystemExit(
            f"Nao foi possivel abrir a camera {args.camera}. "
            "Execute com --scan e verifique a permissao de Camera do macOS."
        )

    saved_this_session: list[Path] = []
    pattern = (args.cols, args.rows)
    window = "Captura para calibracao - SPACE salva | q sai"
    cv.namedWindow(window, cv.WINDOW_NORMAL)

    print(f"Camera {args.camera} aberta. Alvo: {args.count} imagens.")
    print("Varie angulo, distancia e posicao do tabuleiro; cubra centro e bordas da imagem.")

    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            print("Falha ao ler frame da camera.")
            break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        found, corners = detect_checkerboard(gray, pattern)

        display = frame.copy()
        if found:
            cv.drawChessboardCorners(display, pattern, corners, True)
            status = "TABULEIRO DETECTADO - SPACE para salvar"
            status_color = (0, 255, 0)
        else:
            status = "Tabuleiro nao detectado"
            status_color = (0, 0, 255)

        total = len(saved_this_session)
        cv.putText(display, status, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 0.85, status_color, 2, cv.LINE_AA)
        cv.putText(display, f"Fotos desta sessao: {total}/{args.count}", (20, 78), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(display, "SPACE/c salva | f forca | r limpa sessao | q sai", (20, 116), cv.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv.LINE_AA)

        cv.imshow(window, display)
        key = cv.waitKey(1) & 0xFF

        if key in (ord("q"), 27):
            break
        elif key in (ord(" "), ord("c")):
            if not found:
                print("Nao salvo: tabuleiro nao detectado. Ajuste a pose ou pressione 'f' para forcar.")
                continue
            filename = out_dir / f"calib_{int(time.time() * 1000)}_{total + 1:02d}.jpg"
            if cv.imwrite(str(filename), frame):
                saved_this_session.append(filename)
                print(f"Salvo: {filename}")
        elif key == ord("f"):
            filename = out_dir / f"calib_forced_{int(time.time() * 1000)}_{total + 1:02d}.jpg"
            if cv.imwrite(str(filename), frame):
                saved_this_session.append(filename)
                print(f"Salvo (forcado): {filename}")
        elif key == ord("r"):
            for path in saved_this_session:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            saved_this_session.clear()
            print("Imagens desta sessao removidas.")

        if len(saved_this_session) >= args.count:
            print(f"Meta atingida: {args.count} imagens salvas.")
            break

    cap.release()
    cv.destroyAllWindows()
    print(f"Fim. {len(saved_this_session)} imagens salvas nesta sessao em {out_dir}.")


if __name__ == "__main__":
    main()
