def create_telephone_columns(df_):
    for tipo in ['telefone', 'celular', 'fone_adic', 'celular_principal']:
        cols = [col for col in df_.columns if col.endswith(tipo)]
        df_[tipo+'_completo'] = '+ ' + df_[cols[0]].fillna('').astype(str) + ' (' + df_[cols[1]].fillna('').astype(str) + ') ' +\
            df_[cols[2]].fillna('').astype(str).str[:-4] + '-' + df_[cols[2]].fillna('').astype(str).str[-4:]
        df_.loc[df_[tipo+'_completo'].str.len() < 9, tipo+'_completo'] = ''
        df_[tipo+'_completo'] = df_[tipo+'_completo'].apply(lambda x: x.replace('+ 55 () -', '').replace('+  (', '('))
        df_.drop(cols, axis=1, inplace=True)
    return df_.copy()


def text_contains_any_expression(text, dataset_name):
    if type(text) != str:
        return False, 'NÃO'
    import re
    dataset_name = dataset_name.lower()
    
    all_expressions = [" solic(ito|itado|itada|it\.|\.)",  " ret(\.|orno|ornar)", " encam(\.|inho|inha)", " orient(\.|o|ad)",
                " (tomo| ct| tc)(\.|grafia| )", " ressonância|ressonancia| rm", " (ultrasso(m|nografia)|( usg| us)(\.| ))",
                " (endo(scopia|\.| )|eda)( |\.)", " colono(scopia|\.| )", " eco(cardiograma|\.| )",
                " tilt test", " pet(-|\.| )(ct|sca)"]
    if dataset_name in ['resumo de internação médica', 'avaliação médica pa template', 'evolução médica']:
        expressions = all_expressions
    elif dataset_name == 'receita':
        expressions = all_expressions[-8:]
    elif dataset_name == 'atestado':
        expressions = ["\( *x *\) *realização de exames"]
    else:
        raise ValueError(f"Nome do dataset fornecido ('{dataset_name}') não é válido")

    patterns = [re.compile(expression, re.IGNORECASE) for expression in expressions]
    text = "COMECO: " + text + " FIM"
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return True, match.group(0)     
    return False, 'NÃO'
    

def get_processed_excel_fpath():
    from src.definitions import PROCESSED_DATA_DIR
    start_day, end_day = get_start_and_end_day()
    fpath = PROCESSED_DATA_DIR/ f"Lista_de_Atendimentos_{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}.xlsx"
    return fpath


def get_processed_excel_fpath_custom(start_day, end_day):
    from src.definitions import PROCESSED_DATA_DIR
    from datetime import datetime
    start_day = datetime.strptime(start_day, "%d/%m/%Y")
    end_day = datetime.strptime(end_day, "%d/%m/%Y")
    fpath = PROCESSED_DATA_DIR/ f"Lista_de_Atendimentos_{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}.xlsx"
    return fpath


def delete_week_file():
    from os import remove as os_remove
    fpath = get_processed_excel_fpath()
    return os_remove(fpath)
    
    
def get_start_and_end_day():
    from datetime import datetime, timedelta
    today = datetime.today()
    end_day = today - timedelta(days=1)
    start_day = today - timedelta(days=7) 
    return start_day, end_day


def generator_from_args(*args):
    for arg in args:
        yield arg


def my_rtf_to_text(rtf):
    if 'rtf' not in rtf:
        return rtf
    from striprtf.striprtf import rtf_to_text
    return rtf_to_text(rtf, errors='ignore')

   
def apply_rtf_and_bold_expression(text, all_expressions):
    if not isinstance(text, str):
        return text
    expression_found = False
    new_text = """{\\rtf1 {\\colortbl;\\red0\\green0\\blue0;\\red255\\green0\\blue0;}""" + text + "}"
    for expression in all_expressions:
        if (expression == 'NÃO') or ('?' in expression) or ('suspeita' in expression):
            continue
        if expression in new_text:
            new_text = new_text.replace(expression, f"\\cf2\\b {expression}\\b0\\cf ")
            expression_found = True
    return new_text if expression_found else text
    
