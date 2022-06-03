# from create_excel import create_excel_file, gather_info_for_worksheets
from preprocess import preprocess_base, preprocess_orientacao, preprocess_atestado_receita
from dbcomms import retrieve_last_month_data_from_dbtasy
# from send_email import send_standard_mail_prod, send_standard_mail_test
from src.helper_functions import print_with_time, delete_week_file
import traceback
import argparse


def ExecuteProgram(download_data=True, preprocess=True, create_file=True, sendEmail=True, test=False, delete_file=True):
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
                print(traceback.format_exc())
                return
            
            try:
                preprocess_orientacao()
            except:
                print_with_time('Erro ao processar prescrições')
                print(traceback.format_exc())
                return
            
            try:
                preprocess_atestado_receita('atestado')
            except:
                print_with_time('Erro ao processar evoluções médicas')
                print(traceback.format_exc())
                return
            
            try:
                preprocess_atestado_receita('receita')
            except:
                print_with_time('Erro ao processar evoluções da enfermagem')
                print(traceback.format_exc())
                return
        
    #     if create_files:
    #         try:
    #             df_main_, evol_med_, evol_enf_, prescricoes_, movimentacoes_, hemocultura_, antibiotico_  = gather_info_for_worksheets()
    #         except:
    #             print_with_time('Erro ao coletar informações para as planilhas')
    #             print(traceback.format_exc())
    #             return

    #         try:
    #             create_excel_files(df_main_, evol_med_, evol_enf_, prescricoes_, movimentacoes_,  hemocultura_, antibiotico_)
    #         except:
    #             print_with_time('Erro ao criar arquivos de excel')
    #             print(traceback.format_exc())
    #             return
        
    #     if sendEmail:
    #         try:
    #             if test:
    #                 send_standard_mail_test()
    #             else:
    #                 send_standard_mail_prod()
    #         except:
    #             print_with_time('Erro ao enviar emails')
    #             print(traceback.format_exc())
    #             return

    #     if delete_file:
    #         try:
    #             delete_week_file()
    #         except:
    #             print_with_time('Erro ao deletar arquivos da semana')
    #             print(traceback.format_exc())
    #             return

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="My parser")
    parser.add_argument('--teste', dest='test', action='store_true')
    parser.set_defaults(test=False)
    args = parser.parse_args()
    test = args.test
    ExecuteProgram(test=test)
    # ExecuteProgram(download_data=False, preprocess=False, create_file=True,
    #                sendEmail=True, test=test, delete_file=True)
    