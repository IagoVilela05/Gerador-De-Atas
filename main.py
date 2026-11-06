#!/usr/bin/env python3
import sys
import argparse
from datetime import datetime
from pathlib import Path

from src.pipeline import executar_fluxo_completo, obter_proximo_numero_ata
from src.config import MEMBROS_CAAT
from src.drive_service import upload_ata_para_drive

def carregar_presentes_de_arquivo(caminho: Path):
    if not caminho.exists():
        return []
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        linhas = f.readlines()
    presentes = []
    for l in linhas:
        l_strip = l.strip()
        # Ignora cabeçalhos como 'Presença Reunião 05/11'
        if not l_strip or "presenca" in l_strip.lower() or "reuniao" in l_strip.lower() or "data" in l_strip.lower():
            continue
        presentes.append(l_strip)
    return presentes

def main():
    parser = argparse.ArgumentParser(description="Gerador de Atas Multi-Agente CAAT")
    parser.add_argument("--transcricao", help="Caminho do arquivo de texto da transcrição")
    parser.add_argument("--audio", help="Caminho do arquivo de áudio (.mp3, .wav, .m4a)")
    parser.add_argument("--presenca-arquivo", help="Caminho do arquivo .txt com a lista de presença")
    parser.add_argument("--numero", help="Número da ata")
    parser.add_argument("--data", help="Data da reunião (DD/MM/AAAA)")
    parser.add_argument("--inicio", help="Horário de início (HH:MM)")
    parser.add_argument("--fim", help="Horário de término (HH:MM)")
    parser.add_argument("--local", help="Local ou plataforma")
    parser.add_argument("--link", help="Link da chamada")
    parser.add_argument("--presentes", help="Lista de presentes separados por vírgula")
    parser.add_argument("--mock", action="store_true", help="Executa em modo simulação sem chamar API externa")
    parser.add_argument("--auto-approve", action="store_true", help="Aprova automaticamente sem prompt interativo")

    args = parser.parse_args()

    audio_path = args.audio
    transcricao = ""

    # Se --transcricao for um arquivo de áudio/vídeo
    if args.transcricao:
        p = Path(args.transcricao)
        if p.suffix.lower() in [".mp3", ".wav", ".m4a", ".aac"]:
            audio_path = str(p)
        elif p.exists():
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                transcricao = f.read()

    # Presentes
    presentes = []
    if args.presenca_arquivo:
        presentes = carregar_presentes_de_arquivo(Path(args.presenca_arquivo))
    elif args.presentes:
        presentes = [p.strip() for p in args.presentes.split(",") if p.strip()]

    prox_num = obter_proximo_numero_ata()
    metadados = {
        "numero_ata": args.numero or str(prox_num),
        "data": args.data or datetime.now().strftime("%d/%m/%Y"),
        "horario_inicial": args.inicio or "19:30",
        "horario_final": args.fim or "20:45",
        "local": args.local or "Google Meet",
        "link_chamada": args.link or "",
        "presentes": presentes
    }

    # Executa o pipeline de agentes e gerador de documento
    resultado = executar_fluxo_completo(
        transcricao=transcricao,
        audio_path=audio_path,
        metadados=metadados,
        mock_mode=args.mock
    )
    docx_path = resultado["docx_path"]
    alertas = resultado["alertas"]
    presentes_id = resultado["presentes_identificados"]

    print("\n" + "=" * 60)
    print("  RELATÓRIO DE AUDITORIA E CONFERÊNCIA (AGENTE REVISOR)")
    print("=" * 60)

    print(f"\nDocumento gerado: {docx_path.name}")
    print(f"Local salvo: {docx_path.resolve()}")

    print("\nQuórum e Presença:")
    print(f"Total de presentes identificados: {len(presentes_id)} de {len(MEMBROS_CAAT)}")
    for m in MEMBROS_CAAT:
        nome = m["nome"]
        marcado = "[X]" if nome in presentes_id else "[ ]"
        print(f"  {marcado} {nome} ({m['cargo']})")

    if alertas:
        print("\nPontos de Atenção / Incertezas para a Secretaria:")
        for al in alertas:
            print(f"  - {al}")
    else:
        print("\nNenhuma pendência ou inconsistência factual identificada.")

    # Portão de Validação Humana para envio ao Google Drive
    print("\n" + "-" * 60)
    if args.auto_approve:
        resposta = "s"
    else:
        resposta = input("Deseja aprovar e enviar a ata para o Google Drive agora? (s/n): ").strip().lower()

    if resposta == "s":
        print("\nIniciando envio para o Google Drive...")
        try:
            res_drive = upload_ata_para_drive(docx_path)
            print("Upload concluído com sucesso!")
            print(f"Nome no Drive: {res_drive['name']}")
            if res_drive.get("link"):
                print(f"Link de Acesso: {res_drive['link']}")
        except FileNotFoundError as fnf:
            print("\n[Aviso] Não foi possível enviar ao Drive:")
            print(fnf)
            print("\nO documento está salvo e pronto localmente.")
        except Exception as e:
            print(f"\n[Erro ao enviar para o Google Drive]: {e}")
    else:
        print(f"\nEnvio não realizado no Drive. O documento está pronto localmente em:\n{docx_path.resolve()}")

if __name__ == "__main__":
    main()
