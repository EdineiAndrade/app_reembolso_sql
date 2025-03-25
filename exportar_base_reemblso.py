import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import pandas as pd

def gerar_pdf(agente, df_agente):
    """Gera um PDF a partir de um DataFrame."""
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
                          leftMargin=6, rightMargin=6, 
                          topMargin=6, bottomMargin=6)

    # Converter DataFrame para lista de listas
    data = [df_agente.columns.tolist()] + df_agente.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    pdf.build([table])
    buffer.seek(0)
    return buffer.getvalue()

def formatar_dataframe(df):
    """Formata o DataFrame para exibição."""
    df = df.sort_values(by='UNIDADE', ascending=True)

    # Formatar a coluna de data no padrão DD/MM/YYYY
    df['DT_PARCELA'] = df['DT_PARCELA'].apply(
        lambda x: pd.to_datetime(x).strftime('%d/%m/%Y')
    )
   
    df['PREVISTO'] = df['PREVISTO'].apply(
        lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    # Formatar a coluna de valores no padrão 1.000,00
    df['RECEBIDO'] = df['RECEBIDO'].fillna(0).apply(
        lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    
    return df

def exportar(df, base_dir):
    """
    Exporta os dados para arquivos PDF e Excel organizados por unidade e agente.
    
    Args:
        df: DataFrame com os dados a serem exportados
        base_dir: Diretório base onde os arquivos serão salvos
    """
    COLUNAS_OBRIGATORIAS  = [
        'NM_CLIENTE', 'OPERACAO', 'FINAL',
        'MES_PARCELA', 'DT_PARCELA', 'DIAS_REEM', 'PREVISTO', 'RECEBIDO',
        'STATUS', 'MUNICIPIO', 'ID_AGROAMIGO', 'Nome_Agente', 'UNIDADE'
    ]
    
    # 1. Verificar e manter apenas as colunas obrigatórias que existem no DataFrame
    colunas_validas = [col for col in COLUNAS_OBRIGATORIAS if col in df.columns]
    df = df[colunas_validas]
    
    # 2. Verificar se há colunas faltantes
    colunas_faltantes = set(COLUNAS_OBRIGATORIAS) - set(colunas_validas)
    if colunas_faltantes:
        print(f"Aviso: As seguintes colunas não foram encontradas no DataFrame e serão ignoradas: {colunas_faltantes}")
    # Criar diretório base se não existir
    # 3. Atualizar status de pagamento (adaptação da sua regra)
    if 'STATUS' in df.columns and 'RECEBIDO' in df.columns and 'PREVISTO' in df.columns:
        # Converter para valores numéricos se necessário
        df['RECEBIDO'] = pd.to_numeric(df['RECEBIDO'].str.replace('.', '').str.replace(',', '.'), errors='coerce')
        df['PREVISTO'] = pd.to_numeric(df['PREVISTO'].str.replace('.', '').str.replace(',', '.'), errors='coerce')
        
        # Aplicar a regra de atualização de status
        df['STATUS'] = df.apply(
            lambda row: 'PAGO' if row['STATUS'] != 'PAGO' and row['RECEBIDO'] >= (row['PREVISTO'] * 0.98) 
                       else row['STATUS'],
            axis=1
        )
    else:
        print("Aviso: Colunas necessárias para atualização de status não encontradas")
    os.makedirs(base_dir, exist_ok=True)
    
    # Processar cada unidade
    for unidade in df['UNIDADE'].unique():
        unidade_dir = os.path.join(base_dir, str(unidade))
        os.makedirs(unidade_dir, exist_ok=True)
        
        # Filtrar dados da unidade
        df_unidade = df[df['UNIDADE'] == unidade]
        
        # Salvar Excel da unidade
        df_unidade.to_excel(os.path.join(unidade_dir, f"Reembolso_{unidade}.xlsx"), index=False)
        
        # Processar cada agente da unidade
        for agente in df_unidade['Nome_Agente'].unique():
            df_agente = df_unidade[df_unidade['Nome_Agente'] == agente].copy()
            df_agente = df_agente.sort_values(by='DIAS_REEM', ascending=True)
            
            # Preparar caminhos dos arquivos
            pdf_path = os.path.join(unidade_dir, f"{agente}.pdf")
            xlsx_path = os.path.join(unidade_dir, f"{agente}.xlsx")
            
            # Salvar Excel do agente
            df_agente.to_excel(xlsx_path, index=False)
            
            # Preparar dados para PDF (remover colunas e apenas não pagos)
            df_pdf = df_agente.drop(columns=["Nome_Agente", "UNIDADE", "MUNICIPIO", "ID_AGROAMIGO"])
            df_pdf = df_pdf[df_pdf['STATUS'] != "PAGO"]
            
            # Gerar e salvar PDF se houver dados
            if not df_pdf.empty:
                pdf_bytes = gerar_pdf(agente, df_pdf)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
            
            print(f"Processado: UNIDADE:{unidade} AGENTE:{agente}")

def exportar_base_reembolso(df_final):
            # Configurações
            BASE_DIR = r'C:\Users\inec\OneDrive - Instituto Nordeste Cidadania\AGROAMIGO\RELATÓRIOS\REEMBOLSO_2025'
            
            # Carregar dados (substitua por sua fonte de dados)
            # df = carregar_dados()  # Implemente esta função conforme necessário
            
            # Formatar e exportar
            df_formatado = formatar_dataframe(df_final)
            exportar(df_formatado, BASE_DIR)
            print("Exportação concluída!")