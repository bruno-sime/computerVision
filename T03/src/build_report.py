#!/usr/bin/env python3
"""Gera o relatorio-artigo do T03 em PDF a partir dos resultados."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


GIT_URL = "https://github.com/bruno-sime/computerVision/tree/main/T03"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="results/summary.json")
    parser.add_argument("--output", default="docs/relatorio_artigo.pdf")
    return parser.parse_args()


def fit_image(path: Path, max_width: float, max_height: float) -> Image:
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(2 * cm, 1.55 * cm, A4[0] - 2 * cm, 1.55 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.drawString(2 * cm, 1.15 * cm, "T03 - Visao Computacional e Percepcao")
    canvas.drawRightString(A4[0] - 2 * cm, 1.15 * cm, f"Pagina {document.page}")
    canvas.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ArticleTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=14,
        ),
        "author": ParagraphStyle(
            "Author",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=18,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            alignment=TA_JUSTIFY,
            leftIndent=0.7 * cm,
            rightIndent=0.7 * cm,
            spaceAfter=9,
        ),
        "heading": ParagraphStyle(
            "Heading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=colors.HexColor("#0F4C81"),
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.7,
            leading=14.2,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceBefore=4,
            spaceAfter=10,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.6,
            leading=12,
            leftIndent=0.6 * cm,
            backColor=colors.HexColor("#F1F5F9"),
            borderPadding=7,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=12,
            leftIndent=0.5 * cm,
            firstLineIndent=-0.5 * cm,
            spaceAfter=5,
        ),
    }


def build(summary_path: Path, output_path: Path) -> None:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    successful = [r for r in data["records"] if r["status"] == "ok"]
    if not successful:
        raise SystemExit("O resumo nao contem resultados validos.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2 * cm,
        title="Retificacao de perspectiva de um padrao plano com OpenCV",
        author="Bruno Sime Ferreira Nunes",
        subject="Trabalho T03 de Visao Computacional e Percepcao",
    )
    s = styles()
    story = []

    story.append(Paragraph("Retificação de perspectiva de um padrão plano com OpenCV", s["title"]))
    story.append(
        Paragraph(
            "Bruno Sime Ferreira Nunes - GRR20190568<br/>"
            "Universidade Federal do Paraná - Visão Computacional e Percepção - 2026",
            s["author"],
        )
    )
    story.append(
        Paragraph(
            "<b>Resumo.</b> Este artigo apresenta uma aplicação para transformar fotografias oblíquas "
            "de um padrão plano em vistas superiores retificadas. Foram reutilizadas as 30 imagens do "
            "tabuleiro de calibração produzidas no T02. O método detecta automaticamente os cantos "
            "internos, estima uma homografia e aplica a transformação perspectiva com OpenCV. A aplicação "
            f"retificou {data['images_successful']} de {data['images_total']} imagens e produziu saídas "
            "normalizadas de 1000 x 700 pixels.",
            s["abstract"],
        )
    )
    story.append(
        Paragraph(
            "<b>Palavras-chave:</b> homografia; transformação perspectiva; visão computacional; OpenCV; retificação.",
            s["abstract"],
        )
    )

    story.append(Paragraph("1. Introdução", s["heading"]))
    story.append(
        Paragraph(
            "Uma fotografia de uma superfície plana sofre deformações aparentes quando a câmera não está "
            "paralela ao plano. Linhas paralelas podem convergir, dimensões relativas mudam e regiões mais "
            "distantes parecem menores. A retificação perspectiva compensa esse efeito e produz uma vista "
            "frontal, semelhante ao resultado de um escaneamento ou de uma câmera posicionada acima da cena.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "O objetivo foi implementar uma aplicação simples e reprodutível em Python/OpenCV, reutilizando "
            "as imagens do T02. O tabuleiro é especialmente adequado porque fornece pontos coplanares de "
            "geometria conhecida e pode ser detectado automaticamente.",
            s["body"],
        )
    )

    story.append(Paragraph("2. Fundamentação", s["heading"]))
    story.append(
        Paragraph(
            "Pontos pertencentes a dois planos projetivos são relacionados por uma homografia, representada "
            "por uma matriz não singular H de dimensão 3 x 3. Em coordenadas homogêneas, a relação é:",
            s["body"],
        )
    )
    story.append(Paragraph("s [u  v  1]<super>T</super> = H [x  y  1]<super>T</super>", s["code"]))
    story.append(
        Paragraph(
            "Quatro correspondências de pontos, desde que não sejam colineares, determinam os oito graus de "
            "liberdade da homografia. Neste trabalho, as correspondências são os quatro cantos extremos da "
            "grade interna detectada. A função <font name='Courier'>getPerspectiveTransform</font> estima H, "
            "enquanto <font name='Courier'>warpPerspective</font> realiza o remapeamento dos pixels.",
            s["body"],
        )
    )

    story.append(Paragraph("3. Materiais e método", s["heading"]))
    story.append(
        Paragraph(
            "O conjunto contém 30 fotografias de 1920 x 1080 pixels de um tabuleiro com 9 x 6 cantos internos, "
            "equivalente a 10 x 7 quadrados. Antes da homografia, a distorção da lente foi corrigida com os "
            "parâmetros calculados no T02. A detecção utilizou <font name='Courier'>findChessboardCornersSB</font>, "
            "com uma alternativa baseada em <font name='Courier'>findChessboardCorners</font> e refinamento subpixel.",
            s["body"],
        )
    )
    steps = [
        ["Etapa", "Operação"],
        ["1", "Leitura e correção opcional da distorção da lente"],
        ["2", "Detecção dos 54 cantos internos do tabuleiro"],
        ["3", "Seleção dos quatro extremos: superior esquerdo, superior direito, inferior direito e inferior esquerdo"],
        ["4", "Associação com pontos de destino separados por uma margem de um quadrado"],
        ["5", "Estimação da homografia e geração da vista 1000 x 700 pixels"],
    ]
    table = Table(steps, colWidths=[1.25 * cm, 14.2 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))

    first = successful[0]
    comparison_path = Path(first["comparison"])
    if not comparison_path.is_absolute() and not comparison_path.exists():
        comparison_path = summary_path.parent.parent / comparison_path
    story.append(PageBreak())
    story.append(Paragraph("4. Resultados e discussão", s["heading"]))
    story.append(
        Paragraph(
            f"O padrão foi detectado em {data['images_successful']} das {data['images_total']} imagens "
            f"({100 * data['images_successful'] / data['images_total']:.1f}% de sucesso). Todas as vistas "
            "foram produzidas na mesma escala, o que facilita comparação, medição e uso posterior por outros "
            "algoritmos. A figura a seguir apresenta um exemplo representativo.",
            s["body"],
        )
    )
    story.append(fit_image(comparison_path, 16.9 * cm, 10.2 * cm))
    story.append(
        Paragraph(
            f"Figura 1 - Imagem {first['image']}: região detectada e vista superior após a transformação perspectiva.",
            s["caption"],
        )
    )
    story.append(
        Paragraph(
            "Na imagem retificada, os lados do tabuleiro tornam-se horizontais e verticais, e os quadrados "
            "ocupam dimensões aproximadamente uniformes. Pequenas diferenças locais podem permanecer por "
            "imperfeições físicas do papel, erro de calibração, desfoque e interpolação. O erro dos quatro "
            "pontos de controle é numericamente próximo de zero porque esses mesmos pontos determinam a homografia; "
            "portanto, a avaliação visual da regularidade dos demais cantos é mais informativa neste experimento.",
            s["body"],
        )
    )

    sample_rows = [["Imagem", "Entrada", "Saída", "RMSE controle"]]
    for record in successful[:5]:
        sample_rows.append(
            [
                record["image"],
                f"{record['input_size_px'][0]} x {record['input_size_px'][1]}",
                f"{record['output_size_px'][0]} x {record['output_size_px'][1]}",
                f"{record['control_point_rmse_px']:.6f} px",
            ]
        )
    result_table = Table(sample_rows, colWidths=[7.0 * cm, 3.1 * cm, 3.1 * cm, 3.2 * cm], repeatRows=1)
    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.8),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(result_table)
    story.append(Paragraph("Tabela 1 - Amostra dos resultados gerados pela aplicação.", s["caption"]))

    story.append(Paragraph("5. Conclusão", s["heading"]))
    story.append(
        Paragraph(
            "A aplicação demonstrou a transformação perspectiva de forma automática e reprodutível. A escolha "
            "do tabuleiro do T02 eliminou a necessidade de marcação manual e permitiu processar todo o conjunto. "
            "O mesmo princípio pode ser adaptado para documentos, pinturas, fachadas e vistas aéreas, substituindo "
            "a detecção do tabuleiro pela seleção manual ou automática dos quatro limites do plano de interesse.",
            s["body"],
        )
    )

    story.append(Paragraph("Código-fonte", s["heading"]))
    story.append(
        Paragraph(
            f'O código, as instruções e os resultados estão disponíveis em: <link href="{GIT_URL}" color="#0F4C81">{GIT_URL}</link>',
            s["body"],
        )
    )

    story.append(Paragraph("Referências", s["heading"]))
    story.append(
        Paragraph(
            "[1] BRADSKI, G.; KAEHLER, A. <i>Learning OpenCV: Computer Vision with the OpenCV Library.</i> O'Reilly Media, 2008.",
            s["reference"],
        )
    )
    story.append(
        Paragraph(
            "[2] HARTLEY, R.; ZISSERMAN, A. <i>Multiple View Geometry in Computer Vision.</i> 2. ed. Cambridge University Press, 2004.",
            s["reference"],
        )
    )
    story.append(
        Paragraph(
            "[3] OPENCV. Geometric Image Transformations. OpenCV Documentation. Disponível em: "
            '<link href="https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html" color="#0F4C81">docs.opencv.org</link>.',
            s["reference"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    args = parse_args()
    build(Path(args.summary), Path(args.output))
    print(f"Relatorio gerado: {args.output}")


if __name__ == "__main__":
    main()

