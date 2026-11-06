import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
from typing import List, Dict, Any, Set
from .config import TEMPLATE_PATH, OUTPUT_DIR, MEMBROS_CAAT

def normalizar_texto(txt: str) -> str:
    import unicodedata
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def identificar_presentes(presentes_raw: List[str]) -> Set[str]:
    """Cruza nomes/apelidos passados pelo usuário com a lista oficial de 21 membros com correspondência flexível."""
    presentes_oficiais = set()
    conjuncoes = {'de', 'da', 'do', 'dos', 'das', 'e'}

    for r in presentes_raw:
        r_strip = r.strip()
        if not r_strip:
            continue
        r_norm = normalizar_texto(r_strip)
        partes_r = [p for p in r_norm.split() if p not in conjuncoes]

        for membro in MEMBROS_CAAT:
            nome_norm = normalizar_texto(membro["nome"])
            partes_nome = [p for p in nome_norm.split() if p not in conjuncoes]
            apelidos_norm = [normalizar_texto(a) for a in membro.get("apelidos", [])]

            # 1. Correspondência exata ou por apelido/cargo
            if r_norm == nome_norm or r_norm in apelidos_norm:
                presentes_oficiais.add(membro["nome"])
                break

            # 2. Subconjunto de partes significativas (ex: 'Bernardo Augusto de Figueiredo')
            if len(partes_r) >= 2 and set(partes_r).issubset(set(partes_nome)):
                presentes_oficiais.add(membro["nome"])
                break

            # 3. Primeiro e último nome coincidem
            if len(partes_r) >= 2 and partes_r[0] == partes_nome[0] and partes_r[-1] == partes_nome[-1]:
                presentes_oficiais.add(membro["nome"])
                break

            # 4. Apenas primeiro nome quando único na diretoria
            if len(partes_r) == 1:
                nomes_com_mesmo_primeiro = [
                    m["nome"] for m in MEMBROS_CAAT 
                    if normalizar_texto(m["nome"]).startswith(partes_r[0] + " ")
                ]
                if len(nomes_com_mesmo_primeiro) == 1 and partes_r[0] == partes_nome[0]:
                    presentes_oficiais.add(membro["nome"])
                    break

    return presentes_oficiais

def formatar_paragrafo_topico(cell, titulo: str, discussao: str, resultados: List[str]):
    # Título do Tópico (ex: 1. Nome do Assunto)
    p_tit = cell.add_paragraph()
    p_tit.paragraph_format.space_before = Pt(8)
    p_tit.paragraph_format.space_after = Pt(2)
    p_tit.paragraph_format.line_spacing = 1.15
    run_tit = p_tit.add_run(titulo)
    run_tit.bold = True
    run_tit.font.name = "Calibri"
    run_tit.font.size = Pt(12)

    # Bloco Discussão
    if discussao:
        p_disc = cell.add_paragraph()
        p_disc.paragraph_format.space_before = Pt(2)
        p_disc.paragraph_format.space_after = Pt(2)
        p_disc.paragraph_format.line_spacing = 1.15
        
        run_bullet = p_disc.add_run("○ ")
        run_bullet.bold = True
        run_bullet.font.name = "Calibri"
        run_bullet.font.size = Pt(11)

        run_lbl = p_disc.add_run("Discussão: ")
        run_lbl.bold = True
        run_lbl.font.name = "Calibri"
        run_lbl.font.size = Pt(11)

        run_txt = p_disc.add_run(discussao)
        run_txt.font.name = "Calibri"
        run_txt.font.size = Pt(11)

    # Bloco Resultados Decididos
    if resultados:
        p_res_header = cell.add_paragraph()
        p_res_header.paragraph_format.space_before = Pt(2)
        p_res_header.paragraph_format.space_after = Pt(2)
        p_res_header.paragraph_format.line_spacing = 1.15
        
        run_bullet = p_res_header.add_run("○ ")
        run_bullet.bold = True
        run_bullet.font.name = "Calibri"
        run_bullet.font.size = Pt(11)

        run_lbl = p_res_header.add_run("Resultados Decididos:")
        run_lbl.bold = True
        run_lbl.font.name = "Calibri"
        run_lbl.font.size = Pt(11)

        for res in resultados:
            p_res = cell.add_paragraph()
            p_res.paragraph_format.left_indent = Pt(18)
            p_res.paragraph_format.space_before = Pt(1)
            p_res.paragraph_format.space_after = Pt(2)
            p_res.paragraph_format.line_spacing = 1.15
            
            run_dash = p_res.add_run("▪ ")
            run_dash.font.name = "Calibri"
            run_dash.font.size = Pt(11)
            
            run_res = p_res.add_run(res)
            run_res.font.name = "Calibri"
            run_res.font.size = Pt(11)

def formatar_feedbacks(cell, feedbacks: List[Dict[str, str]], numero_secao: int = 5):
    if not feedbacks:
        return
        
    p_header = cell.add_paragraph()
    p_header.paragraph_format.space_before = Pt(8)
    p_header.paragraph_format.space_after = Pt(2)
    p_header.paragraph_format.line_spacing = 1.15
    run_hdr = p_header.add_run(f"{numero_secao}. FEEDBACKS E ORIENTAÇÕES GERAIS DE GESTÃO")
    run_hdr.bold = True
    run_hdr.font.name = "Calibri"
    run_hdr.font.size = Pt(12)

    for item in feedbacks:
        p_item = cell.add_paragraph()
        p_item.paragraph_format.space_before = Pt(2)
        p_item.paragraph_format.space_after = Pt(3)
        p_item.paragraph_format.line_spacing = 1.15
        
        run_bullet = p_item.add_run("• ")
        run_bullet.bold = True
        run_bullet.font.name = "Calibri"
        run_bullet.font.size = Pt(11)

        titulo = item.get("titulo", "")
        if titulo:
            run_t = p_item.add_run(f"{titulo}: ")
            run_t.bold = True
            run_t.font.name = "Calibri"
            run_t.font.size = Pt(11)

        conteudo = item.get("conteudo", "")
        run_c = p_item.add_run(conteudo)
        run_c.font.name = "Calibri"
        run_c.font.size = Pt(11)

