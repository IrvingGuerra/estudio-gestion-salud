"""Convierte guia.md (exportada del Claude Doc) en guia.html para leer en el celular."""
import html
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().splitlines()

CICLO = """
<figure class="ciclo" aria-label="Los 14 temas forman un solo ciclo de gestión">
  <figcaption>Los 14 temas forman un solo ciclo de gestión</figcaption>
  <ol class="pasos">
    <li><span class="paso-nombre">1. Planificar</span><span class="paso-temas">Temas 1 y 4</span><span class="paso-que">Análisis externo e interno, DAFO y estrategia</span></li>
    <li><span class="paso-nombre">2. Organizar</span><span class="paso-temas">Temas 2, 3 y 5</span><span class="paso-que">Procesos, unidades de gestión clínica y guías (MBE)</span></li>
    <li><span class="paso-nombre">3. Pactar objetivos</span><span class="paso-temas">Temas 1 y 13</span><span class="paso-que">Acuerdo de gestión anual con objetivos SMART</span></li>
    <li><span class="paso-nombre">4. Evaluar</span><span class="paso-temas">Temas 6 y 13</span><span class="paso-que">Indicadores, desempeño y evaluación de resultados</span></li>
    <li><span class="paso-nombre">5. Mejorar</span><span class="paso-temas">Temas 11 y 14</span><span class="paso-que">PDCA, equipos de mejora y plan de calidad</span></li>
  </ol>
  <p class="vuelta">↻ y el ciclo vuelve a empezar</p>
  <div class="marcos">
    <div><b>Se aplica en</b><span>Tema 8 · Área integrada AP-AE</span><span>Tema 9 · Hospital de día</span><span>Tema 10 · Salud mental</span></div>
    <div><b>Lo enmarcan</b><span>Tema 4 · Gobierno y COCASEP</span><span>Tema 7 · Investigación traslacional</span><span>Tema 12 · Responsabilidad social</span></div>
  </div>
</figure>
"""

QUIZ_CALLOUT = """
<aside class="callout" id="preguntas">
  <h2>Preguntas de práctica</h2>
  <p>Las 43 preguntas de opción múltiple están en el quiz: te dice al momento si acertaste y por qué, y guarda las que falles para repasarlas.</p>
  <p><a class="btn" href="quiz.html">Hacer el quiz →</a></p>
</aside>
"""


def inline(s):
    # Escapes de markdown (\~ \_ \]) → marcador, luego HTML seguro, luego énfasis
    s = re.sub(r"\\([\\`*_{}\[\]()#+\-.!~|>])", lambda m: "\x00%d\x00" % ord(m.group(1)), s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: html.escape(chr(int(m.group(1))), quote=False), s)
    return s


IDS = {
    "Cómo usar esta guía": "como-usar",
    "Resumen por tema": "resumen",
    "Glosario": "glosario",
    "Repaso de último minuto": "repaso",
}

out = []
para = []
list_kind = None
skipping = False


def flush_para():
    global para
    if para:
        out.append("<p>%s</p>" % inline(" ".join(para)))
        para = []


def close_list():
    global list_kind
    if list_kind:
        out.append("</%s>" % list_kind)
        list_kind = None


for i, raw in enumerate(lines):
    line = raw.rstrip()
    if i < 4 and (line.startswith("# ") or "@Irving" in line):
        continue  # el título y la línea de autor van en la cabecera propia
    if line.startswith("## Preguntas de práctica"):
        flush_para(); close_list()
        out.append(QUIZ_CALLOUT)
        skipping = True
        continue
    if skipping:
        if line.startswith("## Repaso"):
            skipping = False
        else:
            continue
    if "embedded content" in line:
        flush_para(); close_list()
        out.append(CICLO)
        continue
    if not line.strip():
        flush_para(); close_list()
        continue
    m = re.match(r"^(#{2,3}) (.*)$", line)
    if m:
        flush_para(); close_list()
        level = len(m.group(1))
        text = m.group(2)
        tm = re.match(r"Tema (\d+)\.", text)
        hid = "tema-%s" % tm.group(1) if tm else IDS.get(text, "")
        out.append('<h%d%s>%s</h%d>' % (level, ' id="%s"' % hid if hid else "", inline(text), level))
        continue
    m = re.match(r"^(\d+)\. (.*)$", line)
    if m:
        flush_para()
        if list_kind != "ol":
            close_list()
            start = int(m.group(1))
            out.append('<ol%s>' % (' start="%d"' % start if start != 1 else ""))
            list_kind = "ol"
        out.append("<li>%s</li>" % inline(m.group(2)))
        continue
    m = re.match(r"^[-*] (.*)$", line)
    if m:
        flush_para()
        if list_kind != "ul":
            close_list()
            out.append("<ul>")
            list_kind = "ul"
        out.append("<li>%s</li>" % inline(m.group(1)))
        continue
    close_list()
    para.append(line.strip())

