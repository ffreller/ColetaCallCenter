# Usuario e senha
def get_usuario_senha_db_tns(db_tns):
    from credentials import USUARIO_PROD, SENHA_PROD, USUARIO_TESTE, SENHA_TESTE
    from base64 import b64decode
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
    return usuario, senha, vDB_TNS
    

# Cria engine do sqlalchemy
def create_sqlalchemy_engine(db_tns):
    from sqlalchemy import create_engine
    usuario, senha, vDB_TNS = get_usuario_senha_db_tns(db_tns)
    conn = create_engine(f'oracle+cx_oracle://{usuario}:{senha}@{vDB_TNS}')
    return conn


#Cria conexão via cxOracle
def create_conn_cxOracle(db_tns):
    from cx_Oracle import connect
    usuario, senha, vDB_TNS = get_usuario_senha_db_tns(db_tns)
    conn = connect(user=usuario, password=senha, dsn=vDB_TNS)
    return conn


# Executa query via pandas e sqlalchemy
def execute_query_pandas(query, conn):
    from pandas import read_sql
    return read_sql(query, conn)


# Executa query via cxOracle e carrega dados para dataframe
def execute_query_cxOracle_and_load_to_df(query, conn, columns):
    from pandas import DataFrame
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return DataFrame(rows, columns=columns)


# Lë queries presentes em arquivo .sql e separadas por comentários
def read_queries_from_file(fpath=None):
    from re import findall, split
    from src.definitions import MAIN_DIR
    if fpath is None:
        fpath = MAIN_DIR/'data/sql_queries_callcenter.sql'
    with open(fpath, 'r') as f:
        sqlFile = f.read()
    query_names = findall('-- (.*)', sqlFile)
    queries = split('--.*', sqlFile)[1:]
    return dict(zip(query_names, queries))


# Script para baixar dados do HAOC_TASY_PROD
def retrieve_data_from_dbtasy_using_dates(start_date, end_date):
    from logging import getLogger
    from src.definitions import RAW_DATA_DIR
    
    logger = getLogger('standard')
    error_logger = getLogger('error')
    start_date = start_date.strftime('%d/%m/%Y')
    end_date = end_date.strftime('%d/%m/%Y')
    logger.debug(f"Baixando dados do DB_TASY: De %s até %s" % (start_date, end_date))
    queries = read_queries_from_file()
    sqlalchemy_engine = create_sqlalchemy_engine(db_tns='tasy')
    conn_cxOracle = create_conn_cxOracle(db_tns='tasy')
    tabelas_cx_Oracle = ['Atestado', 'Receita', 'Avaliação Médica PA Template', 'Evolução Médica']
    success = True
    for query_name in queries.keys():
        query = queries[query_name]
        assert 'DATE_TO_REPLACE_START' in query, "Sem data início para substituir"
        assert 'DATE_TO_REPLACE_END' in query, "Sem data fim para substituir"
        query = query.replace('DATE_TO_REPLACE_START', start_date).replace('DATE_TO_REPLACE_END', end_date)
        try:
            
            if query_name not in tabelas_cx_Oracle:
                df = execute_query_pandas(query, sqlalchemy_engine)
            else:
                name_of_event = query_name.split(" ")[0].lower()
                columns = ['nr_atendimento', f'dt_{name_of_event}', 'dt_liberacao', f'ds_{name_of_event}']
                if query_name == 'Avaliação Médica PA Template':
                    columns = ['nr_atendimento', 'ds_resultado', 'ds_utc']
                df = execute_query_cxOracle_and_load_to_df(query, conn_cxOracle, columns=columns)
            
        except Exception as e:
            logger.error(f"Erro ao executar query '%s': %s " % (query_name.title(), str(e)))
            error_logger.error(f"Erro ao executar query '%s': %s " % (query_name.title(), str(e)))
            success = False
        if success:
            df_size = len(df.index)
            assert df_size != 0, f"Erro ao executar query {query_name.title()}: dataset vazio"
            logger.debug(f"Sucesso ao executar query '%s': %s registros" % (query_name.title(), df_size))
            df.to_pickle(RAW_DATA_DIR/f"{query_name.title().replace(' ', '_')}.pickle")
    sqlalchemy_engine.dispose()
    conn_cxOracle.close()
   
    return success


# Script para baixar dados do mês passado HAOC_TASY_PROD
def retrieve_last_week_data_from_dbtasy():
    from src.helper_functions import get_start_and_end_day
    last_friday, this_thursday = get_start_and_end_day()
    return retrieve_data_from_dbtasy_using_dates(last_friday, this_thursday)


# Script para baixar dados do mês passado HAOC_TASY_PROD
def retrieve_specific_dates_from_dbtasy(start_day: str, end_day: str):
    from datetime import datetime
    import re
    date_pattern = re.compile('\d{2}/\d{2}/\d{4}')
    assert date_pattern.match(start_day), 'Data de início inválida'
    assert date_pattern.match(end_day), 'Data de fim inválida'
    start_day = datetime.strptime(start_day, "%d/%m/%Y")
    end_day = datetime.strptime(end_day, "%d/%m/%Y")
    return retrieve_data_from_dbtasy_using_dates(start_day, end_day)