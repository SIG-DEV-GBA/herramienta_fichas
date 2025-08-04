def call_with_retry(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Ejecuta una función con reintentos en caso de errores como RateLimitError.

    Parameters
    ----------
    func : Callable
        La función que se desea ejecutar con lógica de reintentos.

    Returns
    -------
    Callable
        La función envuelta que incluye reintentos.
    """
    ...
