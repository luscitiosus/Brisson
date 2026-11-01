# Brisson

Conector MCP del léxico jurídico latino de **Brisson, *De verborum quae ad ius pertinent significatione*, ed. Heineccio (Halle 1743; VD18 10747656)**, dominio público. Pensado para estudiar el derecho romano desde la historia conceptual: separa lo que es de Brisson de lo que termina en nota de Heineccio.

## Herramientas
- `brisson(palabra, capa, parte, max_caracteres)`: entrada completa, citas sin recortar. `capa`: ambas | brisson | heineccio | corchetes. u/v e i/j indiferentes; admite formas flexionadas simples.
- `brisson_texto(consulta)`: busca dentro del texto de todas las entradas.
- `brisson_pagina(pagina)`: enlace a la imagen de la página en Halle (URN con dígito de control calculado).
- `ligaturas_griegas()`: lámina de ligaturas del griego impreso, para leer capturas del libro.

## Capas y límites
- «[Tramo que termina en HEIN.]»: texto que cierra con la firma de Heineccio (puede incluir texto de Brisson anterior a su nota hasta que se integren las manecillas ☞). «[Brisson]»: resto. «[Entre corchetes en la edición]»: entradas entre corchetes.
- Las citas (D., C.) se han convertido a numeración moderna entre [corchetes] en ~70 %; el resto queda como en el original. Los números pueden tener errores de OCR: contrástalos con el conector de fuentes romanas.
- El griego del OCR es ilegible: aparece como `⟦griego⟧` (el original se conserva en el campo `gr` de `brisson.json`). Pide a Claude que lea una captura de la línea.
- Texto de OCR de la edición digital de Halle: comprobar la licencia antes de redistribuir.

## Despliegue en Render (como Romanorum)
1. Sube esta carpeta a un repositorio de GitHub.
2. En [render.com](https://render.com): «New → Blueprint» y elige el repositorio. `render.yaml` crea el servicio y genera `MCP_SECRET`.
3. Cuando termine, copia `MCP_SECRET` (pestaña Environment). URL del conector: `https://<servicio>.onrender.com/<MCP_SECRET>/mcp`.
4. En claude.ai: Ajustes → Conectores → Añadir conector personalizado, pega la URL. Después estará en el móvil.

El plan gratuito de Render se duerme tras unos minutos sin uso; la primera consulta tarda en responder.

Local: `pip install "mcp[cli]>=1.12,<2"` y `python server.py --stdio`.

## Reconstruir datos
Scripts de la raíz: `build_data.py` (partir entradas por «HEIN.»), `griego_detector.py` y `apply_greek.py` (marcado del griego), `manecillas.py` (detector de ☞/☜; requiere poppler, opencv y el PDF).
