import re
def sanitizar_texto(texto: str, max_len: int = 100) -> str:
    """
    [2] Elimina caracteres peligrosos y limita longitud.
    Permite letras, números, espacios, acentos y puntuación básica.
    """
    limpio = re.sub(r"[<>\"'%;()&+\\\x00-\x1f]", "", texto)
    return limpio.strip()[:max_len]