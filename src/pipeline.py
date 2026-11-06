import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .config import OUTPUT_DIR, GEMINI_API_KEY
from .agents.extractor import extrair_informacoes
from .agents.writer import redigir_ata
from .agents.reviewer import revisar_ata
from .docx_generator import gerar_docx_ata, identificar_presentes
from .drive_service import upload_ata_para_drive

def obter_proximo_numero_ata() -> int:
    """Descobre o próximo número de ata a partir dos arquivos existentes na pasta 2026.2."""
    if not OUTPUT_DIR.exists():
        return 41
    numeros = []
    for f in OUTPUT_DIR.glob("*.docx"):
        nome = f.stem
        partes = nome.split("_")
        if partes and partes[0].isdigit():
            numeros.append(int(partes[0]))
    return max(numeros) + 1 if numeros else 41

def executar_fluxo_completo(
    transcricao: Optional[str] = None,
    audio_path: Optional[str] = None,
    metadados: Optional[Dict[str, Any]] = None,
    mock_mode: bool = False
) -> Dict[str, Any]:
    """Executa o pipeline completo: Agente 1 (Extrator) -> Agente 2 (Redator) -> Agente 3 (Revisor) -> DOCX Generator."""
    metadados = metadados or {}
    print("\n[1/4] Executando Agente Extrator...")
    
    if mock_mode or not GEMINI_API_KEY:
        print("  -> Modo Simulação / Teste (sem chamada de LLM externa).")
        dados_extraidos = {
            "pautas": ["Alinhamento das Demandas da Semana", "Planejamento dos Próximos Eventos"],
            "topicos": [
                {
                    "titulo": "1. Alinhamento das Demandas da Semana",
                    "discussao_bruta": "Apresentação do andamento das tarefas de cada diretoria.",
                    "resultados_brutos": ["Prazos alinhados para entrega no final do mês."]
                }
            ],
            "feedbacks_brutos": [
                {
                    "titulo": "Organização Geral",
                    "conteudo": "Manter os status atualizados nas plataformas de gestão."
                }
            ],
            "incertezas": []
        }
        minuta_redigida = {
            "pautas": dados_extraidos["pautas"],
            "topicos": [
                {
                    "titulo": "1. Alinhamento das Demandas da Semana",
                    "discussao": "Realizou-se a revisão periódica das atividades das diretorias, com foco no cumprimento do cronograma semestral.",
                    "resultados": ["Definiu-se a manutenção do acompanhamento contínuo dos prazos operacionais."]
                }
            ],
            "feedbacks": [
                {
                    "titulo": "Organização Geral",
                    "conteudo": "Orientou-se aos integrantes manter os registros de atividades rigorosamente em dia."
                }
            ]
        }
        resultado_revisao = {
            "aprovado_sem_ressalvas": True,
            "alertas_secretaria": ["Simulação concluída com sucesso."],
            "minuta_final": minuta_redigida
        }
    else:
        # Cache temporário para não precisar re-enviar áudio em caso de reexecução rápida
        cache_path = Path("dados_extraidos_cache.json")
        if cache_path.exists():
            print("  -> Carregando extração do cache local...")
            with open(cache_path, "r", encoding="utf-8") as cf:
                dados_extraidos = json.load(cf)
        else:
            dados_extraidos = extrair_informacoes(
                transcricao=transcricao,
                audio_path=audio_path,
                metadados=metadados
            )
            with open(cache_path, "w", encoding="utf-8") as cf:
                json.dump(dados_extraidos, cf, ensure_ascii=False, indent=2)
        incertezas = dados_extraidos.get("incertezas", [])
        
        print("\n[2/4] Executando Agente Redator (Padronização 2026.2)...")
        # Agente 2: Redator
        minuta_redigida = redigir_ata(dados_extraidos)

        print("\n[3/4] Executando Agente Revisor (Auditoria Factual)...")
        # Agente 3: Revisor
        contexto_verificacao = transcricao or f"Pautas e tópicos extraídos do áudio:\n{json.dumps(dados_extraidos, ensure_ascii=False, indent=2)}"
        resultado_revisao = revisar_ata(minuta_redigida, contexto_verificacao, incertezas)

    minuta_final = resultado_revisao.get("minuta_final", minuta_redigida)
    alertas = resultado_revisao.get("alertas_secretaria", [])

    # Monta payload final para o gerador de DOCX
    dados_docx = {
        "numero_ata": metadados.get("numero_ata"),
        "data": metadados.get("data"),
        "horario_inicial": metadados.get("horario_inicial"),
        "horario_final": metadados.get("horario_final"),
        "local": metadados.get("local", "Google Meet"),
        "link_chamada": metadados.get("link_chamada", ""),
        "pautas": minuta_final.get("pautas", []),
        "presentes": metadados.get("presentes", []),
        "topicos": minuta_final.get("topicos", []),
        "feedbacks": minuta_final.get("feedbacks", [])
    }

    print("\n[4/4] Gerando arquivo .docx com layout oficial do CAAT...")
    docx_path = gerar_docx_ata(dados_docx)

    return {
        "docx_path": docx_path,
        "alertas": alertas,
        "dados_finais": dados_docx,
        "presentes_identificados": identificar_presentes(metadados.get("presentes", []))
    }
