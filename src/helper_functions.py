def crate_telephone_columns(df_):
    for tipo in ['telefone', 'celular', 'fone_adic']:
        cols = [col for col in df_.columns if col.endswith(tipo)]
        df_[tipo+'_completo'] = '+ ' + df_[cols[0]].fillna('').astype(str) + ' (' + df_[cols[1]].fillna('').astype(str) + ') ' +\
            df_[cols[2]].fillna('').astype(str).str[:-4] + '-' + df_[cols[2]].fillna('').astype(str).str[-4:]
        df_.loc[df_[tipo+'_completo'].str.len() < 9, tipo+'_completo'] = ''
        df_[tipo+'_completo'] = df_[tipo+'_completo'].apply(lambda x: x.replace('+ 55 () -', '').replace('+  (', '('))
        df_.drop(cols, axis=1, inplace=True)
    colunas = list(df_.columns)
    assert colunas[-3] == 'telefone_completo',\
        print('Erro ao criar colunas de telefone: ordem das colunas não é a esperada')
    colunas.remove('nr_ramal')
    colunas.insert(-2, 'nr_ramal')
    return df_[colunas].copy()


def text_contains_any_expression(text):
    if type(text) != str:
        return False, 'NÃO'
    import re
    expressions = [" solic(ito|itado|itada|it\.|\.)",  " ret(\.|orno|ornar)", " encam(\.|inho|inha)", " orient(\.|o|ad)",
            " (tomo| ct| tc)(\.|grafia| )", " ressonância|ressonancia| rm", " (ultrasso(m|nografia)|( usg| us)(\.| ))",
            " (endo(scopia|\.| )|eda)( |\.)", " colono(scopia|\.| )", " eco(cardiograma|\.| )",
            " tilt test", " pet(-|\.| )(ct|sca)"]
    patterns = [re.compile(expression) for expression in expressions]
    text = "comeo " + text + "."
    for pattern in patterns:
        match = pattern.search(text, re.IGNORECASE)
        if match:
            return True, match.group(0)     
    return False, 'NÃO'


def print_with_time(txt):
    from datetime import datetime
    agora = datetime.now()
    print(f"{agora.strftime('%d/%m/%Y %H:%M:%S')} - {txt}")
    

def get_excel_fpath():
    from src.definitions import PROCESSED_DATA_DIR
    start_day, end_day = get_start_and_end_day()
    fpath = PROCESSED_DATA_DIR/ f"{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}_callcenter.xlsx"
    return fpath


def delete_week_file():
    from os import remove as os_remove
    fpath = get_excel_fpath()
    os_remove(fpath)
    
    
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
    found_expression = False
    if type(text) != str or len(text) <= 30:
        return text
    new_text = """{\\rtf1 {\\colortbl;\\red0\\green0\\blue0;\\red255\\green0\\blue0;}""" + text + "}"
    for expression in all_expressions:
        if expression == 'NÃO':
            continue
        if expression in new_text:
            new_text = new_text.replace(expression, f"\\b {expression} \\b0")
            found_expression = True
        elif expression.capitalize() in new_text:
            new_text = new_text.replace(expression.capitalize(), f"\\b {expression.capitalize()} \\b0")
            found_expression = True
        
        new_text = new_text.replace('\\b ', '\\cf2\\b ')
        new_text = new_text.replace(' \\b0', ' \\b0\\cf')
    return new_text if found_expression else text
    
