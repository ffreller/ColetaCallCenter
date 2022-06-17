import pandas as pd
from src.definitions import INTERIM_DATA_DIR, LOGGING_CONFIG
from src.helper_functions import get_processed_excel_fpath, get_processed_excel_fpath_custom,\
    generator_from_args, apply_rtf_and_bold_expression
import logging
import logging.config


 
def gather_info_for_worksheets():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('standard')
    logger.debug('Agrupando informações para as planilhas')
    # Lendo os datsets
    base = pd.read_pickle(INTERIM_DATA_DIR/'Base.pickle')
    resumo_internacao = pd.read_pickle(INTERIM_DATA_DIR/'Resumo_De_Internação_Médica.pickle')
    atestado = pd.read_pickle(INTERIM_DATA_DIR/'Atestado.pickle')
    receita = pd.read_pickle(INTERIM_DATA_DIR/'Receita.pickle')
    
    atends_resumo_internacao_expression = resumo_internacao[resumo_internacao['resumo_internacao_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_retorno_medico_assinalado = resumo_internacao[resumo_internacao['retorno_medico_s']]['nr_atendimento'].unique().tolist()
    
    atends_atestado_expression = atestado[atestado['atestado_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_receita_expression = receita[receita['receita_contains_expression']]['nr_atendimento'].unique().tolist()
    
    base['Palavras chave no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_resumo_internacao_expression)
    base['Retorno médico assinalado no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_retorno_medico_assinalado)
    base['Palavras chave no Atestado'] = base['nr_atendimento'].isin(atends_atestado_expression)
    base['Palavras chave na Receita'] = base['nr_atendimento'].isin(atends_receita_expression)
    
    #Filtrando dataset
    base = base[base.iloc[:, -4:].any(axis=1)]
    
    all_expressions = set(list(resumo_internacao.iloc[:, -1].unique()) + \
        list(atestado.iloc[:, -1].unique()) + list(receita.iloc[:, -1].unique())
    )
    for df_, text_column in [
        (resumo_internacao, 'resumo_internacao'),
        (atestado, 'atestado'),
        (receita, 'receita')
        ]:

        df_[text_column] = df_[text_column].apply(lambda x: apply_rtf_and_bold_expression(x, all_expressions))
    
    return base, resumo_internacao, atestado, receita


def gather_info_for_base():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('standard')
    logger.debug('Agrupando informaçõe para a planilha base')
    # Lendo os datsets
    base = pd.read_pickle(INTERIM_DATA_DIR/'Base.pickle')
    resumo_internacao = pd.read_pickle(INTERIM_DATA_DIR/'Resumo_De_Internação_Médica.pickle')
    atestado = pd.read_pickle(INTERIM_DATA_DIR/'Atestado.pickle')
    receita = pd.read_pickle(INTERIM_DATA_DIR/'Receita.pickle')
    
    atends_resumo_internacao_expression = resumo_internacao[resumo_internacao['resumo_internacao_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_retorno_medico_assinalado = resumo_internacao[resumo_internacao['retorno_medico_s']]['nr_atendimento'].unique().tolist()
    
    atends_atestado_expression = atestado[atestado['atestado_contains_expression']]['nr_atendimento'].unique().tolist()
    atends_receita_expression = receita[receita['receita_contains_expression']]['nr_atendimento'].unique().tolist()
    
    base['Palavras chave no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_resumo_internacao_expression)
    base['Retorno médico assinalado no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_retorno_medico_assinalado)
    base['Palavras chave no Atestado'] = base['nr_atendimento'].isin(atends_atestado_expression)
    base['Palavras chave na Receita'] = base['nr_atendimento'].isin(atends_receita_expression)
    
    #Filtrando dataset
    base = base[base.iloc[:, -4:].any(axis=1)]
    return base


def create_excel_file(df_main, df_resumo_internacao, df_atestado, df_receita):
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('standard')
    logger.debug('Criando arquivo excel')
    fpath = get_processed_excel_fpath()
    # fpath = get_processed_excel_fpath_custom('14/06/2021', '14/01/2022')
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
        generator_from_args(df_main, df_resumo_internacao, df_atestado, df_receita),
        generator_from_args('Base', 'Resumo de Internação Médica', 'Atestados', 'Receitas')
    )
    
    for _ in range(4):
        df_, sheet_name = next(dfs_sheet_names)
        if len(df_) == 0:
            logger.debug(f"AVISO: Planilha '{sheet_name}' está vazia")
            continue
        df_.to_excel(writer, sheet_name=sheet_name, index=False)
        colunas = df_.columns
        writer.sheets[sheet_name].set_column(0, len(colunas)-1, col_width, cell_format=columns_format)
        writer.sheets[sheet_name].autofilter(0, 0,  len(df_)-1, len(colunas)-1)
        for column_idx, column in enumerate(colunas):
            writer.sheets[sheet_name].write(0, column_idx, column, index_format)                
    writer.save()
    
    logger.debug('Arquivo excel criado com sucesso.')
    
    
    
def create_excel_file_only_base(df_main):
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('standard')
    logger.debug('Criando arquivo excel')
    fpath = get_processed_excel_fpath()
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
       
    sheet_name = "Base"
    if len(df_main) == 0:
        logger.warning(f"Planilha '{sheet_name}' está vazia")
        return
    df_main.to_excel(writer, sheet_name=sheet_name, index=False)
    colunas = df_main.columns
    writer.sheets[sheet_name].set_column(0, len(colunas)-1, col_width, cell_format=columns_format)
    writer.sheets[sheet_name].autofilter(0, 0,  len(df_main)-1, len(colunas)-1)
    for column_idx, column in enumerate(colunas):
        writer.sheets[sheet_name].write(0, column_idx, column, index_format)                
    writer.save()
    
    logger.debug(f"Arquivo excel 'Base' criado com sucesso: {len(df_main)} linhas.")
