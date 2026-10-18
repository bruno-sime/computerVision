library(ggplot2)
library(class)

dir.create("figuras", showWarnings = FALSE)

dados <- iris
names(dados) <- c("Comprimento_sepala", "Largura_sepala",
                  "Comprimento_petala", "Largura_petala", "Categoria")

cores <- c(setosa = "#0072B2", versicolor = "#E69F00", virginica = "#009E73")
tema <- theme_minimal(base_size = 12) +
  theme(legend.position = "bottom", panel.grid.minor = element_blank(),
        plot.margin = margin(8, 8, 8, 8))

p_sepala <- ggplot(dados, aes(Comprimento_sepala, Largura_sepala,
                              color = Categoria)) +
  geom_point(size = 2.4, alpha = 0.82) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.8) +
  scale_color_manual(values = cores) + tema +
  labs(x = "Comprimento da sépala (cm)", y = "Largura da sépala (cm)",
       color = "Categoria")
ggsave("figuras/sepala.pdf", p_sepala, width = 7.2, height = 5.0,
       device = cairo_pdf)

p_petala <- ggplot(dados, aes(Comprimento_petala, Largura_petala,
                              color = Categoria)) +
  geom_point(size = 2.4, alpha = 0.82) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.8) +
  scale_color_manual(values = cores) + tema +
  labs(x = "Comprimento da pétala (cm)", y = "Largura da pétala (cm)",
       color = "Categoria")
ggsave("figuras/petala.pdf", p_petala, width = 7.2, height = 5.0,
       device = cairo_pdf)

pdf("figuras/pares.pdf", width = 7.4, height = 7.0, family = "Helvetica")
par(mar = c(3, 3, 2, 1), oma = c(0, 0, 1, 0))
nomes <- c("Comp. sépala", "Larg. sépala", "Comp. pétala", "Larg. pétala")
col_pts <- unname(cores[as.character(dados$Categoria)])
pairs(dados[, 1:4], labels = nomes, col = adjustcolor(col_pts, alpha.f = 0.72),
      pch = 19, cex = 0.65, main = "Distribuição conjunta das quatro medidas")
legend("topright", legend = levels(dados$Categoria), col = cores,
       pch = 19, bty = "n", cex = 0.85)
dev.off()

pca <- prcomp(dados[, 1:4], center = TRUE, scale. = TRUE)
var_exp <- 100 * pca$sdev^2 / sum(pca$sdev^2)
pca_df <- data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2],
                     Categoria = dados$Categoria)
p_pca <- ggplot(pca_df, aes(PC1, PC2, color = Categoria)) +
  geom_point(size = 2.5, alpha = 0.82) +
  stat_ellipse(linewidth = 0.7, level = 0.90) +
  scale_color_manual(values = cores) + tema +
  labs(x = sprintf("PC1 (%.1f%%)", var_exp[1]),
       y = sprintf("PC2 (%.1f%%)", var_exp[2]), color = "Categoria")
ggsave("figuras/pca.pdf", p_pca, width = 7.2, height = 5.0,
       device = cairo_pdf)

set.seed(42)
idx_treino <- unlist(lapply(levels(dados$Categoria), function(cat) {
  idx <- which(dados$Categoria == cat)
  sample(idx, 0.8 * length(idx))
}))
treino <- dados[idx_treino, ]
set.seed(42)
fold_id <- integer(nrow(treino))
for (cat in levels(treino$Categoria)) {
  idx <- which(treino$Categoria == cat)
  fold_id[idx] <- sample(rep(1:5, length.out = length(idx)))
}
ks <- seq(1, 15, 2)
acc_cv <- sapply(ks, function(k) {
  acertos <- unlist(lapply(1:5, function(f) {
    tr <- treino[fold_id != f, ]
    va <- treino[fold_id == f, ]
    mu <- sapply(tr[, 1:4], mean)
    sig <- sapply(tr[, 1:4], sd)
    pred <- knn(scale(tr[, 1:4], mu, sig), scale(va[, 1:4], mu, sig),
                cl = tr$Categoria, k = k)
    pred == va$Categoria
  }))
  mean(acertos)
})
cv <- data.frame(k = ks, Acuracia = acc_cv)
p_cv <- ggplot(cv, aes(k, Acuracia)) +
  geom_line(color = "#0072B2", linewidth = 0.8) +
  geom_point(color = "#0072B2", size = 2.5) +
  scale_x_continuous(breaks = ks) +
  scale_y_continuous(limits = c(0.90, 1.00), labels = function(x) paste0(100*x, "%")) +
  tema + labs(x = "Número de vizinhos (k)", y = "Acurácia na validação cruzada")
ggsave("figuras/knn_cv.pdf", p_cv, width = 7.2, height = 4.4,
       device = cairo_pdf)
