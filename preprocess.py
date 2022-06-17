from matplotlib.pyplot import axis
import pandas as pd
from src.helper_functions import my_rtf_to_text, print_with_time, crate_telephone_columns, text_contains_any_expression
from src.HTMLStripper import strip_html_tags
from src.definitions import RAW_DATA_DIR, INTERIM_DATA_DIR


def preprocess_base():
    print_with_time('Processando dataset base')
    # Lendo o dataset
    fname = 'Baskle'
    base = pd.read_pickle(RAW_DATA_DIR/fname)
    # Criar coluna com telefone completo
    base2 = crate_telephone_columns(base)
    base2 = base2[base2['ds_tipo_atendimento'] == 'Internado']
    colunas = ['nr_atendimento', 'dt_nascimento', 'nm_social', 'nm_pessoa_fisica', 'dt_entrada', 'dt_alta', 'ds_motivo_alta', 'ds_email',
                'ds_mala_direta', 'ds_classif_setor', 'dt_agenda_consulta', 'dt_agenda_exame','telefone_completo', 'celular_principal_completo',
                'celular_completo', 'fone_adic_completo']
    
    # Salvar dataset criado
    base2[colunas].to_pickle(INTERIM_DATA_DIR/fname)
    print_with_time(f'Sucesso ao processar dataset base: {len(base2)} linhas')

    
def preprocess_secondary_table(dataset_name):
    dataset_name = dataset_name.title()
    print_with_time(f"Processando dataset '{dataset_name}'")
    fname = dataset_name.replace(' ', '_') +'.pickle'
    df0 = pd.read_pickle(RAW_DATA_DIR/fname)
    
    datasets_to_process_differently = ['resumo de internação médica', 'avaliação médica pa template']
    
    text_col_name = 'ds_resultado' if dataset_name.lower() in datasets_to_process_differently\
        else "ds_"+dataset_name.split(' ')[0].lower()
    new_text_col_name = 'resumo_internacao' if dataset_name.lower() == 'resumo de internação médica'\
        else 'resumo_avaliacao' if dataset_name.lower() == 'avaliação médica pa template'\
        else text_col_name.split('_')[1]
    
    if dataset_name.lower() in datasets_to_process_differently:
        df0.rename(columns={text_col_name: new_text_col_name}, inplace=True)
        if dataset_name.lower() == 'resumo de internação médica':
            df0.loc[(df0['ds_label'] == 'Retorno médico em') & (df0[new_text_col_name] == 'S'), 'retorno_medico_s'] = True
            df0['retorno_medico_s'].fillna(False, inplace=True)
    else:
        df0[new_text_col_name] = df0[text_col_name].apply(strip_html_tags)
        df0[new_text_col_name] = df0[new_text_col_name].apply(my_rtf_to_text)
        df0.drop(text_col_name, axis=1, inplace=True)
    
    df0[[new_text_col_name+'_contains_expression', new_text_col_name+'_expression']] =\
        df0.apply(lambda x: text_contains_any_expression(x[new_text_col_name], dataset_name=dataset_name), axis=1, result_type="expand")
    df0.to_pickle(INTERIM_DATA_DIR/fname)
    print_with_time(f"Sucesso ao processar dataset '{dataset_name}': {len(df0)} linhas" )
        
    
if __name__ == '__main__':
    preprocess_base()
    preprocess_secondary_table(dataset_name='resumo de internação médica')
    preprocess_secondary_table(dataset_name='atestado')
    preprocess_secondary_table(dataset_name='evolução médica')
    preprocess_secondary_table(dataset_name='avaliação médica pa template')
    
