from matplotlib.pyplot import axis
import pandas as pd
from src.helper_functions import my_rtf_to_text, print_with_time, crate_telephone_columns, text_contains_any_expression
from src.HTMLStripper import strip_html_tags
from src.definitions import RAW_DATA_DIR, INTERIM_DATA_DIR


def preprocess_base():
    print_with_time('Processando dataset base')
    # Lendo o dataset
    fname = 'Base.pickle'
    base = pd.read_pickle(RAW_DATA_DIR/fname)
    # Criar coluna com telefone completo
    base2 = crate_telephone_columns(base)
    # Salvar dataset criado
    base2.to_pickle(INTERIM_DATA_DIR/fname)
    print_with_time('Sucesso ao processar dataset base')

    
def preprocess_secondary_table(dataset_name):
    dataset_name = dataset_name.title()
    print_with_time(f"Processando dataset '{dataset_name}'")
    text_col_name = "ds_"+dataset_name.lower()
    fname = dataset_name.replace(' ', '_') +'.pickle'
    df0 = pd.read_pickle(RAW_DATA_DIR/fname)
    
    if dataset_name.lower() == 'resumo de internação médica':
        old_col_name = 'ds_resultado'
        new_text_col_name = 'resumo_internacao'
        df0.rename(columns={old_col_name: new_text_col_name}, inplace=True)

        df0.loc[ (df0['ds_label'] == 'Retorno médico em') & (df0[new_text_col_name] == 'S'), 'retorno_medico_s'] = True
        df0['retorno_medico_s'].fillna(False, inplace=True)
    else:
        new_text_col_name = text_col_name.split('_')[1]
        df0[new_text_col_name] = df0[text_col_name].apply(strip_html_tags)
        df0[new_text_col_name] = df0[new_text_col_name].apply(my_rtf_to_text)
        df0.drop(text_col_name, axis=1, inplace=True)
        
    df0[[new_text_col_name+'_contains_expression', new_text_col_name+'_expression']] =\
        df0.apply(lambda x: text_contains_any_expression(x[new_text_col_name]), axis=1, result_type="expand")
    df0.to_pickle(INTERIM_DATA_DIR/fname)
    print_with_time(f"Sucesso ao processar dataset '{dataset_name}'")
        
    
if __name__ == '__main__':
    preprocess_base()
    preprocess_secondary_table(dataset_name='resumo de internação médica')
    preprocess_secondary_table(dataset_name='atestado')
    preprocess_secondary_table(dataset_name='receita')
