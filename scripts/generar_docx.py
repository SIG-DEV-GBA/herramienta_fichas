import os
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def formatear_titulo(document: Document, texto: str):
    p = document.add_paragraph()
    run = p.add_run(texto.upper())
    run.bold = True
    run.font.size = Pt(11)
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

def formatear_contenido(document: Document, texto: str):
    p = document.add_paragraph(texto.strip())
    p.paragraph_format.space_after = Pt(6)

def formatear_lista(document: Document, items: list):
    for item in items:
        if isinstance(item, dict):
            texto = " · ".join(f"{k}: {v}" for k, v in item.items() if v)
            document.add_paragraph(texto, style='List Bullet')
        else:
            document.add_paragraph(str(item), style='List Bullet')

def formatear_cuantia_especial(document: Document, cuantias: list):
    for item in cuantias:
        concepto = item.get("concepto", "").strip()
        valor = item.get("valor", "").strip()
        unidad = item.get("unidad", "").strip()

        if concepto and valor:
            puntos = '.' * max(5, 60 - len(concepto))  # Ajuste dinámico
            texto = f"{concepto} {puntos} {valor} {unidad}"
            document.add_paragraph(texto, style='List Bullet')

def generar_docx_desde_json(json_path: str, output_dir: str = "salidas_docx"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nombre_base = os.path.splitext(os.path.basename(json_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{nombre_base}.docx")

    # 🧹 Intentar eliminar archivo anterior si existe
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError:
            print(f"❌ No se puede sobrescribir {output_path}. Asegúrate de cerrar el archivo en Word.")
            return

    doc = Document()
    doc.add_heading("FICHA DE AYUDA UNIFICADA", level=1)

    for clave, valor in data.items():
        if valor in [None, "", [], "- "]:
            continue  # omitir campos vacíos

        formatear_titulo(doc, clave)

        if clave == "cuantia" and isinstance(valor, list):
            formatear_cuantia_especial(doc, valor)

        elif isinstance(valor, str):
            formatear_contenido(doc, valor)

        elif isinstance(valor, list):
            if all(isinstance(v, str) for v in valor) or all(isinstance(v, dict) for v in valor):
                formatear_lista(doc, valor)

        elif isinstance(valor, dict):  # Por ejemplo: lugares_presentacion
            for subclave, subvalores in valor.items():
                formatear_titulo(doc, f"{clave} - {subclave}")
                formatear_lista(doc, subvalores)

    doc.save(output_path)
    print(f"📄 Documento Word generado en: {output_path}")
