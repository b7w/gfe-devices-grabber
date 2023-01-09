import logging.config
import logging.handlers
from concurrent.futures import ThreadPoolExecutor

from gfe_devices_grabber.automation import Detector
from gfe_devices_grabber.report import create_report
from gfe_devices_grabber.ui import create_window
from gfe_devices_grabber.utils import State

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)-5s [%(asctime)s, %(msecs)d] %(name)s %(filename)s at %(lineno)d: %(message)s',
            'datefmt': '%Y-%b-%d %H:%M:%S',
        },
    },
    'handlers': {
        'simple': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'windows': {
            'level': 'WARNING',
            'class': 'logging.handlers.NTEventLogHandler',
            'appname': 'gfe-devices-grabber',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'gfe_devices_grabber': {
            'handlers': ['simple', 'windows'],
            'level': 'DEBUG',
            'propagate': False
        },
        'root': {
            'handlers': ['simple', 'windows'],
            'level': 'INFO',
        }
    },
}


def grabber(state: State, detector: Detector):
    records = detector.extract_records()
    create_report(records, state.save_as.as_posix())


def main():
    with ThreadPoolExecutor(max_workers=2) as pool:
        # t = threading.Thread(target=detector.loop)
        # t.start()
        # create objects
        state = State()
        detector = Detector(state)
        window = create_window(state, lambda: pool.submit(grabber, state, detector))

        # start loops
        logging.info('Staring..')
        pool.submit(detector.loop)
        window.mainloop()

        # Stop detector loop
        state.is_alive = False
        # t.join()
    logging.info('Stopped!')


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)
    main()
