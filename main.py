import pandas as pd
import os

from atualizar_valores_recebidos import atualizar_valores_recebidos

from exportar_base_reemblso import exportar_base_reembolso

def main():
    # # Caminhos para os arquivos Excel
    base_reembolso = os.listdir(r"C:\Reembolso\Bases\base_reembolso")[0]
    base_reembolso = f"C:\\Reembolso\\Bases\\base_reembolso\\{base_reembolso}"
    
    base_valores_recebidos = os.listdir(r"C:\Reembolso\Bases\valores_recebidos")[0]
    base_valores_recebidos = f"C:\\Reembolso\\Bases\\valores_recebidos\\{base_valores_recebidos}"
    
    base_atualizado = os.listdir(r"C:\Reembolso\Bases\reembolso_atualizado")
 
    print("Lendo Arquivo Base Reembolso...") 
    df_reembolso = pd.read_excel(base_reembolso)
    print("Lendo Arquivo Valores Recebidos...") 
    df_recebidos = pd.read_excel(base_valores_recebidos)
    print("Atualizando Base Reembolso...")
    df_final = atualizar_valores_recebidos(df_reembolso,df_recebidos)
    print("Exportando arquivos...")
    exportar_base_reembolso(df_final)
    print("Processo Finalizado!!")
         

if __name__ == "__main__":

    main()