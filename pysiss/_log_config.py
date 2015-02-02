LOG_CONFIG = {
    'version': 1,
    'loggers': {
        'pysiss': {'handlers': ['console', 'file']}
    },
    'formatters': {
        'brief': {'format': "pysiss - %(module)-8s - %(message)s"},
        'detailed': {'format': '%(asctime)s %(module)-17s line:%(lineno)-4d ' \
                     '%(levelname)-8s %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler',
                    'formatter': 'brief', 'stream': 'ext://sys.stdout'},
        'file': {'class': 'logging.handlers.RotatingFileHandler',
                 'formatter': 'detailed', 'filename': 'logs/pysiss.log',
                 'maxBytes': 2 ** 15, 'level': 'DEBUG'}
    }
}
