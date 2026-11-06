import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from google import genai
from ..config import GEMINI_API_KEY, MEMBROS_CAAT
from .common import gerar_conteudo_com_resiliencia

PROMPT_EXTRATOR = """Você é o Agente Extrator de Informações do Centro Acadêmico Alan Turing (CAAT - UNIFEI).
Sua função é analisar a gravação de áudio ou transcrição da reunião e as anotações do secretário para extrair APENAS FATOS VERÍDICOS em formato estruturado.

Contexto Institucional:
- O CAAT (Engenharia de Computação) realiza diversas atividades e eventos (como a UNIFEI Tech Week) em parceria com os centros acadêmicos irmãos:
  * CCO (Centro Acadêmico de Ciência da Computação)
  * CABIA (Centro Acadêmico do Bacharelado em Inteligência Artificial)
- Fique atento a divisões financeiras, cotas, lucro ou alocação de horas que envolvam essas três entidades (frequentemente na proporção 50% CAAT, 25% CCO e 25% CABIA).

Quadro de Membros e Diretorias do CAAT para referência:
{membros_json}

Regras Cruciais:
1. Ouça/leia atentamente toda a reunião e agrupe as discussões por temas/pautas bem definidos.
2. Para cada tema, separe o que foi discutido (contexto/argumentos) do que foi de fato DECIDIDO (deliberações, aprovações, votações, tarefas).
3. Capture prazos, valores monetários, datas de eventos e nomes de membros responsáveis por tarefas.
4. Identifique avisos gerais, recados da presidência ou cobranças de equipe para a seção de Feedbacks Gerais.
5. Se algum ponto for confuso, inaudível ou duvidoso, adicione-o na lista de "incertezas" para checagem humana.

Responda ESTRITAMENTE em formato JSON seguindo este esquema:
{{
  "pautas": ["Nome Resumido da Pauta 1", "Nome Resumido da Pauta 2"],
  "topicos": [
    {{
      "titulo": "1. Nome do Assunto",
      "discussao_bruta": "Resumo objetivo do que foi discutido...",
      "resultados_brutos": [
        "Deliberação ou tarefa 1 com responsável e prazo",
        "Deliberação ou tarefa 2"
      ]
    }}
  ],
  "feedbacks_brutos": [
    {{
      "titulo": "Tema do Feedback",
      "conteudo": "Orientação ou recomendação repassada à equipe..."
    }}
  ],
  "incertezas": [
    "Dúvida 1 sobre um valor ou responsável não totalmente claro"
  ]
}}
"""

def extrair_informacoes(
    transcricao: Optional[str] = None,
    audio_path: Optional[str] = None,
    metadados: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Agente 1: Extrai dados estruturados a partir de áudio ou texto de transcrição."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY não configurada. Defina a chave no arquivo .env.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    metadados = metadados or {}

    membros_str = json.dumps([{"nome": m["nome"], "cargo": m["cargo"]} for m in MEMBROS_CAAT], ensure_ascii=False, indent=2)
    prompt = PROMPT_EXTRATOR.format(membros_json=membros_str)
    
    conteudo_metadados = f"""Metadados da Reunião:
- Data: {metadados.get('data')}
- Horário: {metadados.get('horario_inicial')} às {metadados.get('horario_final')}
- Local: {metadados.get('local')}
- Presentes informados pelo secretário: {', '.join(metadados.get('presentes', []))}
"""

    contents = [prompt, conteudo_metadados]

    uploaded_file = None
    if audio_path and Path(audio_path).exists():
        print(f"  -> Fazendo upload do áudio para a API do Gemini ({Path(audio_path).name})...")
        uploaded_file = client.files.upload(file=str(audio_path))
        print("  -> Aguardando processamento do arquivo de áudio...")
        
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise RuntimeError(f"Falha ao processar arquivo de áudio no Gemini: {uploaded_file.error}")

        contents.append(uploaded_file)
        print("  -> Áudio carregado com sucesso. Analisando reunião...")
    elif transcricao:
        contents.append(f"Transcrição da Reunião:\n{transcricao}")
    else:
        raise ValueError("É necessário fornecer uma transcrição de texto ou o caminho de um arquivo de áudio.")

    try:
        texto_resposta = gerar_conteudo_com_resiliencia(
            client=client,
            contents=contents,
            response_mime_type="application/json",
            temperature=0.1
        )
        return json.loads(texto_resposta)
    finally:
        # Limpeza do arquivo temporário no Google AI Studio
        if uploaded_file:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass
