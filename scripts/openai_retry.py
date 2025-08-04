import time
import random
import logging
from typing import Any, Callable



    Parameters
    ----------
    func : Callable

            # Determinar el código de estado asociado al error
            status = getattr(err, "status_code", None)
            if isinstance(err, RateLimitError):
                status = 429


            time.sleep(espera)

    # Si se alcanzan todos los intentos sin éxito, relanzar una excepción genérica
    raise RuntimeError("Máximo de reintentos alcanzado")
