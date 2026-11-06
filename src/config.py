import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "template_2026_2.docx"
OUTPUT_DIR = BASE_DIR / "ATAS" / "2026.2"

# Google Drive Configuration
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Gemini / LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Centros Acadêmicos Parceiros (Reuniões Conjuntas / Tech Week)
CENTROS_ACADEMICOS = [
    {"sigla": "CAAT", "nome": "Centro Acadêmico Alan Turing", "curso": "Engenharia de Computação"},
    {"sigla": "CCO", "nome": "Centro Acadêmico de Ciência da Computação", "curso": "Ciência da Computação"},
    {"sigla": "CABIA", "nome": "Centro Acadêmico do Bacharelado em Inteligência Artificial", "curso": "Bacharelado em Inteligência Artificial"}
]

# Official CAAT Members Roster (2026.2)
MEMBROS_CAAT = [
    {
        "nome": "Bernardo Augusto de Figueiredo Rodrigues",
        "cargo": "Presidente",
        "apelidos": ["bernardo", "bernardo augusto", "presidencia"]
    },
    {
        "nome": "Anna Clara Cardoso Martins",
        "cargo": "Vice-Presidente",
        "apelidos": ["anna", "anna clara", "ana clara", "vice"]
    },
    {
        "nome": "Rodrigo Ferreira Garcia da Silva",
        "cargo": "Dir. Marketing",
        "apelidos": ["rodrigo ferreira", "rodrigo garcia", "rodrigo marketing"]
    },
    {
        "nome": "Maria Fernanda Almeida Cunha Santos",
        "cargo": "Dir. Graduação",
        "apelidos": ["maria fernanda", "fernanda", "nanda"]
    },
    {
        "nome": "Matheus Lucas Tavares Bueno",
        "cargo": "Dir. Financeiro",
        "apelidos": ["matheus lucas tavares", "matheus financeiro", "tavares"]
    },
    {
        "nome": "Thamara Luiza Bicalho Oliveira",
        "cargo": "Dir. Gestão de Pessoas",
        "apelidos": ["thamara", "tamara", "thamara luiza", "rp"]
    },
    {
        "nome": "Frederico Pires de Moraes Gomes",
        "cargo": "Dir. Eventos",
        "apelidos": ["frederico", "fred", "frederico pires"]
    },
    {
        "nome": "Emanuel Reis Fiocco",
        "cargo": "Dir. Secretaria",
        "apelidos": ["emanuel", "emanuel reis", "secretaria"]
    },
    {
        "nome": "Fabrício Rickelmer Souza Duarte",
        "cargo": "Ass. Financeiro",
        "apelidos": ["fabricio", "fabrício", "fabricio rickelmer"]
    },
    {
        "nome": "Nicole Cíntia Alves Coelho",
        "cargo": "Ass. Graduação",
        "apelidos": ["nicole", "nicole cintia", "nicole cíntia"]
    },
    {
        "nome": "Matheus Lucas de Oliveira",
        "cargo": "Ass. Gestão de Pessoas",
        "apelidos": ["matheus lucas de oliveira", "matheus oliveira", "matheus gp"]
    },
    {
        "nome": "Pedro Fernandes Aguiar",
        "cargo": "Ass. Gestão de Pessoas",
        "apelidos": ["pedro", "pedro fernandes", "pedro aguiar"]
    },
    {
        "nome": "Ray Oliveira Coelho",
        "cargo": "Ass. Gestão de Pessoas",
        "apelidos": ["ray", "ray oliveira", "ray coelho"]
    },
    {
        "nome": "Iago Rafael Quaresma Lima",
        "cargo": "Ass. Graduação",
        "apelidos": ["iago rafael", "iago quaresma", "iago graduação"]
    },
    {
        "nome": "Gabriel Leandro Fonseca Silva",
        "cargo": "Ass. Eventos",
        "apelidos": ["gabriel", "gabriel leandro", "gabriel fonseca"]
    },
    {
        "nome": "João Henrique Menezes",
        "cargo": "Ass.",
        "apelidos": ["joao", "joão", "joao henrique", "joão henrique"]
    },
    {
        "nome": "Luiz Ferreira",
        "cargo": "Ass. Marketing",
        "apelidos": ["luiz", "luis", "luiz ferreira"]
    },
    {
        "nome": "Paulo Inácio Pereira",
        "cargo": "Ass. Eventos",
        "apelidos": ["paulo", "paulo inacio", "paulo inácio"]
    },
    {
        "nome": "Robson Borges",
        "cargo": "Ass.",
        "apelidos": ["robson", "robson borges"]
    },
    {
        "nome": "Rodrigo Amorim",
        "cargo": "Ass.",
        "apelidos": ["rodrigo amorim", "amorim"]
    },
    {
        "nome": "Iago Vieira Vilela",
        "cargo": "Ass. Secretaria / 2º Secretário",
        "apelidos": ["iago vieira", "iago vilela", "2º secretario", "segundo secretario"]
    }
]
