import json
from typing import Dict, Any, List
from google import genai
from ..config import GEMINI_API_KEY
from .common import gerar_conteudo_com_resiliencia

PROMPT_REVISOR = """Você é o Agente Auditor e Revisor de Atas do Centro Acadêmico Alan Turing (CAAT - UNIFEI).
Sua função é confrontar a minuta gerada pelo Redator com a Transcrição Original e as anotações do secretário para garantir 100% DE FIDELIDADE FACTUAL.

Critérios de Auditoria:
1. Fidelidade Numérica e Temporal: Os valores monetários (ex: R$), datas de eventos, horários e prazos correspondem exatamente ao que foi dito na gravação?
2. Atribuição de Responsabilidades: As tarefas foram delegadas às pessoas certas mencionadas na reunião?
3. Ausência de Alucinação: Não foi inventada nenhuma decisão que não tenha ocorrido?
4. Coerência dos Membros: Todos os nomes citados no texto pertencem ao quadro do CAAT ou são convidados devidamente identificados?

Responda ESTRITAMENTE em formato JSON:
{{
  "aprovado_sem_ressalvas": true/false,
  "alertas_secretaria": [
    "Aviso ou dúvida 1 para o secretário conferir antes de assinar",
    "Aviso 2 (se houver)"
  ],
  "minuta_final": {{
    "pautas": ["Pauta 1", "Pauta 2"],
    "topicos": [
      {{
        "titulo": "1. Nome do Assunto",
        "discussao": "Texto da discussão revisado...",
        "resultados": [
          "Resultado 1",
          "Resultado 2"
        ]
      }}
    ],
    "feedbacks": [
      {{
        "titulo": "Tema",
        "conteudo": "Texto..."
      }}
    ]
  }}
}}
"""

def revisar_ata(minuta: Dict[str, Any], transcricao: str, incertezas: List[str] = None) -> Dict[str, Any]:
    """Agente 3: Audita a minuta contra a transcrição original e emite relatório de conformidade."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY não configurada.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = PROMPT_REVISOR
    conteudo_comparacao = f"""Transcrição Original da Reunião:
{transcricao}

Dúvidas e Incertezas levantadas pelo Extrator:
{json.dumps(incertezas or [], ensure_ascii=False, indent=2)}

Minuta Gerada pelo Redator para Auditoria:
{json.dumps(minuta, ensure_ascii=False, indent=2)}
"""

    texto_resposta = gerar_conteudo_com_resiliencia(
        client=client,
        contents=[prompt, conteudo_comparacao],
        response_mime_type="application/json",
        temperature=0.0
    )

    return json.loads(texto_resposta)
