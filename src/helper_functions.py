def crate_telephone_columns(df_):
    for tipo in ['telefone', 'celular', 'fone_adic', 'celular_principal']:
        cols = [col for col in df_.columns if col.endswith(tipo)]
        df_[tipo+'_completo'] = '+ ' + df_[cols[0]].fillna('').astype(str) + ' (' + df_[cols[1]].fillna('').astype(str) + ') ' +\
            df_[cols[2]].fillna('').astype(str).str[:-4] + '-' + df_[cols[2]].fillna('').astype(str).str[-4:]
        df_.loc[df_[tipo+'_completo'].str.len() < 9, tipo+'_completo'] = ''
        df_[tipo+'_completo'] = df_[tipo+'_completo'].apply(lambda x: x.replace('+ 55 () -', '').replace('+  (', '('))
        df_.drop(cols, axis=1, inplace=True)
    colunas = ['nr_atendimento', 'dt_nascimento', 'nm_social', 'nm_pessoa_fisica', 'dt_entrada', 'dt_alta', 'ds_motivo_alta', 'ds_email',
               'ds_mala_direta', 'ds_classif_setor', 'dt_agenda_consulta', 'ds_status_agenda_consulta', 'ds_tipo_agenda_consulta', 'dt_agenda_exame',
               'ds_status_agenda_exame', 'ds_procedimento', 'telefone_completo', 'celular_principal_completo', 'celular_completo', 'fone_adic_completo']
    return df_[colunas].copy()


def text_contains_any_expression(text, dataset_name):
    if type(text) != str:
        return False, 'NÃO'
    import re
    dataset_name = dataset_name.lower()
    
    all_expressions = [" solic(ito|itado|itada|it\.|\.)",  " ret(\.|orno|ornar)", " encam(\.|inho|inha)", " orient(\.|o|ad)",
                " (tomo| ct| tc)(\.|grafia| )", " ressonância|ressonancia| rm", " (ultrasso(m|nografia)|( usg| us)(\.| ))",
                " (endo(scopia|\.| )|eda)( |\.)", " colono(scopia|\.| )", " eco(cardiograma|\.| )",
                " tilt test", " pet(-|\.| )(ct|sca)"]
    if dataset_name == 'resumo de internação médica':
        expressions = all_expressions
    elif dataset_name == 'receita':
        expressions = all_expressions[-8:]
    elif dataset_name == 'atestado':
        expressions = ["\( *x *\) *realização de exames"]
    else:
        raise ValueError(f"Nome do dataset ({dataset_name}) fornecido não é válido")

    patterns = [re.compile(expression, re.IGNORECASE) for expression in expressions]
    text = "COMECO: " + text + " FIM"
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return True, match.group(0)     
    return False, 'NÃO'


def print_with_time(txt):
    from datetime import datetime
    agora = datetime.now()
    print(f"{agora.strftime('%d/%m/%Y %H:%M:%S')} - {txt}")
    

def get_processed_excel_fpath():
    from src.definitions import PROCESSED_DATA_DIR
    start_day, end_day = get_start_and_end_day()
    fpath = PROCESSED_DATA_DIR/ f"{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}_callcenter.xlsx"
    return fpath


def get_processed_excel_fpath_custom(start_day, end_day):
    from src.definitions import PROCESSED_DATA_DIR
    from datetime import datetime
    start_day = datetime.strptime(start_day, "%d/%m/%Y")
    end_day = datetime.strptime(end_day, "%d/%m/%Y")
    fpath = PROCESSED_DATA_DIR/ f"{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}_callcenter.xlsx"
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
    
