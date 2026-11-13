# =============================================================================
# tema.R — Tema visual e exportação das figuras (artigo, PDF e slides)
# =============================================================================
# Cada figura é descrita por uma FUNÇÃO que monta o ggplot. A função salvar()
# chama essa função uma vez por dispositivo, porque o texto muda de forma
# conforme o destino:
#   - .tex  (tikzDevice): o LaTeX do artigo compõe todo o texto da figura com a
#           fonte do acmart (Linux Libertine + newtxmath). Entra no main.tex com
#           \input{figures/<nome>.tex}.
#   - .pdf  : o mesmo .tex compilado de forma avulsa (pdflatex), para quem
#           preferir \includegraphics.
#   - .png  : ragg a 300 dpi, mesma fonte Libertine (pré-visualização).
#   - slide : ragg com fonte sem serifa e corpo maior, para os slides Marp.
# Use tx("$\\Delta t$", "Δt") e esc() nos textos para que funcionem nos dois
# modos (LaTeX e texto puro).
# =============================================================================

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
})

# Largura do texto do acmsmall (\the\textwidth = 395.8225pt).
TEXTW_IN <- 395.8225 / 72.27

LABEL <- c(kyber512 = "Kyber-512", `ctru-light` = "CTRU-Light", ecdh = "ECDH")
PAL <- c(`Kyber-512` = "#0072B2", `CTRU-Light` = "#D55E00", ECDH = "#009E73")

# ---- Fontes -----------------------------------------------------------------
.kpse <- function(arquivo) {
  out <- tryCatch(
    suppressWarnings(system2("kpsewhich", arquivo, stdout = TRUE, stderr = FALSE)),
    error = function(e) character()
  )
  out <- out[nzchar(out) & file.exists(out)]
  if (length(out)) out[[1]] else NA_character_
}

registrar_fontes <- function() {
  arquivos <- c(plain = "LinLibertine_R.otf", bold = "LinLibertine_RB.otf",
                italic = "LinLibertine_RI.otf", bolditalic = "LinLibertine_RBI.otf")
  caminhos <- vapply(arquivos, .kpse, character(1))
  fonte_texto <- "serif"
  if (!anyNA(caminhos)) {
    systemfonts::register_font(
      name = "Libertine Artigo", plain = caminhos[["plain"]], bold = caminhos[["bold"]],
      italic = caminhos[["italic"]], bolditalic = caminhos[["bolditalic"]]
    )
    fonte_texto <- "Libertine Artigo"
  } else {
    warning("Linux Libertine não encontrada via kpsewhich; PNGs usarão 'serif'.")
  }
  familias <- unique(systemfonts::system_fonts()$family)
  fonte_slide <- c("Inter", "Arial", "Liberation Sans", "DejaVu Sans")
  fonte_slide <- c(fonte_slide[fonte_slide %in% familias], "sans")[[1]]
  options(cmp223.fonte_texto = fonte_texto, cmp223.fonte_slide = fonte_slide)
  ggplot2::update_geom_defaults("text", list(family = fonte_texto))
  invisible(c(texto = fonte_texto, slide = fonte_slide))
}

# ---- tikzDevice com o mesmo preâmbulo de fontes do acmart ---------------------
configurar_tikz <- function(cache_dir) {
  dir.create(cache_dir, recursive = TRUE, showWarnings = FALSE)
  options(
    tikzDefaultEngine = "pdftex",
    tikzDocumentDeclaration = "\\documentclass[10pt]{article}",
    tikzLatexPackages = c(
      "\\usepackage[T1]{fontenc}",
      "\\usepackage[utf8]{inputenc}",
      "\\usepackage[tt=false]{libertine}",
      "\\usepackage[libertine]{newtxmath}",
      "\\usepackage{tikz}",
      "\\usepackage[active,tightpage,psfixbb]{preview}",
      "\\PreviewEnvironment{pgfpicture}",
      "\\setlength\\PreviewBorder{0pt}"
    ),
    tikzMetricsDictionary = file.path(cache_dir, "tikz-metricas"),
    tikzSanitizeCharacters = character(),
    tikzReplacementCharacters = character()
  )
}

# ---- Modo de texto: LaTeX (tikz) ou texto puro (png) ---------------------------
.modo <- new.env()
.modo$tikz <- FALSE
.modo$corpo <- 8
modo_tikz <- function() isTRUE(.modo$tikz)

# Tamanho de texto de geom_text()/annotate() como fração do corpo do tema, em
# mm (unidade do ggplot). Acompanha o corpo maior da versão de slide.
fs <- function(fracao = 0.8) fracao * .modo$corpo / ggplot2::.pt

# Escolhe a forma LaTeX ou a forma em texto puro do mesmo rótulo.
tx <- function(latex, texto) if (modo_tikz()) latex else texto

# Escapa caracteres especiais do LaTeX em textos vindos dos dados.
esc <- function(x) {
  if (!modo_tikz()) return(x)
  x <- gsub("\\\\", "\\\\textbackslash{}", x)
  gsub("([%#&_$])", "\\\\\\1", x)
}

# Número no padrão brasileiro (1.234,5).
br <- function(x, nd = 1) {
  formatC(x, format = "f", digits = nd, big.mark = ".", decimal.mark = ",")
}
rotulo_br <- function(nd = 0, sufixo = "") {
  function(x) ifelse(is.na(x), NA, paste0(br(x, nd), sufixo))
}

