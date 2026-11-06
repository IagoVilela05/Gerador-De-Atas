import os
import time
from typing import List, Any
from google import genai
from google.genai import types

MODEL_FALLBACKS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.7-flash"
]

def gerar_conteudo_com_resiliencia(
    client: genai.Client,
    contents: List[Any],
    response_mime_type: str = "application/json",
    temperature: float = 0.1
) -> str:
    """Tenta gerar conteúdo priorizando os modelos ultra-rápidos e alternando em caso de pico de demanda."""
    ultimo_erro = None

    for modelo in MODEL_FALLBACKS:
        for tentativa in range(2):
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type=response_mime_type,
                        temperature=temperature
                    )
                )
                return response.text
            except Exception as e:
                ultimo_erro = e
                err_msg = str(e)
                if any(code in err_msg for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                    time.sleep(3)
                else:
                    break

    raise RuntimeError(f"Não foi possível obter resposta após tentar os modelos: {ultimo_erro}")
