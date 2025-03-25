import pandas as pd
from datetime import datetime


def atualizar_valores_recebidos(df_reembolso,df_recebidos):
   
    # 1. Processamento do DataFrame de recebidos (equivalente à sua query SQL)
    # Filtrar as linhas conforme o critério do WHERE
    df_recebidos_filtrado = df_recebidos[df_recebidos['NM_OPC'].isin(['CLIENTE', 'BONUS DE ADIMPLENCIA-FNE','RENEGOCIACAO DE DIVIDAS'])]

    # Agrupar e agregar conforme o GROUP BY
    df_recebidos_agregado = df_recebidos_filtrado.groupby('cd_cli').agg(
        total_recebido=('VR_REA_MN', 'sum'),
        data_pagamento=('DT_LNC', 'max')
    ).reset_index()

    # Substituir valores nulos na coluna data_pagamento pela data padrão
    data_padrao = datetime(2025, 1, 1)
    df_recebidos_agregado['data_pagamento'] = df_recebidos_agregado['data_pagamento'].fillna(data_padrao)

    # 2. Atualizar a tabela reembolso com os valores recebidos
    df_atualizado = pd.merge(
        df_reembolso,
        df_recebidos_agregado,
        left_on="SICAD",    # Coluna da tabela reembolso
        right_on="cd_cli",  # Coluna da tabela valores_recebidos
        how="left"
    )

    # Dias que faltam para o reembolso
    df_atualizado["Dias_Reem."] = (df_atualizado["DT_PARCELA"] - datetime.now()).dt.days.round().astype(int) + 1

    # 3. Substituir a coluna "valores_recebidos" pelo total atualizado
    df_atualizado["RECEBIDO"] = df_atualizado["total_recebido"].astype(float).round(2).fillna(0.00)
    df_atualizado["VR_REEMBOLSO_PREVISTO"] = df_atualizado["VR_REEMBOLSO_PREVISTO"].astype(float).round(2)

    # Atualizar a coluna Status_Pagamento
    df_atualizado['STATUS_PAGAMENTO'] = df_atualizado.apply(
        lambda row: 'PAGO' if row['STATUS_PAGAMENTO'] != 'PAGO' and row['RECEBIDO'] >= (row['VR_REEMBOLSO_PREVISTO'] * 0.98) else row['STATUS_PAGAMENTO'],
        axis=1
    )

    # Remover colunas desnecessárias
    df_atualizado = df_atualizado.drop(columns=["POSICAO", "CD_APLICACAO", "NM_APLICACAO", "cd_cli", "total_recebido", "data_pagamento"])

    # Renomear colunas
    df_atualizado = df_atualizado.rename(columns={
        'STATUS_PAGAMENTO': 'STATUS',
        'VR_REEMBOLSO_PREVISTO': 'PREVISTO',
        'ID_RENEGOCIACAO': 'RENEG',
        'VR_REEMBOLSO_EFETIVO': 'EFETIVO',
        'REEMBOLSO_FINAL': 'FINAL',
        'NM_TP_QUITACAO': 'QUITACAO',
        'Dias_Reem.': 'DIAS_REEM',
        'NM_MUNICIPIO': 'MUNICIPIO',
        'NR_OPERACAO': 'FICHA',
        'TIPO_ACOMP': 'TP_ACOMP',
        'CD_CONTRATO': 'OPERACAO',
    })

    # Agora df_atualizado está pronto para uso

    return df_atualizado