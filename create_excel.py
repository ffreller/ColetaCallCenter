def gather_info_for_worksheets(only_base):
    from pandas import read_pickle
    from src.helper_functions import apply_rtf_and_bold_expression, generator_from_args
    from src.definitions import INTERIM_DATA_DIR
    from logging import getLogger
    
    logger = getLogger('standard')
    
    # Lendo os datsets
    base = read_pickle(INTERIM_DATA_DIR/'Base.pickle')
    resumo_internacao = read_pickle(INTERIM_DATA_DIR/'Resumo_De_Internação_Médica.pickle')
    atestado = read_pickle(INTERIM_DATA_DIR/'Atestado.pickle')
    receita = read_pickle(INTERIM_DATA_DIR/'Receita.pickle')
    evolucao = read_pickle(INTERIM_DATA_DIR/'Evolução_Médica.pickle')
    avaliacao_pa = read_pickle(INTERIM_DATA_DIR/'Avaliação_Médica_Pa_Template.pickle')
    
    atends_resumo_internacao_expression = resumo_internacao[resumo_internacao['resumo_internação_contains_expression']]['nr_atendimento'].unique().tolist()
    if not atends_resumo_internacao_expression:
        logger.warning('Nenhum atendimento com expressão relevante no resumo de internação')
        
    atends_retorno_medico_assinalado = resumo_internacao[resumo_internacao['retorno_medico_s']]['nr_atendimento'].unique().tolist()
    if not atends_retorno_medico_assinalado:
        logger.warning('Nenhum atendimento com retorno médico assinalado')
        
    atends_atestado_expression = atestado[atestado['atestado_contains_expression']]['nr_atendimento'].unique().tolist()
    if not atends_atestado_expression:
        logger.warning('Nenhum atendimento com expressão relevante no atestado')
        
    atends_receita_expression = receita[receita['receita_contains_expression']]['nr_atendimento'].unique().tolist()
    if not atends_receita_expression:
        logger.warning('Nenhum atendimento com expressão relevante na receita')
        
    atends_evolucao_expression = evolucao[evolucao['evolução_contains_expression']]['nr_atendimento'].unique().tolist()
    if not atends_evolucao_expression:
        logger.warning('Nenhum atendimento com expressão relevante na evolução médica')
        
    atends_avaliacao_pa_expression = avaliacao_pa[avaliacao_pa['resumo_avaliação_contains_expression']]['nr_atendimento'].unique().tolist()
    if not atends_avaliacao_pa_expression:
        logger.warning('Nenhum atendimento com expressão relevante na avaliação médica no PA')
    
    base['Palavras chave no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_resumo_internacao_expression)
    base['Retorno médico assinalado no Resumo de internação médica'] = base['nr_atendimento'].isin(atends_retorno_medico_assinalado)
    base['Palavras chave no Atestado'] = base['nr_atendimento'].isin(atends_atestado_expression)
    base['Palavras chave na Receita'] = base['nr_atendimento'].isin(atends_receita_expression)
    base['Palavras chave na Evolução Médica'] = base['nr_atendimento'].isin(atends_evolucao_expression)
    base['Palavras chave na Avaliação Médica do PA'] = base['nr_atendimento'].isin(atends_avaliacao_pa_expression)
    
    #Filtrando dataset
    base = base[base.iloc[:, -6:].any(axis=1)]
    
    if only_base:
        return base
    
    all_expressions = set(list(resumo_internacao.iloc[:, -1].unique()) + \
        list(atestado.iloc[:, -1].unique()) + list(receita.iloc[:, -1].unique())
    )
    
    # Generator para percorrer os datasets
    dfs_text_columns = zip(
        generator_from_args(resumo_internacao, atestado, receita, evolucao, avaliacao_pa),
        generator_from_args('resumo_internação', 'atestado', 'receita', 'evolução', 'resumo_avaliação'),
    )
    
    for df_, text_column in dfs_text_columns:
        #Aplicando RTF e destacando visualmente expressão na coluna com o texto.
        df_[text_column] = df_[text_column].apply(lambda x: apply_rtf_and_bold_expression(x, all_expressions))
        
    logger.debug('Sucesso ao agrupar informações para as planilhas')
    
    return base, resumo_internacao, atestado, receita, evolucao, avaliacao_pa


def append_df_to_excel_workbook_sheet(writer, df, sheet_name, index_format, columns_format, col_width):
    from logging import getLogger
    
    logger = getLogger('standard')
    if df.empty:
        logger.warning(f"Planilha '{sheet_name}' está vazia")
        return writer
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    colunas = df.columns
    writer.sheets[sheet_name].set_column(0, len(colunas)-1, col_width, cell_format=columns_format)
    writer.sheets[sheet_name].autofilter(0, 0,  len(df.index)-1, len(colunas)-1)
    for column_idx, column in enumerate(colunas):
        writer.sheets[sheet_name].write(0, column_idx, column, index_format)
    return writer


def create_excel_file(df_main, only_base, df_resumo_internacao=None, df_atestado=None, df_receita=None, df_evolucao=None, df_avaliacao_pa=None):
    from logging import getLogger
    from pandas import ExcelWriter
    from src.helper_functions import get_processed_excel_fpath, get_processed_excel_fpath_custom, generator_from_args

    logger = getLogger('standard')
    
    if not only_base:
        assert df_resumo_internacao is not None, "Dataset 'resumo de internação' não foi passado"
        assert df_receita is not None, "Dataset 'receita' não foi passado"
        assert df_atestado is not None, "Dataset 'atestado' não foi passado"
        assert df_evolucao is not None, "Dataset 'evolução médica' não foi passado"
        assert df_avaliacao_pa is not None, "Dataset 'avaliação médica no PA' não foi passado como argumento"
        
    fpath = get_processed_excel_fpath()
    # fpath = get_processed_excel_fpath_custom('14/06/2021', '14/01/2022')
    
    #Cofngiruações da planilha excel
    options = {'strings_to_formulas' : False, 
               'strings_to_urls' : False}
    writer = ExcelWriter(fpath, engine='xlsxwriter', engine_kwargs={'options':options})
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

    # Generator para percorrer os datasets
    dfs_sheet_names = zip(
        generator_from_args(df_main, df_resumo_internacao, df_atestado, df_receita, df_evolucao, df_avaliacao_pa),
        generator_from_args('Base', 'Resumo de Internação Médica', 'Atestados', 'Receitas', 'Evolução Médica', 'Avaliação Médica no PA')
    )
        
    for df_, sheet_name in dfs_sheet_names:
        # Se dataframe for nulo, script pára o laço for. (Só deve ser registrado o dataset base) 
        if df_ is None:
            break
        # Se dataframe não for nulo, script o anexa à planilha          
        writer = append_df_to_excel_workbook_sheet(writer, df_, sheet_name, index_format, columns_format, col_width)
            
    writer.save()
    logger.debug('Arquivo excel criado com sucesso. Base tem %s linhas' % len(df_main.index))
