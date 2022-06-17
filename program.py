def ExecuteProgram(send_mail, test, download_data=True, preprocess=True, create_file=True):
    from traceback import format_exc
    from create_excel import gather_info_for_worksheets, create_excel_file
    from preprocess import preprocess_base, preprocess_secondary_table
    from dbcomms import retrieve_last_week_data_from_dbtasy, retrieve_specific_dates_from_dbtasy
    from send_email import send_standard_mail
    from src.helper_functions import delete_week_file, get_logger
    
    logger = get_logger('standard')
    error_logger = get_logger('error')
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
                df_base = gather_info_for_worksheets(only_base=True)
            except Exception:
                logger.error('Erro ao coletar informações para as planilhas: %s' % format_exc())
                error_logger.error('Erro ao coletar informações para as planilhas: %s' % format_exc())
                return

            try:
                create_excel_file(df_base, only_base=True)
            except Exception:
                logger.error('Erro ao criar arquivo excel: %s' % format_exc())
                error_logger.error('Erro ao criar arquivo excel: %s' % format_exc())
                return
        
        if send_mail:
            try:
                send_standard_mail(test=test)
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
    parser = ArgumentParser(description="My parser")
    parser.add_argument('--teste', dest='test', action='store_true')
    parser.add_argument('--no-email', dest='no_email', action='store_true')
    parser.set_defaults(test=False)
    parser.set_defaults(no_email=False)
    args = parser.parse_args()
    test = args.test
    send_mail = not args.no_email
    ExecuteProgram(send_mail=send_mail, test=test)
    # ExecuteProgram(send_mail=send_mail, test=test,  
    #                download_data=False, preprocess=True, create_file=False)