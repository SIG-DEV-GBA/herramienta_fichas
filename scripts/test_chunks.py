import sys
from scripts.embedding_manager import buscar_chunks_relevantes

DOC_ID = "documento_001"
TOP_N = 20

def mostrar_chunks(consulta: str):
    print(f"\n🔎 Consulta: '{consulta}' (top {TOP_N})\n{'=' * 60}")
    chunks = buscar_chunks_relevantes(consulta, doc_id=DOC_ID, top_n=TOP_N)

    if not chunks:
        print("⚠️  No se encontraron chunks relevantes.")
        return

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n[Chunk {i}]\n{'-' * 60}\n{chunk.strip()}\n{'-' * 60}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python test_chunks.py <palabra_clave_o_campo>")
        sys.exit(1)

    query = sys.argv[1]
    mostrar_chunks(query)
