from matplotlib.pyplot import axis
import pandas as pd
from src.helper_functions import print_with_time, crate_telephone_columns, create_expression_columns
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


def preprocess_orientacao():
    print_with_time('Processando orientações de alta')
    # Lendo o dataset
    fname = 'Orientação_De_Alta.pickle'
    df0 = pd.read_pickle(RAW_DATA_DIR/fname)
    
    df0.loc[ (df0['ds_label'] == 'Retorno médico em') & (df0['ds_resultado'] == 'S'), 'retorno_medico_s'] = True
    df0['retorno_medico_s'].fillna(False, inplace=True)
    
    text_column = 'ds_resultado'
    new_text_column = 'orientacao'
    df0.rename(columns={text_column: new_text_column}, inplace=True)
    df1 = create_expression_columns(df0, new_text_column)
    df1.to_pickle(INTERIM_DATA_DIR/fname)
    
    print_with_time('Sucesso ao processar orientações de alta')
    

def preprocess_atestado_receita(dataset_target):
    if 'receita' in dataset_target.lower():
        fname = 'Receita.pickle'
        text_column = 'ds_receita'
    elif 'atestado' in dataset_target.lower():
        fname = 'Atestado.pickle'
        text_column = 'ds_atestado'
    else:
        raise ValueError('Nome do dateset target não contém palavra "receita" ou "atestado"')
    new_text_column = text_column.split('_')[1]
    print_with_time(f'Processando {new_text_column}s')
    df0 = pd.read_pickle(RAW_DATA_DIR/fname)
    
    df0[new_text_column] = df0[text_column].apply(strip_html_tags)
    df1 = create_expression_columns(df0, new_text_column)
    df1.drop(text_column, axis=1, inplace=True)
    df1.to_pickle(INTERIM_DATA_DIR/fname)
    print_with_time(f'Sucesso ao processar {new_text_column}s')
        
    
if __name__ == '__main__':
    preprocess_base()
    preprocess_orientacao()
    preprocess_atestado_receita('atestado')
    preprocess_atestado_receita('receita')