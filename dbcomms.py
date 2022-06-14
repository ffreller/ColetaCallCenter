
import pandas as pd
from base64 import b64decode
import re
import cx_Oracle
from datetime import datetime
from sqlalchemy import create_engine
from src.helper_functions import print_with_time, get_start_and_end_day
from src.definitions import RAW_DATA_DIR
from credentials import USUARIO_PROD, SENHA_PROD, USUARIO_TESTE, SENHA_TESTE


# Cria engine do sqlalchemy
def create_sqlalchemy_engine(db_tns):
    if db_tns.lower() == 'odi':
        usuario = b64decode(USUARIO_PROD).decode("utf-8")
        senha = b64decode(SENHA_PROD).decode("utf-8")
        vDB_TNS = "DB_ODI_PROD"
    elif db_tns.lower() == 'test':
        usuario = b64decode(USUARIO_TESTE).decode("utf-8")
        senha = b64decode(SENHA_TESTE).decode("utf-8")
        vDB_TNS = "DBTESTE1"
    elif db_tns.lower() == 'tasy':
        usuario = b64decode(USUARIO_PROD).decode("utf-8")
        senha = b64decode(SENHA_PROD).decode("utf-8")
        vDB_TNS = "HAOC_TASY_PROD"
    else:
        print("O argumento db_tns precisa ser igual a 'test', 'tasy' ou 'odi'")
        return None
    conn = create_engine(f'oracle+cx_oracle://{usuario}:{senha}@{vDB_TNS}')
    return conn


#Cria conexão via cxOracle
def create_conn_cxOracle(db_tns):
    if db_tns.lower() == 'odi':
        usuario = b64decode(USUARIO_PROD).decode("utf-8")
        senha = b64decode(SENHA_PROD).decode("utf-8")
        vDB_TNS = "DB_ODI_PROD"
    elif db_tns.lower() == 'test':
        usuario = b64decode(USUARIO_TESTE).decode("utf-8")
        senha = b64decode(SENHA_TESTE).decode("utf-8")
        vDB_TNS = "DBTESTE1"
    elif db_tns.lower() == 'tasy':
        usuario = b64decode(USUARIO_PROD).decode("utf-8")
        senha = b64decode(SENHA_PROD).decode("utf-8")
        vDB_TNS = "HAOC_TASY_PROD"
    conn = cx_Oracle.connect(user=usuario, password=senha, dsn=vDB_TNS)
    return conn


# Executa query via pandas e sqlalchemy
def execute_query_pandas(query, conn):
    df = pd.read_sql(query, conn)
    return df


# Executa query via cxOracle e carrega dados para dataframe
def execute_query_cxOracle_and_load_to_df(query, conn, columns):
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    return df


# Lë queries presentes em arquivo .sql e separadas por comentários
def read_queries_from_file(fpath=None):
    if not fpath:
        fpath = 'data/sql_queries_callcenter.sql'
    with open(fpath, 'r') as f:
        sqlFile = f.read()
    query_names = re.findall('-- (.*)', sqlFile)
    queries = re.split('--.*', sqlFile)[1:]
    dict_queries = dict(zip(query_names, queries))
    return dict_queries


# Script para baixar dados do HAOC_TASY_PROD
def retrieve_data_from_dbtasy_using_dates(start_date, end_date):
    start_date = start_date.strftime('%d/%m/%Y')
    end_date = end_date.strftime('%d/%m/%Y')
    print_with_time(f"Baixando dados do DB_TASY: De {start_date} até {end_date}")
    queries = read_queries_from_file()
    sqlalchemy_engine = create_sqlalchemy_engine(db_tns='tasy')
    conn_cxOracle = create_conn_cxOracle(db_tns='tasy')
    tabelas_cx_Oracle = ['Atestado', 'Receita']
    success = True
    for query_name in queries.keys():
        query = queries[query_name]
        query = query.replace('DATE_TO_REPLACE_START', start_date).replace('DATE_TO_REPLACE_END', end_date)
        try:
            if query_name not in tabelas_cx_Oracle:
                df = execute_query_pandas(query, sqlalchemy_engine)
            else:
                columns = ['nr_atendimento', f'dt_{query_name.lower()}', 'dt_liberacao', f'ds_{query_name.lower()}']
                df = execute_query_cxOracle_and_load_to_df(query, conn_cxOracle, columns=columns)
        except Exception as e:
            print_with_time(f'Erro ao excecutar query {query_name.title()}: ' + str(e))
            success = False
        if success:
            print_with_time(f"Query '{query_name.title()}' executada com sucesso")
            df.to_pickle(RAW_DATA_DIR/f"{query_name.title().replace(' ', '_')}.pickle")
    sqlalchemy_engine.dispose()
    conn_cxOracle.close()
    return success


# Script para baixar dados do mês passado HAOC_TASY_PROD
def retrieve_last_month_data_from_dbtasy():
    last_friday, this_thursday = get_start_and_end_day()
    return retrieve_data_from_dbtasy_using_dates(last_friday, this_thursday)


# Script para baixar dados do mês passado HAOC_TASY_PROD
def retrieve_specific_dates_from_dbtasy(start_day, end_day):
    start_day = datetime.strptime(start_day, "%d/%m/%Y")
    end_day = datetime.strptime(end_day, "%d/%m/%Y")
    return retrieve_data_from_dbtasy_using_dates(start_day, end_day)