flush_para(); close_list()
body = "\n".join(out)

# Ajustes para la web: las preguntas viven en el quiz
body = body.replace(
    "Resuelve las 43 preguntas sin ver las respuestas y regresa a los temas donde falles.",
    'Practica con el <a href="quiz.html">quiz de 43 preguntas</a> y regresa a los temas donde falles.',
)
body = body.replace("Mira el diagrama:", "Mira el ciclo de abajo:")

chips = ['<a class="chip" href="#como-usar">Inicio</a>']
chips += ['<a class="chip" href="#tema-%d">T%d</a>' % (n, n) for n in range(1, 15)]
chips += ['<a class="chip" href="#glosario">Glosario</a>', '<a class="chip" href="#repaso">Repaso</a>', '<a class="chip chip-quiz" href="quiz.html">Quiz</a>']

page = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#2e4ca8">
<title>Guía de Gestión en Salud</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="estilos.css">
<style>
html { scroll-behavior: smooth; }
.temas-nav {
  position: sticky;
  top: 0;
  z-index: 5;
  background: var(--bg);
  border-bottom: 1px solid var(--line);
  padding-top: env(safe-area-inset-top, 0px);
}
.temas-nav .fila {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 10px 16px;
  max-width: 44rem;
  margin: 0 auto;
  scrollbar-width: none;
}
.temas-nav .fila::-webkit-scrollbar { display: none; }
.chip {
  flex: none;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  text-decoration: none;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 99px;
  padding: 5px 11px;
}
.chip-quiz { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
.ciclo {
  margin: 1.4rem 0;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px;
}
.ciclo figcaption { font-family: var(--font-display); font-weight: 700; font-size: 1.1rem; margin-bottom: 12px; }
.pasos { list-style: none; padding: 0; margin: 0; display: grid; gap: 18px; position: relative; }
.pasos li {
  margin: 0;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2px 10px;
  border: 1.25px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  position: relative;
}
.pasos li + li::before {
  content: "↓";
  position: absolute;
  top: -19px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--muted);
  font-size: 0.85rem;
  line-height: 1;
}
.paso-nombre { font-weight: 700; }
.paso-temas { font-family: var(--font-mono); font-size: 0.75rem; color: var(--muted); align-self: center; }
.paso-que { grid-column: 1 / -1; font-size: 0.93rem; color: var(--muted); }
.vuelta { margin: 12px 0 0; font-weight: 700; color: var(--accent); }
.marcos { display: grid; gap: 10px; margin-top: 14px; }
.marcos div { background: var(--accent-soft); border-radius: 8px; padding: 10px 12px; display: grid; gap: 2px; font-size: 0.93rem; }
.callout {
  margin-top: 2.4rem;
  background: var(--accent-soft);
  border-radius: 12px;
  padding: 4px 18px 10px;
}
.callout h2 { border: 0; margin-top: 0.8rem; padding-top: 0; }
.btn {
  display: inline-block;
  font-weight: 700;
  text-decoration: none;
  background: var(--accent);
  color: var(--on-accent);
  border-radius: 8px;
  padding: 10px 18px;
}
@media (min-width: 640px) {
  .marcos { grid-template-columns: 1fr 1fr; }
}
</style>
</head>
<body>
<nav class="temas-nav" aria-label="Ir a un tema"><div class="fila">{{CHIPS}}</div></nav>
<main class="wrap">
  <a class="backlink" href="index.html">← Inicio</a>
  <p class="eyebrow">Gestión en Salud · UNIR · 14 temas</p>
  <h1>Guía de estudio</h1>
{{BODY}}
  <p class="foot">Resumen personal de estudio hecho a partir del material de la asignatura Gestión en Salud (UNIR). No incluye ni sustituye el material original del curso. <a href="guia-gestion-salud.pdf">PDF para imprimir</a> · <a href="quiz.html">Quiz</a></p>
</main>
</body>
</html>
""".replace("{{CHIPS}}", "".join(chips)).replace("{{BODY}}", body)

open(dst, "w", encoding="utf-8").write(page)
print("ok", len(page), "caracteres")
