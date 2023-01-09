import logging
import time

from pywinauto import Desktop, findwindows

from gfe_devices_grabber.utils import State, split_list


class Detector:
    def __init__(self, state: State):
        self.state = state
        self.desktop = Desktop()
        self.app_selector = lambda: self.desktop.window(title_re='GFL - .*')
        self.table_selector = lambda: self.app_selector() \
            .child_window(title="tab_devices") \
            .child_window(class_name="SysListView32")

    def waite_application(self):
        while self.state.is_alive and not self.app_selector().exists(timeout=0, retry_interval=60):
            if self.state.is_program_opened or self.table_selector:
                self.state.is_program_opened = False
                self.state.is_devices_tab_table_opened = False
                self.state.notify()
            self._wait('Application')
        if self.state.is_alive and not self.state.is_program_opened:
            self.state.is_program_opened = True
            self.state.notify()
            logging.info('State change for application')

    def waite_table(self):
        control = None
        while self.state.is_alive and not control:
            control = self._resolve_control(self.table_selector())
            if not control:
                if self.state.is_devices_tab_table_opened:
                    self.state.is_devices_tab_table_opened = False
                    self.state.records_count = 0
                    self.state.notify()
                self._wait('Table')

        if self.state.is_alive:
            count = control.item_count()
            if not self.state.is_devices_tab_table_opened or self.state.records_count != count:
                self.state.is_devices_tab_table_opened = True
                self.state.records_count = count
                self.state.notify()
                logging.info(f'State change for table')

    def loop(self):
        while self.state.is_alive:
            try:
                self.waite_application()
                self.waite_table()
                self._wait('Loop', factor=4)
            except Exception:
                logging.exception('Opps..')
                self._wait('Opps..')
        logging.info('Exit loop')

    def extract_records(self):
        tb = self.table_selector()
        logging.info(f'Find {tb.item_count()} records')
        records = split_list(tb.texts()[1:], tb.column_count())
        return records

    def _wait(self, ctrl, factor=1):
        logging.debug(f'Waiting "{ctrl}"..')
        time.sleep(1.0 * factor)

    def _resolve_control(self, selector):
        try:
            ctrls = selector._WindowSpecification__resolve_control(selector.criteria, timeout=0, retry_interval=60)
            return ctrls[-1]
        except findwindows.ElementNotFoundError:
            return None
