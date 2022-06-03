from create_excel import create_excel_file, gather_info_for_worksheets
from preprocess import preprocess_base, preprocess_orientacao, preprocess_atestado_receita
from dbcomms import retrieve_last_month_data_from_dbtasy
from send_email import send_standard_mail_prod, send_standard_mail_test
from src.helper_functions import print_with_time, delete_week_file
from traceback import format_exc
from argparse import ArgumentParser


def ExecuteProgram(test, download_data=True, preprocess=True, create_file=True, sendEmail=True, delete_file=True):
    print()
    print('*'*80)
    if test:
        print('TESTE!')
    success = True
    if download_data:
        success = retrieve_last_month_data_from_dbtasy()     
    
    if success:
        if preprocess:
            try:
                preprocess_base()
            except Exception:
                print_with_time('Erro ao processar dataset base')
                print(format_exc())
                return
            
            try:
                preprocess_orientacao()
            except:
                print_with_time('Erro ao processar prescrições')
                print(format_exc())
                return
            
            try:
                preprocess_atestado_receita('atestado')
            except:
                print_with_time('Erro ao processar evoluções médicas')
                print(format_exc())
                return
            
            try:
                preprocess_atestado_receita('receita')
            except:
                print_with_time('Erro ao processar evoluções da enfermagem')
                print(format_exc())
                return
        
        if create_file:
            try:
                df_base, df_orientacao, df_atestado, df_receita = gather_info_for_worksheets()
            except:
                print_with_time('Erro ao coletar informações para as planilhas')
                print(format_exc())
                return

            try:
                create_excel_file(df_base, df_orientacao, df_atestado, df_receita)
            except:
                print_with_time('Erro ao criar arquivo de excel')
                print(format_exc())
                return
        
        if sendEmail:
            try:
                if test:
                    send_standard_mail_test()
                else:
                    send_standard_mail_prod()
            except:
                print_with_time('Erro ao enviar emails')
                print(format_exc())
                return

        if delete_file:
            try:
                delete_week_file()
            except:
                print_with_time('Erro ao deletar arquivo da semana')
                print(format_exc())
                return

    
if __name__ == '__main__':
    parser = ArgumentParser(description="My parser")
    parser.add_argument('--teste', dest='test', action='store_true')
    parser.set_defaults(test=False)
    args = parser.parse_args()
    test = args.test
    ExecuteProgram(test=test)
    # ExecuteProgram(download_data=False, preprocess=False, create_file=True,
    #                sendEmail=True, test=test, delete_file=True)
    