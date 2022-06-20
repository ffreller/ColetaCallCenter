from turtle import done


def ExecuteProgram(send_mail, prod, download_data=True, preprocess=True, create_file=True, only_base=True):
    from traceback import format_exc
    from create_excel import gather_info_for_worksheets, create_excel_file
    from preprocess import preprocess_base, preprocess_secondary_table
    from dbcomms import retrieve_last_week_data_from_dbtasy, retrieve_specific_dates_from_dbtasy
    from send_email import send_standard_mail
    from src.helper_functions import delete_week_file
    from logging import getLogger
    
    logger = getLogger('standard')
    error_logger = getLogger('error')
    print()
    print('*'*80)
    delete_file = send_mail
    success = True
    
    if download_data:
        success = retrieve_last_week_data_from_dbtasy()
        # success = retrieve_specific_dates_from_dbtasy('14/06/2021', '14/01/2022')     
    
    if success:
        if preprocess:
            try:
                preprocess_base()
            except Exception:
                logger.error('Erro ao processar dataset base: %s' % format_exc())
                error_logger.error('Erro ao processar dataset base: %s' % format_exc())
                return
            
            for name in ['resumo de internação médica', 'atestado', 'receita', 'evolução médica', 'avaliação médica pa template']:
                try:
                    preprocess_secondary_table(dataset_name=name)
                except Exception:
                    logger.error('Erro ao processar %s: %s' % (name, format_exc()))
                    error_logger.error('Erro ao processar %s: %s' % (name, format_exc()))
                    return
            
        
        if create_file:
            try:
                if only_base:
                    df_base = gather_info_for_worksheets(only_base=True)
                else:
                    df_base, df_resumo_internacao, df_atestado, df_receita, df_evolucao, df_avaliacao_pa = gather_info_for_worksheets(only_base=False)
            except Exception:
                logger.error('Erro ao coletar informações para as planilhas: %s' % format_exc())
                error_logger.error('Erro ao coletar informações para as planilhas: %s' % format_exc())
                return

            try:
                if only_base:
                    create_excel_file(df_base, only_base=True)
                else:
                    create_excel_file(df_base, False, df_resumo_internacao, df_atestado, df_receita, df_evolucao, df_avaliacao_pa)
            except Exception:
                logger.error('Erro ao criar arquivo excel: %s' % format_exc())
                error_logger.error('Erro ao criar arquivo excel: %s' % format_exc())
                return
        
        if send_mail:
            try:
                send_standard_mail(prod=prod)
            except Exception:
                logger.error('Erro ao enviar emails: %s' % format_exc())
                error_logger.error('Erro ao enviar emails: %s' % format_exc())
                return

        if delete_file:
            try:
                delete_week_file()
            except Exception:
                logger.error('Erro ao deletar arquivo da semana: %s' % format_exc())
                error_logger.error('Erro ao deletar arquivo da semana: %s' % format_exc())
                return
            
        logger.debug('FIM: Sucesso ao executar script\n')

    
if __name__ == '__main__':
    from argparse import ArgumentParser
    import logging.config
    from src.configs import LOGGING_CONFIG
    
    logging.config.dictConfig(LOGGING_CONFIG)
    
    parser = ArgumentParser(description="My parser")
    parser.add_argument('--prod', dest='prod', action='store_true')
    parser.add_argument('--no-email', dest='no_email', action='store_true')
    parser.add_argument('--no-download', dest='no_download', action='store_true')
    parser.add_argument('--only-base', dest='only_base', action='store_true')
    parser.set_defaults(prod=False)
    parser.set_defaults(no_email=False)
    parser.set_defaults(no_download=False)
    parser.set_defaults(only_base=False)
    args = parser.parse_args()
    
    send_mail = not args.no_email
    download_data = not args.no_download
    only_base = args.only_base
    prod = args.prod
    
    if prod:
        only_base = True
        send_mail = True
        download_data = True

    ExecuteProgram(send_mail=send_mail, prod=prod, dowload_data=download_data, only_base=only_base)