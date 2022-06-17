from pathlib import Path


MAIN_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = MAIN_DIR / 'data/processed'
INTERIM_DATA_DIR = MAIN_DIR / 'data/interim'
RAW_DATA_DIR = MAIN_DIR / 'data/raw'
REPORTS_DIR = MAIN_DIR / 'reports'



LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format':'%(asctime)s - %(levelname)s: %(message)s',
            'datefmt':'%d/%m/%Y %H:%M:%S'
        },
    },
    'handlers': { 
        'stream': { 
            'level': 'NOTSET',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': { 
            'level': 'NOTSET',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'log.log',
            'mode': 'a'
        },
        'file_error': { 
            'level': 'ERROR',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'mode': 'a'
        },
    },
    'loggers': { 
        '': {  # root logger
            'handlers': ['stream'],
            'level': 'NOTSET',
            'propagate': False
        },
        'standard': { 
            'handlers': ['stream', 'file'],
            'level': 'NOTSET',
            'propagate': False
        },
        'error': { 
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False
        }
    } 
}
