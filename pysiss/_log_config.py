LOG_CONFIG = {
    'version': 1,
    'loggers': {
        'pysiss': {'level': 'CRITICAL', 'handlers': ['console']}
    },
    'formatters': {
        'brief': {'format': "(pysiss) %(module)-8s - %(levelname)-8s" \
                            " %(message)s"},
        'detailed': {'format': '%(asctime)s %(module)-17s line:%(lineno)-4d ' \
                     '%(levelname)-8s %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler',
                    'formatter': 'brief',
                    'stream': 'ext://sys.stdout'}
    }
}
