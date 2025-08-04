import time
import random
import logging
from typing import Any, Callable

from openai import RateLimitError, APIError, APIStatusError


def call_with_retry(func: Callable[..., Any], *args: Any, max_retries: int = 5, base_delay: float = 2.0, **kwargs: Any) -> Any:
    """Execute an OpenAI client function with exponential backoff on rate limits.

    Parameters
    ----------
    func : Callable
        Client method to call (e.g. client.chat.completions.create).
    max_retries : int, optional
        Maximum number of attempts before giving up, by default 5.
    base_delay : float, optional
        Initial delay in seconds for the backoff, by default 2.0.
    \*args, \**kwargs : Any
        Arguments forwarded to the client function.
    """
    for intento in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (RateLimitError, APIStatusError, APIError) as err:
            # Determinar el código de estado asociado al error
            status = getattr(err, "status_code", None)
            if isinstance(err, RateLimitError):
                status = 429

            if status != 429 or intento == max_retries - 1:
                raise

            # Exponential backoff con jitter para evitar thundering herd
            espera_base = base_delay * (2 ** intento)
            jitter = espera_base * random.random()
            espera = espera_base + jitter
            logging.warning(f"Rate limit alcanzado, reintentando en {espera:.1f}s...")
            time.sleep(espera)

    # Si se alcanzan todos los intentos sin éxito, relanzar una excepción genérica
    raise RuntimeError("Máximo de reintentos alcanzado")
