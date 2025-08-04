import time
import random
import logging
from typing import Any, Callable

# Errores más comunes en la SDK de OpenAI
from openai import (
    RateLimitError,
    APIError,
    APIStatusError,
    APIConnectionError,
)


def call_with_retry(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 8,
    base_delay: float = 2.0,
    **kwargs: Any,
) -> Any:
    """Execute an OpenAI client function with exponential backoff.

    This helper centralises retry behaviour for all OpenAI requests. It honours the
    ``Retry-After`` header when available and falls back to a jittered exponential
    backoff. Network and availability errors are also retried.

    Parameters
    ----------
    func : Callable
        Client method to call (e.g. ``client.chat.completions.create``).
    max_retries : int, optional
        Maximum number of attempts before giving up, by default ``8``.
    base_delay : float, optional
        Initial delay in seconds for the backoff, by default ``2.0``.
    *args, **kwargs : Any
        Arguments forwarded to the client function.
    """

    for intento in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (RateLimitError, APIStatusError, APIError, APIConnectionError) as err:
            # Determinar el código de estado asociado al error
            status = getattr(err, "status_code", None)
            if isinstance(err, RateLimitError):
                status = 429

            # Errores distintos de rate limit o servidor se relanzan
            if status not in (429, 500, 502, 503, 504, None) and not isinstance(
                err, APIConnectionError
            ):
                raise

            if intento == max_retries - 1:
                raise

            # Intentar respetar cabecera Retry-After si está disponible
            retry_after = None
            resp = getattr(err, "response", None)
            if resp is not None:
                headers = getattr(resp, "headers", {})
                retry_after = headers.get("Retry-After") or headers.get("retry-after")

            if retry_after is not None:
                espera = float(retry_after)
            else:
                espera_base = base_delay * (2 ** intento)
                jitter = espera_base * random.random()
                espera = espera_base + jitter

            logging.warning(
                f"Rate limit o error de red, reintentando en {espera:.1f}s..."
            )
            time.sleep(espera)

    # Si se alcanzan todos los intentos sin éxito, relanzar una excepción genérica
    raise RuntimeError("Máximo de reintentos alcanzado")