def gerar_docx_ata(dados: Dict[str, Any], output_path: Path = None) -> Path:
    """Preenche o template de 2026.2 e gera o arquivo .docx com formatação oficial."""
    doc = docx.Document(TEMPLATE_PATH)

    numero_ata = str(dados.get("numero_ata", "41"))
    data = dados.get("data", "")
    horario_ini = dados.get("horario_inicial", "")
    horario_fim = dados.get("horario_final", "")
    local = dados.get("local", "Google Meet")
    link_chamada = dados.get("link_chamada", "")
    pautas_list = dados.get("pautas", [])
    pautas_str = ", ".join(pautas_list) if isinstance(pautas_list, list) else str(pautas_list)
    presentes_raw = dados.get("presentes", [])
    presentes_set = identificar_presentes(presentes_raw)

    # 1. Atualizar Título no topo mantendo a imagem da logo intacta
    p1 = doc.paragraphs[1]
    p1.runs[0].text = f"Ata N#{numero_ata}"

    # 2. Tabela 0: Identificação e Acessos
    t0 = doc.tables[0]
    t0.rows[0].cells[0].paragraphs[0].text = f"Ata nº: {numero_ata}"
    
    # Célula Local e Pautas
    cell_local = t0.rows[1].cells[0]
    cell_local.text = ""
    p_loc = cell_local.paragraphs[0]
    p_loc.paragraph_format.line_spacing = 1.15
    run_loc_lbl = p_loc.add_run("Local: ")
    run_loc_lbl.bold = True
    p_loc.add_run(f"{local}\n\n")
    run_paut_lbl = p_loc.add_run("Pautas discutidas:\n")
    run_paut_lbl.bold = True
    p_loc.add_run(pautas_str)

    # Célula Link de chamada
    cell_link = t0.rows[1].cells[1]
    cell_link.text = ""
    p_link = cell_link.paragraphs[0]
    p_link.paragraph_format.line_spacing = 1.15
    if link_chamada:
        run_link_lbl = p_link.add_run("Link da chamada:\n")
        run_link_lbl.bold = True
        p_link.add_run(link_chamada)

    # 3. Tabela 1: Data e Horários
    t1 = doc.tables[1]
    t1.rows[1].cells[0].paragraphs[0].text = data
    t1.rows[1].cells[1].paragraphs[0].text = horario_ini
    t1.rows[1].cells[2].paragraphs[0].text = horario_fim
    for c in t1.rows[1].cells:
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 4. Tabela 2: Participantes (21 membros)
    t2 = doc.tables[2]
    for row in t2.rows[2:]:
        nome_membro = row.cells[0].text.strip()
        cell_pres = row.cells[2]
        cell_pres.text = ""
        p_pres = cell_pres.paragraphs[0]
        p_pres.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if nome_membro in presentes_set:
            run_x = p_pres.add_run("X")
            run_x.bold = True

    # 5. Tabela 3: Assuntos
    t3 = doc.tables[3]
    cell_assuntos = t3.rows[1].cells[0]
    
    # Limpa parágrafos antigos
    p_first = cell_assuntos.paragraphs[0]
    p_first.text = ""
    for p in list(cell_assuntos.paragraphs)[1:]:
        cell_assuntos._tc.remove(p._p)

    # Insere tópicos
    topicos = dados.get("topicos", [])
    for idx, topico in enumerate(topicos):
        titulo = topico.get("titulo", "")
        # Se não começar com número, numera automaticamente
        if not any(titulo.strip().startswith(f"{i}.") for i in range(1, 15)):
            titulo = f"{idx + 1}. {titulo}"
        discussao = topico.get("discussao", "")
        resultados = topico.get("resultados", [])
        formatar_paragrafo_topico(cell_assuntos, titulo, discussao, resultados)

    # Insere feedbacks numerados sequencialmente
    feedbacks = dados.get("feedbacks", [])
    if feedbacks:
        proximo_numero = len(topicos) + 1
        formatar_feedbacks(cell_assuntos, feedbacks, numero_secao=proximo_numero)

    # Salva arquivo
    if not output_path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # Formata data para o nome do arquivo DD-MM-AAAA
        data_slug = data.replace("/", "-") if data else "SEM-DATA"
        output_path = OUTPUT_DIR / f"{numero_ata}_ATA_CAAT_{data_slug}.docx"

    try:
        doc.save(str(output_path))
    except PermissionError:
        # Se o arquivo estiver aberto no Word pelo usuário, salva com sufixo _revisada
        alt_path = output_path.parent / f"{output_path.stem}_revisada{output_path.suffix}"
        print(f"  [Aviso] O arquivo '{output_path.name}' está aberto no Word. Salvando versão revisada em '{alt_path.name}'.")
        doc.save(str(alt_path))
        output_path = alt_path

    return output_path
