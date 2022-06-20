import os
import sys
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="My parser")
    parser.add_argument('--prod', dest='prod', action='store_true')
    parser.add_argument('--no-email', dest='no_email', action='store_true')
    parser.set_defaults(prod=False)
    parser.set_defaults(no_email=False)
    args = parser.parse_args()
    prod = args.prod
    no_email = args.no_email
    
    # Set library path for SQLAlchemy
    this_dir = os.path.dirname(os.path.realpath(__file__))
    instant_client_path = os.path.join(this_dir, 'instantclient_21_5')
    # Oracle client path
    os.environ['LD_LIBRARY_PATH'] = instant_client_path
    os.environ['TZ'] = 'America/Sao_Paulo'
    exec_list = [sys.executable] + [this_dir+'/program.py']
    if prod:
        exec_list += ['--prod']
    if no_email:
        exec_list += ['--no-email']

    # Run Program.py with adjusted arguments
    os.execv(sys.executable, exec_list)

