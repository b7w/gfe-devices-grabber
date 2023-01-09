import logging
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename
from typing import Callable

from gfe_devices_grabber.utils import State, Events

FONT = ("Courier", 12)

SUCCESS_COLOR = 'green3'
WARNING_COLOR = 'dark orange'


def create_label(window, wrap_length):
    return tk.Label(master=window, text='', fg=WARNING_COLOR,
                    font=FONT, anchor=tk.E, justify=tk.RIGHT,
                    wraplengt=wrap_length)


def change_label(lb: tk.Label, text: str, status: bool):
    lb['text'] = text
    lb['fg'] = SUCCESS_COLOR if status else WARNING_COLOR


def on_state_changed(state: State, lb1: tk.Label, lb2: tk.Label, lb3: tk.Label, lb4: tk.Label, btn: tk.Button):
    if state.is_program_opened:
        change_label(lb1, 'GFE Connector захвачен', status=True)
    else:
        change_label(lb1, 'GFE Connector не найден', status=False)

    if state.is_devices_tab_table_opened:
        change_label(lb2, 'Закладка "Devices" открыта.\nРежиме "Device List+All" выбран', status=True)
    else:
        change_label(lb2, 'Закладка "Devices" не открыта.\nИли режиме "Device List" не выбран', status=False)

    if state.records_count:
        change_label(lb3, 'Найдено {} записей'.format(state.records_count), status=True)
    else:
        change_label(lb3, 'Найдено 0 записей', status=False)

    status = [state.save_as.name if state.save_as else '', state.save_status]
    lb4['text'] = ' - '.join(i for i in status if i)

    if state.save_as and state.records_count > 0 and not state.is_locked:
        btn['state'] = 'normal'
    else:
        btn['state'] = 'disabled'


def on_save_as(state: State):
    filepath = asksaveasfilename(
        confirmoverwrite=True,
        defaultextension="xlsx",
        filetypes=[("Exel", "*.xlsx")],
    )
    if filepath:
        state.save_as = Path(filepath)
    state.save_status = ''
    state.notify()


def on_grab(state: State, grabber: Callable):
    def on_result(result):
        e = result.exception()
        if e:
            logging.exception('Error while try grab')
            messagebox.showerror("Error", str(e))
            state.save_status = 'Ошибка!'
        else:
            state.save_status = 'Сохранено'
            logging.info(f'Saved {state.records_count} records to {state.save_as}')
        state.is_locked = False
        state.notify()

    if not state.is_locked:
        logging.info(f'Starting saving {state.records_count} records to {state.save_as}')
        state.is_locked = True
        state.save_status = 'Сохранение...'
        state.notify()
        future = grabber()
        future.add_done_callback(on_result)
    else:
        logging.warning(f'Skipped lock')


def create_window(state: State, grabber: Callable):
    window = tk.Tk()
    window.title('GFE Devices Grabber')

    min_width = round(window.winfo_screenwidth() / 5)
    max_label_width = round(min_width / 0.7)
    window.resizable(width=False, height=False)
    window.columnconfigure(0, minsize=min_width)

    state.listeners.append(lambda: window.event_generate(Events.STATE_CHANGED))

    lb1 = create_label(window, max_label_width)
    lb1.grid(row=0, column=0, sticky='ew')

    lb2 = create_label(window, max_label_width)
    lb2.grid(row=1, column=0, sticky='ew')

    lb3 = create_label(window, max_label_width)
    lb3.grid(row=2, column=0, sticky='ew')

    btn_fr = tk.Frame(master=window, relief=tk.GROOVE, borderwidth=2)

    btn_grab = tk.Button(master=btn_fr, text='Захватить данные', state='disabled',
                         command=lambda: on_grab(state, grabber))
    btn_grab.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)

    btn_save = tk.Button(master=btn_fr, text='Сохранить как',
                         command=lambda: on_save_as(state))
    btn_save.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)

    lb_status = tk.Label(master=btn_fr, text='')
    lb_status.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)

    btn_fr.grid(row=4, column=0, sticky='ew')

    window.bind(Events.STATE_CHANGED, lambda _: on_state_changed(state, lb1, lb2, lb3, lb_status, btn_grab))
    window.bind(Events.RETURN_KEY, lambda _: on_grab(state, grabber))
    # Init form
    on_state_changed(state, lb1, lb2, lb3, lb_status, btn_grab)
    return window
