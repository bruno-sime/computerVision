# Retificação de perspectiva de um padrão plano com OpenCV

**Bruno Sime Ferreira Nunes - GRR20190568**  
Universidade Federal do Paraná - Visão Computacional e Percepção - 2026

## Resumo

Este trabalho apresenta uma aplicação para transformar fotografias oblíquas de um padrão plano em vistas superiores retificadas. Foram reutilizadas as 30 imagens do tabuleiro de calibração produzidas no T02. O método detecta automaticamente os cantos internos, estima uma homografia e aplica a transformação perspectiva com OpenCV. A aplicação processa o conjunto de forma automática e produz saídas normalizadas de 1000 x 700 pixels.

**Palavras-chave:** homografia; transformação perspectiva; visão computacional; OpenCV; retificação.

## 1. Introdução

Uma fotografia de uma superfície plana sofre deformações aparentes quando a câmera não está paralela ao plano. Linhas paralelas podem convergir, dimensões relativas mudam e regiões mais distantes parecem menores. A retificação perspectiva compensa esse efeito e produz uma vista frontal, semelhante ao resultado de um escaneamento ou de uma câmera posicionada acima da cena.

O objetivo foi implementar uma aplicação simples e reprodutível em Python/OpenCV, reutilizando as imagens do T02. O tabuleiro é adequado porque fornece pontos coplanares de geometria conhecida e pode ser detectado automaticamente.

## 2. Fundamentação

Pontos pertencentes a dois planos projetivos são relacionados por uma homografia, representada por uma matriz não singular H de dimensão 3 x 3. Em coordenadas homogêneas:

```text
s [u v 1]^T = H [x y 1]^T
```

Quatro correspondências de pontos não colineares determinam os oito graus de liberdade da homografia. Neste trabalho, as correspondências são os quatro cantos extremos da grade interna detectada. `cv2.getPerspectiveTransform` estima H e `cv2.warpPerspective` realiza o remapeamento dos pixels.

## 3. Materiais e método

O conjunto contém 30 fotografias de 1920 x 1080 pixels de um tabuleiro com 9 x 6 cantos internos, equivalente a 10 x 7 quadrados. Antes da homografia, a distorção da lente é corrigida com os parâmetros calculados no T02. A detecção utiliza `findChessboardCornersSB`, com alternativa baseada em `findChessboardCorners` e refinamento subpixel.

O processamento executa cinco etapas:

1. leitura da imagem e correção opcional da distorção da lente;
2. detecção dos 54 cantos internos;
3. seleção dos quatro cantos extremos;
4. associação com pontos de destino separados por uma margem de um quadrado;
5. estimação da homografia e geração da vista de 1000 x 700 pixels.

## 4. Resultados e discussão

As saídas ficam em `results/annotated`, `results/rectified` e `results/comparisons`. O arquivo `results/summary.json` registra a homografia e os pontos usados em cada imagem.

Nas imagens retificadas, os lados do tabuleiro tornam-se horizontais e verticais, e os quadrados ocupam dimensões aproximadamente uniformes. Pequenas diferenças locais podem permanecer por imperfeições físicas do papel, erro de calibração, desfoque e interpolação.

## 5. Conclusão

A aplicação demonstra a transformação perspectiva de forma automática e reprodutível. O tabuleiro do T02 elimina a necessidade de marcação manual. O mesmo princípio pode ser adaptado para documentos, pinturas, fachadas e vistas aéreas, substituindo a detecção do tabuleiro pela seleção manual ou automática dos quatro limites do plano.

## Código-fonte

<https://github.com/bruno-sime/computerVision/tree/main/T03>

## Referências

1. BRADSKI, G.; KAEHLER, A. *Learning OpenCV: Computer Vision with the OpenCV Library.* O'Reilly Media, 2008.
2. HARTLEY, R.; ZISSERMAN, A. *Multiple View Geometry in Computer Vision.* 2. ed. Cambridge University Press, 2004.
3. OpenCV. *Geometric Image Transformations.* <https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html>.
