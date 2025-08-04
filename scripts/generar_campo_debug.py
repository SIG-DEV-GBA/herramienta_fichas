import sys
import os
import json
import logging
from datetime import datetime
from scripts.embedding_manager import buscar_chunks_relevantes
from scripts.generador_ficha import generar_campo_ficha, cargar_instrucciones, cargar_tipos_ayuda
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

DOC_ID = "documento_001"
EXPORT_DIR = "debug_exports"
FICHA_GENERADA_PATH = f"salidas/ficha_{DOC_ID}.json"
TOP_N = 20

os.makedirs(EXPORT_DIR, exist_ok=True)

def cargar_ficha_prev():
    if not os.path.exists(FICHA_GENERADA_PATH):
        return {}
    try:
        with open(FICHA_GENERADA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def debug_campo(campo: str):
    instrucciones = cargar_instrucciones("entradas/intrucciones.json")
    tipos_ayuda = cargar_tipos_ayuda("entradas/tipos_ayuda.json")
    ficha_prev = cargar_ficha_prev()

    print(f"\n🔎 Campo: {campo}\n{'=' * 40}")
    print("📥 Obteniendo chunks relevantes...\n")

    chunks = buscar_chunks_relevantes(campo.replace("_", " "), doc_id=DOC_ID, top_n=TOP_N)

    if not chunks:
        print("⚠️ No se encontraron chunks relevantes.")
        return

    prompt_chunks = "\n\n".join(chunks)
    instrucciones_campo = ""
    campo_normalizado = campo.lower().replace("_", " ")
    for clave, reglas in instrucciones.items():
        if campo_normalizado in clave.lower():
            instrucciones_campo = "\n".join(f"- {linea}" for linea in reglas)
            break

    lista_restringida = ""
    if campo == "tipo_ayuda" and tipos_ayuda:
        lista_restringida = (
            "\n\nIMPORTANTE: debes seleccionar uno o varios términos exactamente iguales a los siguientes. "
            "No los modifiques ni inventes. Esta es una lista cerrada:\n"
            + ", ".join(tipos_ayuda)
        )

    prompt = f"""
Eres un asistente legal encargado de rellenar un único campo de una ficha técnica de ayudas públicas, siguiendo la normativa oficial y las instrucciones del proyecto Fichas Miguel.

Tu tarea es rellenar el campo **{campo}** de forma literal, clara y precisa, exclusivamente en base al contenido del documento original.

### INSTRUCCIONES PARA ESTE CAMPO
Sigue todas estas reglas literalmente. No ignores ninguna. No inventes.

{instrucciones_campo}
{lista_restringida}

### FRAGMENTOS RELEVANTES DE LA NORMA
Usa exclusivamente los siguientes fragmentos para construir tu respuesta. Si no hay datos suficientes, devuelve exactamente: ""

[INICIO_TEXTO]
{prompt_chunks}
[FIN_TEXTO]

### REGLAS FINALES
- Devuelve solo el contenido final del campo "{campo}".
- No incluyas encabezados, comentarios ni explicaciones.
- No utilices bloques markdown como ```json.
- Si no hay suficiente información en los fragmentos, devuelve exactamente: ""
"""

    print("\n📡 Enviando prompt a GPT...\n")
    nueva_respuesta = generar_campo_ficha(campo, chunks, instrucciones, tipos_ayuda)

    print("\n🧠 RESPUESTA GPT:\n")
    print(nueva_respuesta.strip() if nueva_respuesta else "⚠️ Vacío")

    valor_prev = ficha_prev.get(campo, "")
    es_distinto = valor_prev.strip() != nueva_respuesta.strip()

    # Guardar informe
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(EXPORT_DIR, f"{campo}_{timestamp}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# 🧪 DEBUG CAMPO: {campo}\n\n")
        f.write("## 🔹 INSTRUCCIONES APLICADAS:\n")
        f.write(instrucciones_campo or "(no se definieron instrucciones)") 
        f.write("\n\n---\n\n")
        f.write("## 📄 FRAGMENTOS USADOS (top 20):\n\n")
        for i, ch in enumerate(chunks):
            f.write(f"### Fragmento {i+1}\n{ch}\n\n")
        f.write("---\n\n")
        f.write("## 💬 PROMPT ENVIADO:\n\n")
        f.write(prompt.strip())
        f.write("\n\n---\n\n")
        f.write("## ✅ RESPUESTA DEL MODELO:\n\n")
        f.write(nueva_respuesta.strip() if nueva_respuesta else "⚠️ Vacío")
        f.write("\n\n---\n\n")
        f.write("## 🧾 COMPARACIÓN CON FICHA EXISTENTE:\n\n")
        if valor_prev:
            f.write(f"📄 Valor previo:\n{valor_prev.strip()}\n\n")
            if es_distinto:
                f.write("🔁 Resultado: ❗️DIFERENTE al generado ahora.\n")
            else:
                f.write("✅ Resultado: Sin cambios.\n")
        else:
            f.write("🟡 No hay valor previo en la ficha existente.\n")

    print(f"\n📝 Exportado a: {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generar_campo_debug.py <nombre_campo>")
        sys.exit(1)

    campo = sys.argv[1]
    debug_campo(campo)
