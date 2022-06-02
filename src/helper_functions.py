import pandas as pd
import re
from os import remove as os_remove
from io import StringIO
from html.parser import HTMLParser
from datetime import datetime, timedelta
from striprtf.striprtf import rtf_to_text
from src.definitions import PROCESSED_DATA_DIR


def campo_sepse_med(text):
    if type(text) == str:
        if "Sepse :" in text:
            trecho = text[text.find("Sepse :")+len("Sepse :")+2: text.find("Sepse :")+12]
            if trecho.lower() == 'sim':
                return True
    return False


def remove_campo_sepse_from_text_med(text):
    if type(text) == str:
        if "Sepse :" in text:
            new = text.replace('Sepse :', '')
            return new
    return text


pattern_antecedentes = re.compile('Antecedentes ?:')
def remove_antecedentes_from_text(text):
    if type(text) == str:
        match = pattern_antecedentes.search(text)
        if match:
            before_antecedentes = text[:match.start()]
            if 'Tabagismo' in text:
                after_tabagismo = text[text.find('Tabagismo'):]
                new = before_antecedentes + after_tabagismo
                return new
            return text
    return text


key_words_pattern_sepse = re.compile('choque *(s(e|é)ptico|refrat(a|á)rio|misto)|seps(e|is)|septicemia')
key_words_pattern_sepse_meio = re.compile('(choque *(s(e|é)ptico|refrat(a|á)rio|misto) *\?|seps(e|is) *\?|septicemia *\?)|(suspeita *de *choque *(s(e|é)ptico|refrat(a|á)rio|misto)|suspeita *de *seps(e|is)|suspeita *de *septicemia)')
def text_contains_sepse_expression(text):
    if type(text) == str:
        if 'paciente comparece para biopsia de prostata' not in text.lower().replace('ó', 'o'):
            match = key_words_pattern_sepse.search(text, re.IGNORECASE)
            if match:
                match_meio = key_words_pattern_sepse_meio.search(text, re.IGNORECASE)
                if match_meio:
                    return 0.5
                return 1       
    return 0


def text_contains_sepse_expression_with_text(text):
    if type(text) == str:
        if 'paciente comparece para biopsia de prostata' not in text.lower().replace('ó', 'o'):
            match = key_words_pattern_sepse.search(text, re.IGNORECASE)
            if match:
                match_meio = key_words_pattern_sepse_meio.search(text, re.IGNORECASE)
                if match_meio:
                    return match_meio.group(0)
                return match.group(0)       
    return 'NÃO'


key_words_pattern_paliativo = re.compile('cuidados? paliativos?')
key_words_patter_paliativo_ignorar = re.compile('cuidados paliativos *: * (sem limitação de suporte orgânico invasivo)|não')
def text_contains_cuidados_paliativos(text):
    if type(text) == str:
        match = key_words_pattern_paliativo.search(text.lower())
        if match:
            match_ignorar = key_words_patter_paliativo_ignorar.search(text.lower())
            if not match_ignorar:
                return True       
    return False


def text_contains_codigo_amarelo(text):
    if type(text) == str:
        if 'código amarelo/avaliação clínica' in text[:50].lower():
            return True       
    return False


def get_time_between_evolucao_med_com_sepse(df__):
    df_ = df__.copy()
    df_['tempo_entre_evolucao_med_com_sepse'] = df_['DT_EVOLUCAO_MED'].diff()
    df_.loc[df_['NR_ATENDIMENTO'].diff() != 0, 'tempo_entre_evolucao_med_com_sepse'] = float('nan')
    df_['tempo_entre_evolucao_med_com_sepse>72'] = df_['tempo_entre_evolucao_med_com_sepse'] > pd.Timedelta(days=3)
    return df_[['tempo_entre_evolucao_med_com_sepse', 'tempo_entre_evolucao_med_com_sepse>72']].copy()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_html_tags(html):
    if '<html tasy=' in html:
        s = MLStripper()
        s.feed(html)
        return s.get_data()
    return html


def my_rtf_to_text(rtf):
    return rtf_to_text(rtf, errors='ignore')


def print_with_time(txt):
    agora = datetime.now()
    print(f"{agora.strftime('%d/%m/%Y %H:%M:%S')} - {txt}")
    
    
def apply_rtf_and_bold_expression(text, all_expressions):
    new_text = """{\\rtf1 {\\colortbl;\\red0\\green0\\blue0;\\red255\\green0\\blue0;}""" + text + "}"
    for expression in all_expressions:
        if expression == 'NÃO' or '?' in expression or 'suspeita' in expression:
            continue
        if expression in new_text:
            new_text = new_text.replace(expression, f"\\b {expression} \\b0")
        elif expression.capitalize() in new_text:
            new_text = new_text.replace(expression.capitalize(), f"\\b {expression.capitalize()} \\b0")
        else:
            new_text = new_text.replace(expression.title(), f"\\b {expression.title()} \\b0")
        
        new_text = new_text.replace('\\b ', '\\cf2\\b ')
        new_text = new_text.replace(' \\b0', ' \\b0\\cf')
    return new_text 


def get_excel_fpath():
    start_day, end_day = get_start_and_end_day()
    fpath = PROCESSED_DATA_DIR/ f"{start_day.strftime('%d/%m/%Y')}_{end_day.strftime('%d/%m/%Y')}_callcenter.xlsx"
    return fpath


def delete_week_file():
    fpath = get_excel_fpath()
    os_remove(fpath)
    
    
def get_start_and_end_day():
    today = datetime.today()
    end_day = today - timedelta(days=1)
    start_day = today - timedelta(days=7) 
    return start_day, end_day
    