# ---- Tema ----------------------------------------------------------------------
theme_artigo <- function(base_size = 8, base_family = "") {
  linha <- base_size / 32
  theme_bw(base_size = base_size, base_family = base_family) +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(linewidth = linha, colour = "grey90"),
      panel.border = element_rect(linewidth = linha * 1.6, colour = "grey30"),
      axis.ticks = element_line(linewidth = linha * 1.4, colour = "grey30"),
      axis.text = element_text(colour = "grey15"),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", hjust = 0, margin = margin(1, 0, 2, 0)),
      panel.spacing.x = unit(base_size * 0.9, "pt"),
      legend.position = "top",
      legend.title = element_blank(),
      legend.margin = margin(0, 5, 0, 5),
      legend.spacing.x = unit(base_size * 0.8, "pt"),
      legend.box.spacing = unit(base_size * 0.3, "pt"),
      legend.key.size = unit(base_size * 1.1, "pt"),
      legend.background = element_blank(),
      plot.title = element_text(face = "bold", size = rel(1.05)),
      plot.title.position = "plot",
      plot.margin = margin(2, 4, 2, 2)
    )
}

.aplicar <- function(p, t) if (inherits(p, "patchwork")) p & t else p + t

# Escreve a figura em todos os destinos.
#   fazer        função sem argumentos que devolve o ggplot/patchwork
#   nome         nome base dos arquivos (sem extensão)
#   larg, alt    tamanho no artigo, em polegadas
#   ajuste       theme() aplicado depois do tema base (posição de legenda etc.)
#   slide        nome do PNG em slides/figures/ (NULL = sem versão de slide)
#   slide_larg, slide_alt, slide_corpo   tamanho e corpo da versão de slide
#   tikz         FALSE para figuras sem versão LaTeX (só PNG/PDF via ragg/cairo)
salvar <- function(fazer, nome, larg = TEXTW_IN, alt = 2.5, ajuste = theme(),
                   slide = NULL, slide_larg = 10, slide_alt = 5, slide_corpo = 15,
                   tikz = TRUE, dirs = DIRS) {
  fonte_texto <- getOption("cmp223.fonte_texto", "serif")
  fonte_slide <- getOption("cmp223.fonte_slide", "sans")
  base <- file.path(dirs$fig, nome)

  # Monta e desenha no dispositivo já aberto. O modo fica ligado durante o
  # print() porque os rótulos de escala só são calculados na hora de desenhar.
  desenhar <- function(tikz_mode, corpo, familia) {
    .modo$tikz <- tikz_mode
    .modo$corpo <- corpo
    ggplot2::update_geom_defaults("text", list(family = familia))
    on.exit({
      grDevices::dev.off()
      ggplot2::update_geom_defaults("text", list(family = fonte_texto))
      .modo$tikz <- FALSE
      .modo$corpo <- 8
    })
    print(.aplicar(fazer(), theme_artigo(corpo, familia) + ajuste))
  }

  if (tikz) {
    tikzDevice::tikz(paste0(base, ".tex"), width = larg, height = alt,
                     standAlone = FALSE, sanitize = FALSE)
    desenhar(TRUE, 8, "")
    .compilar_pdf(desenhar, base, larg, alt, dirs$tmp)
  } else {
    grDevices::cairo_pdf(paste0(base, ".pdf"), width = larg, height = alt,
                         family = fonte_texto)
    desenhar(FALSE, 8, fonte_texto)
  }

  ragg::agg_png(paste0(base, ".png"), width = larg, height = alt, units = "in", res = 300)
  desenhar(FALSE, 8, fonte_texto)

  if (!is.null(slide)) {
    ragg::agg_png(file.path(dirs$slide, slide), width = slide_larg, height = slide_alt,
                  units = "in", res = 200)
    desenhar(FALSE, slide_corpo, fonte_slide)
  }
  art_fig <- file.path(dirs$root, "artigo", "figures")
  if (dir.exists(art_fig)) {
    exts <- if (tikz) c(".tex", ".pdf", ".png") else c(".pdf", ".png")
    file.copy(paste0(base, exts), art_fig, overwrite = TRUE)
  }
  invisible(paste0(base, ".png"))
}

# Versão de slide de um gráfico, devolvida como objeto (para compor com outros).
versao_slide <- function(fazer, corpo = 15, ajuste = theme()) {
  familia <- getOption("cmp223.fonte_slide", "sans")
  .modo$corpo <- corpo
  ggplot2::update_geom_defaults("text", list(family = familia))
  on.exit({
    ggplot2::update_geom_defaults("text", list(family = ""))
    .modo$corpo <- 8
  })
  .aplicar(fazer(), theme_artigo(corpo, familia) + ajuste)
}

# Compila a versão avulsa (standAlone) do mesmo gráfico em PDF.
.compilar_pdf <- function(desenhar, base, larg, alt, tmp) {
  dir.create(tmp, recursive = TRUE, showWarnings = FALSE)
  nome <- basename(base)
  tex <- file.path(tmp, paste0(nome, ".tex"))
  tikzDevice::tikz(tex, width = larg, height = alt, standAlone = TRUE, sanitize = FALSE)
  desenhar(TRUE, 8, "")
  status <- withr_dir(tmp, system2(
    "pdflatex", c("-interaction=nonstopmode", "-halt-on-error", shQuote(basename(tex))),
    stdout = FALSE, stderr = FALSE
  ))
  pdf <- file.path(tmp, paste0(nome, ".pdf"))
  if (status != 0 || !file.exists(pdf)) {
    stop("pdflatex falhou ao compilar ", tex, " (veja o .log em ", tmp, ")")
  }
  file.copy(pdf, paste0(base, ".pdf"), overwrite = TRUE)
}

withr_dir <- function(dir, expr) {
  old <- setwd(dir)
  on.exit(setwd(old))
  force(expr)
}
