import sys
import os
import fitz  # PyMuPDF
import docx

def extraer_texto_pdf(ruta_pdf: str) -> str:
    texto = ""
    try:
        with fitz.open(ruta_pdf) as doc:
            for pagina in doc:
                texto += pagina.get_text()
        return texto.strip()
    except Exception as e:
        print(f"[ERROR] Fallo al extraer texto del PDF: {e}")
        return ""

def extraer_texto_docx(ruta_docx: str) -> str:
    texto = ""
    try:
        doc = docx.Document(ruta_docx)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
        return texto.strip()
    except Exception as e:
        print(f"[ERROR] Fallo al extraer texto del DOCX: {e}")
        return ""

def detectar_tipo_archivo(ruta: str) -> str:
    ext = os.path.splitext(ruta)[1].lower()
    if ext == ".pdf":
        return "pdf"
    elif ext == ".docx":
        return "docx"
    else:
        raise ValueError("Formato de archivo no compatible. Solo se aceptan PDF o DOCX.")

def extraer_texto(ruta_archivo: str) -> str:
    tipo = detectar_tipo_archivo(ruta_archivo)
    if tipo == "pdf":
        return extraer_texto_pdf(ruta_archivo)
    elif tipo == "docx":
        return extraer_texto_docx(ruta_archivo)

    
def extraer_textos_unificados(lista_rutas: list[str]) -> str:
    """
    Dado una lista de rutas a archivos .pdf o .docx, extrae el texto de todos en orden
    y los concatena con separadores identificativos por documento.
    """
    textos = []
    for i, ruta in enumerate(lista_rutas):
        try:
            texto = extraer_texto(ruta)
            if texto.strip():
                nombre_archivo = os.path.basename(ruta)
                textos.append(f"--- DOCUMENTO {i+1} ({nombre_archivo}) ---\n{texto.strip()}")
        except Exception as e:
            print(f"[ERROR] Fallo en '{ruta}': {e}")
    return "\n\n".join(textos)

# Modo CLI / n8n
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extractor_texto.py <archivo1> [<archivo2> ...]")
        sys.exit(1)

    rutas = sys.argv[1:]
    texto_final = extraer_textos_unificados(rutas)
    print(texto_final)