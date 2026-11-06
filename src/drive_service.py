import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import CREDENTIALS_FILE, TOKEN_FILE, DRIVE_SCOPES, DRIVE_FOLDER_ID

def obter_servico_drive():
    """Autentica e retorna a instância da API do Google Drive (compatível com OAuth e Service Account)."""
    if not CREDENTIALS_FILE.exists() and not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado em: {CREDENTIALS_FILE}\n"
            "Para integrar com o Google Drive:\n"
            "1. Crie um projeto no Google Cloud Console e ative a Google Drive API.\n"
            "2. Baixe o arquivo de credenciais (OAuth Client ID ou Service Account) e salve como 'credentials.json' na raiz do projeto."
        )

    creds = None

    # 1. Verifica se já temos um token OAuth salvo
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), DRIVE_SCOPES)
        except Exception:
            creds = None

    # 2. Se as credenciais forem inválidas ou expiradas, renova ou inicia novo fluxo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
        elif CREDENTIALS_FILE.exists():
            # Verifica se o arquivo é uma Service Account ou OAuth Client
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                cred_data = json.load(f)

            if cred_data.get("type") == "service_account":
                creds = service_account.Credentials.from_service_account_file(
                    str(CREDENTIALS_FILE), scopes=DRIVE_SCOPES
                )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), DRIVE_SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def upload_ata_para_drive(file_path: Path, folder_id: Optional[str] = None) -> Dict[str, Any]:
    """Faz o upload de um arquivo .docx para o Google Drive e retorna o ID e o link de visualização."""
    folder_id = folder_id or DRIVE_FOLDER_ID

    service = obter_servico_drive()

    file_metadata = {
        "name": file_path.name,
        "mimeType": "application/vnd.google-apps.document"  # Converte automaticamente para Google Docs editável se desejado
    }
    
    # Se quiser manter estritamente como arquivo .docx no Drive, basta remover mimeType acima ou usar docx mimeType
    # Vamos manter como .docx oficial (ou Docs conforme padrão do CA):
    file_metadata = {
        "name": file_path.name
    }

    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(
        str(file_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink, webContentLink"
    ).execute()

    return {
        "id": file.get("id"),
        "name": file.get("name"),
        "link": file.get("webViewLink")
    }
