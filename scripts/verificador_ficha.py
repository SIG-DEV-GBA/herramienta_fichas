import logging
from scripts.validar_campo import validar_y_corregir_campo, tipo_esperado_por_campo
from typing import List

# Puedes añadir aquí campos que permiten estar vacíos si lo deseas
CAMPOS_OPCIONALES = [
    "criterios_concesion", "frase_publicitaria"
]

def verificar_ficha_vs_plantilla(plantilla: dict, ficha: dict) -> List[str]:
    errores = []

    for campo, valor_esperado in plantilla.items():
        if campo not in ficha:
            errores.append(f"❌ Campo ausente: '{campo}'")
            continue

        valor_crudo = ficha[campo]
        valor_corregido = validar_y_corregir_campo(campo, valor_crudo)
        tipo_esperado = tipo_esperado_por_campo(campo)

        # Tipo validado
        if tipo_esperado == "str" and not isinstance(valor_corregido, str):
            errores.append(f"⚠️ Tipo incorrecto en '{campo}': esperado str, obtenido {type(valor_corregido).__name__}")
        elif tipo_esperado == "list" and not isinstance(valor_corregido, list):
            errores.append(f"⚠️ Tipo incorrecto en '{campo}': esperado list, obtenido {type(valor_corregido).__name__}")
        elif tipo_esperado == "dict" and not isinstance(valor_corregido, dict):
            errores.append(f"⚠️ Tipo incorrecto en '{campo}': esperado dict, obtenido {type(valor_corregido).__name__}")
        elif tipo_esperado == "list[dict]":
            if not isinstance(valor_corregido, list) or not all(isinstance(i, dict) for i in valor_corregido):
                errores.append(f"⚠️ Tipo incorrecto en '{campo}': esperado list[dict], obtenido {type(valor_corregido).__name__}")

        # Verificar vacío (si no es campo opcional)
        if campo not in CAMPOS_OPCIONALES:
            if tipo_esperado == "str" and valor_corregido.strip() == "":
                errores.append(f"🟡 Campo vacío: '{campo}'")
            elif tipo_esperado == "list" and len(valor_corregido) == 0:
                errores.append(f"🟡 Campo vacío: '{campo}'")
            elif tipo_esperado == "dict" and not valor_corregido:
                errores.append(f"🟡 Campo vacío: '{campo}'")
            elif tipo_esperado == "list[dict]" and len(valor_corregido) == 0:
                errores.append(f"🟡 Campo vacío: '{campo}'")

    return errores
