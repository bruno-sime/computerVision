"""Segmentacao classica por textura para uma fotografia.

O descritor de cada recorte tem 24 dimensoes: 8 filtros x 3 escalas.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy import ndimage
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


FILTER_NAMES = (
    "horizontal",
    "vertical",
    "diagonal_45",
    "diagonal_135",
    "laplaciano",
    "log",
    "difusao",
    "circular",
)


def build_filters() -> list[np.ndarray]:
    """Cria oito filtros de textura com suporte 7x7."""
    horizontal = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=float)
    vertical = horizontal.T
    diagonal_45 = np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], dtype=float)
    diagonal_135 = diagonal_45.T
    laplaciano = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=float)

    coordinates = np.arange(-3, 4)
    xx, yy = np.meshgrid(coordinates, coordinates)
    radius2 = xx**2 + yy**2
    log_filter = (radius2 - 4) * np.exp(-radius2 / 8)
    diffusion = np.exp(-radius2 / 4)
    diffusion[3, 3] -= diffusion.sum()
    circular = ((radius2 >= 4) & (radius2 <= 9)).astype(float)
    circular[3, 3] = -circular.sum()

    return [
        horizontal,
        vertical,
        diagonal_45,
        diagonal_135,
        laplaciano,
        log_filter,
        diffusion,
        circular,
    ]


def load_gray(path: Path) -> np.ndarray:
    image = ImageOps.exif_transpose(Image.open(path)).convert("L")
    return np.asarray(image, dtype=np.float32) / 255.0


def make_patches(image: np.ndarray, size: int, count: int) -> list[tuple[int, int, np.ndarray]]:
    """Seleciona recortes 512x512 em uma grade regular, sem ampliar a foto."""
    height, width = image.shape
    columns = max(1, int(np.sqrt(count * width / height)))
    rows = max(1, int(np.ceil(count / columns)))
    columns = min(columns, width // size)
    rows = min(rows, height // size)
    positions = [(row * size, column * size) for row in range(rows) for column in range(columns)]
    positions = positions[:count]
    return [(y, x, image[y : y + size, x : x + size]) for y, x in positions]


def resize_array(array: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    zoom = (shape[0] / array.shape[0], shape[1] / array.shape[1])
    return ndimage.zoom(array, zoom, order=1)


def extract_descriptors(
    image: np.ndarray, patches: list[tuple[int, int, np.ndarray]], patch_size: int
) -> np.ndarray:
    filters = build_filters()
    descriptors = np.zeros((len(patches), len(filters) * 3), dtype=float)
    for scale_index, scale in enumerate((1.0, 0.5, 0.25)):
        scaled_shape = (round(image.shape[0] * scale), round(image.shape[1] * scale))
        scaled = ndimage.gaussian_filter(image, sigma=1.0) if scale == 1.0 else resize_array(
            ndimage.gaussian_filter(image, sigma=1.0), scaled_shape
        )
        filtered = [ndimage.convolve(scaled, kernel, mode="reflect") for kernel in filters]
        for patch_index, (y, x, _) in enumerate(patches):
            scaled_y, scaled_x = round(y * scale), round(x * scale)
            scaled_size = max(1, round(patch_size * scale))
            for filter_index, response in enumerate(filtered):
                region = response[scaled_y : scaled_y + scaled_size, scaled_x : scaled_x + scaled_size]
                descriptors[patch_index, scale_index * len(filters) + filter_index] = np.mean(
                    np.abs(region)
                )
    return descriptors


def save_csv(
    path: Path,
    patches: list[tuple[int, int, np.ndarray]],
    descriptors: np.ndarray,
    labels: np.ndarray,
) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["recorte", "linha", "coluna", *[f"f{i:02d}" for i in range(24)], "grupo"])
        for index, ((y, x, _), descriptor, label) in enumerate(zip(patches, descriptors, labels)):
            writer.writerow([index, y, x, *[f"{value:.8f}" for value in descriptor], int(label)])


def save_montage(path: Path, patches: list[tuple[int, int, np.ndarray]], labels: np.ndarray) -> None:
    columns = 8
    rows = int(np.ceil(len(patches) / columns))
    figure, axes = plt.subplots(rows, columns, figsize=(16, 2 * rows))
    axes = np.atleast_1d(axes).ravel()
    colors = plt.get_cmap("tab10")
    for index, ((_, _, patch), label) in enumerate(zip(patches, labels)):
        axes[index].imshow(patch, cmap="gray", vmin=0, vmax=1)
        axes[index].set_title(f"recorte {index} | grupo {label + 1}", color=colors(label))
        axes[index].axis("off")
    for axis in axes[len(patches) :]:
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def save_overlay(path: Path, image: np.ndarray, patches: list[tuple[int, int, np.ndarray]], labels: np.ndarray) -> None:
    output = Image.fromarray(np.uint8(image * 255), mode="L").convert("RGB")
    draw = ImageDraw.Draw(output)
    colors = [(230, 57, 70), (29, 123, 138), (244, 162, 97), (42, 157, 143), (87, 117, 144)]
    for index, ((y, x, _), label) in enumerate(zip(patches, labels)):
        color = colors[int(label) % len(colors)]
        draw.rectangle((x, y, x + 512, y + 512), outline=color, width=8)
        draw.text((x + 12, y + 12), str(int(label) + 1), fill=color)
    output.save(path, quality=90, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=Path("image.jpg"))
    parser.add_argument("--output", type=Path, default=Path("resultados"))
    parser.add_argument("--patches", type=int, default=32)
    parser.add_argument("--groups", type=int, default=4)
    args = parser.parse_args()

    args.output.mkdir(exist_ok=True)
    image = load_gray(args.image)
    patches = make_patches(image, size=512, count=args.patches)
    if len(patches) < args.groups:
        raise ValueError("O numero de recortes deve ser maior ou igual ao numero de grupos.")

    descriptors = extract_descriptors(image, patches, patch_size=512)
    standardized = StandardScaler().fit_transform(descriptors)
    model = KMeans(n_clusters=args.groups, n_init=20, random_state=42)
    labels = model.fit_predict(standardized)

    np.save(args.output / "descritores_24d.npy", descriptors)
    save_csv(args.output / "descritores_24d.csv", patches, descriptors, labels)
    save_montage(args.output / "categorizacao_recortes.png", patches, labels)
    save_overlay(args.output / "categorizacao_imagem.jpg", image, patches, labels)
    print(f"Imagem: {image.shape[1]}x{image.shape[0]} pixels, tons de cinza")
    print(f"Recortes analisados: {len(patches)}")
    print(f"Descritores: {descriptors.shape} (8 filtros x 3 escalas)")
    print(f"Grupos: {args.groups}")
    print(f"Resultados salvos em: {args.output.resolve()}")


if __name__ == "__main__":
    main()