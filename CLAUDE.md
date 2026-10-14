# Estudio de Gestión en Salud

Sitio estático de estudio de Irving para la asignatura **Gestión en Salud** (Maestría en Dirección y
Administración en Salud, UNIR; examen de octubre de 2026). Repo público con GitHub Pages:
https://irvingguerra.github.io/estudio-gestion-salud/

## Archivos

- `index.html` — portada (enlaces a guía, quiz, repaso, glosario y PDF). Usa `estilos.css`.
- `guia.md` — texto fuente de la guía, exportado del Claude Doc
  https://claude.ai/code/artifact/255ab1b8-c5bf-469d-9ac2-aa300ea33425
- `guia.html` — **generado**, no editar a mano: `python3 herramientas/construir_guia.py guia.md guia.html`.
  El script omite la sección de preguntas (viven en el quiz) y cambia el diagrama del doc por un ciclo en HTML.
- `quiz.html` — autocontenido; las 43 preguntas están en el arreglo `PREGUNTAS` (n, tema, opciones,
  índice correcto, explicación). Las falladas se guardan en `localStorage` (`quiz-gestion-salud-falladas`).
  Es la misma página que el artifact https://claude.ai/artifact/HuZUMu4GaPFcfYcwcNDFak, más el `<head>`,
  la navegación y los enlaces a la guía.
- `guia-gestion-salud.pdf` — exportación del doc en tamaño carta (29 hojas).

## Publicar

No hay build: `git push` a `main` y GitHub Pages sirve la raíz. Probar antes en vista de celular (375 px):
sin scroll horizontal y con 16 px de margen lateral.

Todo en español. Es un resumen personal: nunca subir el PDF original de UNIR.
