import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from scripts.chunker import dividir_en_chunks
from scripts.extractor_texto import extraer_texto, extraer_textos_unificados

# Inicialización
load_dotenv()
client = OpenAI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_plantilla_json():
    with open(os.path.join(BASE_DIR, "..", "entradas", "plantilla.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_instrucciones_texto():
    with open(os.path.join(BASE_DIR, "..", "entradas", "instrucciones.json"), "r", encoding="utf-8") as f:
        return f.read()

def cargar_lista_tipo_ayuda():
    with open(os.path.join(BASE_DIR, "..", "entradas", "tipos_ayuda.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
        return "\n- " + "\n- ".join(data.get("tipos_de_ayuda", []))

def guardar_json_generado(contenido_json: str, nombre_base: str):
    carpeta = os.path.join(BASE_DIR, "..", "salidas_json")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{nombre_base}_resumen.json")

    try:
        contenido_json = contenido_json.strip()

        # Eliminar formato Markdown tipo ```json ... ```
        if contenido_json.startswith("```json") or contenido_json.startswith("```"):
            contenido_json = re.sub(r"^```(?:json)?\s*|```$", "", contenido_json.strip(), flags=re.DOTALL).strip()

        json_data = json.loads(contenido_json)

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Resumen guardado en: {ruta}")
    except Exception as e:
        print(f"❌ No se pudo guardar el JSON: {e}")

def generar_resumen_con_openai(texto_extraido: str, nombre_archivo_salida: str = "ficha") -> str:
    instrucciones = cargar_instrucciones_texto()
    plantilla = cargar_plantilla_json()
    tipos_ayuda_str = cargar_lista_tipo_ayuda()

    prompt = f"""
Eres un asistente legal experto en ayudas públicas. Tu tarea es analizar el texto legal proporcionado y devolver un resumen estructurado en formato JSON, siguiendo fielmente la plantilla y todas las reglas del proyecto Fichas Miguel.

 DIRECTRICES CLAVE (cumple todas):

1. **denominacion_normativa_nombre_ayuda**:
   - Resume el título oficial.
   - Incluye el año de la convocatoria si aparece.
   - Si es plurianual, refleja el año correspondiente.

2. **tipo_ayuda**: solo puede contener términos exactos de esta lista cerrada:
{tipos_ayuda_str}

3. **descripcion**:
   - Desarrolla una descripción exhaustiva y clara.
   - Detalla modalidades, servicios cubiertos, requisitos y finalidad.
   - Indica incompatibilidades solo si aparecen literalmente en el texto.
   - No repitas información que ya se indica en cuantía, requisitos o documentación.
   - No incluyas valores económicos aquí.

4. **cuantia**:
   - Incluir solo cantidades que el beneficiario percibe o paga finalmente.
   - Refleja tramos, descuentos aplicados o aportaciones finales.
   - No inventes ni adaptes valores.
   - Si hay tablas o escalas, conviértelas en una lista clara.

5. **referencia_legislativa**:
   - Incluye todas las normas mencionadas, sin omitir ninguna disposición legal.
   - Una por línea, completas y literales.

6. **lugares_presentacion.online**:
   - Si hay sede electrónica concreta, inclúyela primero.
   - Luego añade siempre esta frase: "También puede presentarse a través de la Red SARA (Sistema de Aplicaciones y Redes para las Administraciones), una plataforma estatal segura que permite enviar solicitudes electrónicas a cualquier administración pública, usando certificado digital o sistema Cl@ve."

📎 Instrucciones completas del proyecto:
{instrucciones}

 Texto legal a analizar:
---
{texto_extraido}
---

 Plantilla JSON a completar:
{json.dumps(plantilla, indent=2, ensure_ascii=False)}

 Devuelve únicamente el JSON final, sin encabezados, sin explicaciones ni comentarios.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096
        )
        resultado = response.choices[0].message.content.strip()
        guardar_json_generado(resultado, nombre_archivo_salida)
        return resultado
    except Exception as e:
        print(f"[ERROR] Error al llamar a OpenAI: {e}")
        return ""

def resumir_desde_archivo(path_txt: str) -> str:
    nombre_base = os.path.splitext(os.path.basename(path_txt))[0]
    with open(path_txt, "r", encoding="utf-8") as f:
        texto = f.read()

    chunks = dividir_en_chunks(texto)
    resumenes = []

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        print(f"🧩 Procesando chunk {i+1}/{len(chunks)}...")
        resumen = generar_resumen_con_openai(chunk, f"{nombre_base}_parte{i+1}")
        resumenes.append(resumen)

    return "\n\n".join(resumenes)

def resumir_desde_varios_archivos(lista_rutas: list[str], nombre_base: str = "ficha") -> str:
    texto_completo = extraer_textos_unificados(lista_rutas)
    chunks = dividir_en_chunks(texto_completo)
    resumenes = []

    for i, chunk in enumerate(chunks):
        print(f"🧩 Procesando chunk {i+1}/{len(chunks)} (multiarchivo)...")
        resumen = generar_resumen_con_openai(chunk, f"{nombre_base}_parte{i+1}")
        resumenes.append(resumen)

    return "\n\n".join(resumenes)
