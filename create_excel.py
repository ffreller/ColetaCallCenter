import pandas as pd
from src.definitions import INTERIM_DATA_DIR
from src.helper_functions import print_with_time, get_excel_fpath, generator_from_args

 
def gather_info_for_worksheets():
    print_with_time('Agrupando informações para as planilhas')
    # Lendo os datsets
    base = pd.read_pickle(INTERIM_DATA_DIR/'Base.pickle')
    orientacao = pd.read_pickle(INTERIM_DATA_DIR/'Orientação_De_Alta.pickle')
    atestado = pd.read_pickle(INTERIM_DATA_DIR/'Atestado.pickle')
    receita = pd.read_pickle(INTERIM_DATA_DIR/'Receita.pickle')
    
    atends_orientacao_expression = orientacao[orientacao['orientacao_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_retorno_medico_assinalado = orientacao[orientacao['retorno_medico_s']]['nr_atendimento'].unique().tolist()
    
    atends_atestado_expression = atestado[atestado['atestado_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_receita_expression = receita[receita['receita_contains_expression']]['nr_atendimento'].unique().tolist()
    
    base['Orientação de alta'] = base['nr_atendimento'].isin(atends_orientacao_expression)
    base['Retorno médico assinalado'] = base['nr_atendimento'].isin(atends_retorno_medico_assinalado)
    base['Atestado'] = base['nr_atendimento'].isin(atends_atestado_expression)
    base['Receita'] = base['nr_atendimento'].isin(atends_receita_expression)
    
    return base, orientacao, atestado, receita


def create_excel_file(df_main, df_orientacao, df_atestado, df_receita):
    print_with_time('Criando arquivo excel')
    fpath = get_excel_fpath()
    options = {'strings_to_formulas' : False, 
               'strings_to_urls' : False}
    writer = pd.ExcelWriter(fpath, engine='xlsxwriter', engine_kwargs={'options':options})
    workbook  = writer.book
    align = 'center'
    index_format = workbook.add_format({
        'text_wrap': True,
        'bold':True,
        'align': align,
        'valign': 'vcenter',
        'border':True
    })
    columns_format = workbook.add_format({
        'align': align
    })
    col_width = 17.4
       
    dfs_sheet_names = zip(
        generator_from_args(df_main, df_orientacao, df_atestado, df_receita),
        generator_from_args('Base', 'Orientações de Alta', 'Atestados', 'Receitas')
    )
    
    for _ in range(4):
        df_, sheet_name = next(dfs_sheet_names)
        if len(df_) == 0:
            print_with_time(f"AVISO: Planilha '{sheet_name}' está vazia")
            continue
        df_.to_excel(writer, sheet_name=sheet_name, index=False)
        colunas = df_.columns
        writer.sheets[sheet_name].set_column(0, len(colunas)-1, col_width, cell_format=columns_format)
        writer.sheets[sheet_name].autofilter(0, 0,  len(df_)-1, len(colunas)-1)
        for column_idx, column in enumerate(colunas):
            writer.sheets[sheet_name].write(0, column_idx, column, index_format)                
    writer.save()
    
    print_with_time('Arquivo excel criados com sucesso')


if __name__ == '__main__':
    df_base, df_orientacao, df_atestado, df_receita = gather_info_for_worksheets()
    create_excel_file(df_base, df_orientacao, df_atestado, df_receita)
