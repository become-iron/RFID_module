# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from logic import Readers


def show_error(response):
    error_pattern = 'Произошла ошибка:\nКод: {0}\nОписание: {1}'
    msg = error_pattern \
        .format(response['error']['error_code'], response['error']['error_msg'])
    messagebox.showerror(message=msg)

# TODO при выходе из программы, отключать ридеры


# noinspection PyAttributeOutsideInit
class Application(tk.Frame):
    def __init__(self, master=None):
        self.readers = {}   # список доступных ридеров

        self.readers_list = ()
        self.conn_readers = ()
        self.tags = ()

        self.sel_reader = tk.StringVar()
        self.sel_conn_reader = tk.StringVar()
        self.sel_tag = tk.StringVar()

        self.reader_id = tk.StringVar()
        self.bus_addr = tk.StringVar()
        self.port_number = tk.StringVar()
        self.reader_state = tk.StringVar()  # TODO

        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.update_reader_sets_fields()

    def create_widgets(self):
        # настройки для виджетов: отступы и выравнивание по ширине
        def_sets = dict(padx=8, pady=3, sticky=tk.E + tk.W)

        # фреймы
        self.readers_sets_frame = ttk.LabelFrame(self, text='Настройка ридеров')
        self.readers_sets_frame.grid(row=0, column=0, padx=8, pady=3, sticky=tk.N+tk.E+tk.S+tk.W)

        self.tags_frame = ttk.LabelFrame(self, text='Работа с метками')
        self.tags_frame.grid(row=0, column=1, padx=8, pady=3, sticky=tk.N+tk.E+tk.S+tk.W)

        # ФРЕЙМ С НАСТРОЙКАМИ РИДЕРОВ
        # I строка
        self.readers_id_lbl = ttk.Label(self.readers_sets_frame, text='Идентификатор\nридера')
        self.readers_id_lbl.grid(row=0, column=0, **def_sets)

        self.readers_id_entry = ttk.Entry(self.readers_sets_frame, textvariable=self.reader_id)
        self.readers_id_entry.grid(row=0, column=1, **def_sets)

        self.add_reader_btn = ttk.Button(self.readers_sets_frame, text='Добавить ридер', command=self.add_reader)
        self.add_reader_btn.grid(row=0, column=2, **def_sets)

        # II строка
        self.bus_addr_lbl = ttk.Label(self.readers_sets_frame, text='Адрес шины')
        self.bus_addr_lbl.grid(row=1, column=0, **def_sets)

        self.bus_addr_entry = ttk.Entry(self.readers_sets_frame, textvariable=self.bus_addr)
        self.bus_addr_entry.grid(row=1, column=1, **def_sets)

        self.update_reader_btn = ttk.Button(self.readers_sets_frame, text='Обновить ридер', command=self.update_reader)
        self.update_reader_btn.grid(row=1, column=2, **def_sets)

        # III строка
        self.port_number_lbl = ttk.Label(self.readers_sets_frame, text='Номер порта')
        self.port_number_lbl.grid(row=2, column=0, **def_sets)

        self.port_number_enrty = ttk.Entry(self.readers_sets_frame, textvariable=self.port_number)
        self.port_number_enrty.grid(row=2, column=1, **def_sets)

        self.delete_reader_btn = ttk.Button(self.readers_sets_frame, text='Удалить ридер', command=self.delete_reader)
        self.delete_reader_btn.grid(row=2, column=2, **def_sets)

        # IV строка
        self.reader_state_lbl = ttk.Label(self.readers_sets_frame, text='Подключен ли\nридер')
        self.reader_state_lbl.grid(row=3, column=0, **def_sets)

        self.reader_state_cb = ttk.Combobox(self.readers_sets_frame, state=('readonly',),
                                            values=('Подключен', 'Отключен'), textvariable=self.reader_state)
        self.reader_state_cb.grid(row=3, column=1, **def_sets)

        self.delete_all_readers_btn = ttk.Button(self.readers_sets_frame,
                                                 text='Удалить\nвсе ридеры', command=self.delete_all_readers)
        self.delete_all_readers_btn.grid(row=3, column=2, **def_sets)

        # V строка
        self.readers_list_lbl = ttk.Label(self.readers_sets_frame, text='Доступные\nридеры')
        self.readers_list_lbl.grid(row=4, column=0, **def_sets)

        def update_fields(event):
            """Обновляет поля в соответствии с выбранным ридером"""
            reader_id = self.sel_reader.get()
            if reader_id == '':
                return
            reader = self.readers[reader_id]
            self.reader_id.set(reader_id)
            self.bus_addr.set(reader['bus_addr'])
            self.port_number.set(reader['port_number'])
            self.reader_state.set('Подключен' if reader['state'] else 'Отключен')  # TODO
        self.readers_list_cb = ttk.Combobox(self.readers_sets_frame, state=('readonly',), textvariable=self.sel_reader)
        self.readers_list_cb.grid(row=4, column=1, columnspan=2, **def_sets)
        self.readers_list_cb.bind('<<ComboboxSelected>>', update_fields)

        # ФРЕЙМ ДЛЯ РАБОТЫ С МЕТКАМИ
        # I строка
        self.conn_readers_lbl = ttk.Label(self.tags_frame, text='Подключенные\nридеры')
        self.conn_readers_lbl.grid(row=0, column=0, **def_sets)

        self.conn_readers_cb = ttk.Combobox(self.tags_frame, state=('readonly',), textvariable=self.sel_conn_reader)
        self.conn_readers_cb.grid(row=0, column=1, columnspan=2, **def_sets)

        # II строка
        self.invent_lbl = ttk.Label(self.tags_frame, text='Метки')
        self.invent_lbl.grid(row=1, column=0, **def_sets)

        self.tags_list_cb = ttk.Combobox(self.tags_frame, state=('readonly',), textvariable=self.sel_tag)
        self.tags_list_cb.grid(row=1, column=1, **def_sets)

        self.invent_btn = ttk.Button(self.tags_frame, text='Инвента\nризация', command=self.inventory)
        self.invent_btn.grid(row=1, column=2, **def_sets)

        # III-V строки
        self.tag_data_lbl = ttk.Label(self.tags_frame, text='Данные с/для\nметки')
        self.tag_data_lbl.grid(row=2, column=0, rowspan=3, **def_sets)

        self.tag_data_text = tk.Text(self.tags_frame, width=28, height=8)
        self.tag_data_text.grid(row=2, column=1, rowspan=3, **def_sets)

        self.read_tag_btn = ttk.Button(self.tags_frame, text='Считать\nметку', command=self.read_tag)
        self.read_tag_btn.grid(row=2, column=2, **def_sets)

        self.write_tag_btn = ttk.Button(self.tags_frame, text='Записать\nметку', command=self.write_tag)
        self.write_tag_btn.grid(row=3, column=2, **def_sets)

        self.clear_tag_btn = ttk.Button(self.tags_frame, text='Очистить\nметку', command=self.clear_tag)
        self.clear_tag_btn.grid(row=4, column=2, **def_sets)

    def update_reader_sets_fields(self):
        self.reader_id.set('')
        self.bus_addr.set('')
        self.port_number.set('')
        self.reader_state.set('')
        self.sel_reader.set('')
        self.sel_conn_reader.set('')

        # удаляем старые ридеры
        self.readers_list_cb['values'] = ()
        self.conn_readers_cb['values'] = ()

        response = Readers.get_readers()
        self.readers = response['response']

        self.readers_list_cb['values'] = tuple(self.readers.keys())
        self.conn_readers_cb['values'] = \
            tuple(reader_id for reader_id in self.readers if self.readers[reader_id]['state'])

    def add_reader(self):
        # TODO каким-то образом идентификатор записывается в кодировке windows-1251. возможно проблема в logic.py
        reader_id = self.reader_id.get()
        bus_addr = self.bus_addr.get()
        port_number = self.port_number.get()
        reader_state = self.reader_state.get()

        # проверяем, что все поля непустые
        if not all(map(
                lambda x: x != '',
                (reader_id, bus_addr, port_number, reader_state)
        )):
            messagebox.showerror(message='Не указаны все требуемые значения')
            return
        if not bus_addr.isdigit():
            messagebox.showerror(message='Адрес шины должен быть числом')
            return
        if not port_number.isdigit():
            messagebox.showerror(message='Номер порта должен быть числом')
            return

        bus_addr = int(bus_addr)
        port_number = int(port_number)
        reader_state = True if reader_state == 'Подключен' else False

        response = Readers.add_reader(
            data={'reader_id': reader_id, 'bus_addr': bus_addr, 'port_number': port_number, 'state': reader_state}
        )
        if 'error' in response:
            show_error(response)
            return
        self.update_reader_sets_fields()
        messagebox.showinfo(message='Ридер добавлен')

    def update_reader(self):
        reader_id = self.reader_id.get()
        bus_addr = self.bus_addr.get()
        port_number = self.port_number.get()
        reader_state = self.reader_state.get()

        # проверяем, что все поля непустые
        if not all(map(
                lambda x: x != '',
                (reader_id, bus_addr, port_number, reader_state)
        )):
            messagebox.showerror(message='Не указаны все требуемые значения')
            return
        if not bus_addr.isdigit():
            messagebox.showerror(message='Адрес шины должен быть числом')
            return
        if not port_number.isdigit():
            messagebox.showerror(message='Номер порта должен быть числом')
            return

        bus_addr = int(bus_addr)
        port_number = int(port_number)
        reader_state = True if reader_state == 'Подключен' else False  # TODO

        sel_reader = self.sel_reader.get()

        # TODO не обновлять неизменённые параметры
        if sel_reader == '' or sel_reader == reader_id:
            response = Readers.update_reader(
                reader_id=reader_id,
                data={'bus_addr': bus_addr, 'port_number': port_number, 'state': reader_state}
            )
        else:
            # обновляется и идентификатор ридера
            response = Readers.update_reader(
                reader_id=sel_reader,
                data={'reader_id': reader_id, 'bus_addr': bus_addr, 'port_number': port_number, 'state': reader_state}
            )

        if 'error' in response:
            show_error(response)
            return
        self.update_reader_sets_fields()
        messagebox.showinfo(message='Ридер обновлён')

    def delete_reader(self):
        reader_id = self.sel_reader.get()
        if reader_id == '':
            messagebox.showerror(message='Сначала нужно выбрать ридер')
            return

        answer = messagebox.askyesno(message='Уверены, что хотите удалить ридер?')
        if answer != 'yes':
            return

        response = Readers.delete_reader(reader_id=reader_id)
        if 'error' in response:
            show_error(response)
            return

        self.update_reader_sets_fields()
        messagebox.showinfo(message='Ридер удалён')

    def delete_all_readers(self):
        answer = messagebox.askyesno(message='Уверены, что хотите удалить все ридеры?')
        if answer != 'yes':
            return

        response = Readers.delete_readers()
        if 'error' in response:
            show_error(response)
            return

        self.update_reader_sets_fields()
        messagebox.showinfo(message='Все ридеры удалены')

    def inventory(self):
        reader_id = self.sel_conn_reader.get()
        if reader_id == '':
            messagebox.showerror(message='Сначала нужно выбрать ридер')
            return

        response = Readers.inventory(reader_id=reader_id)
        if 'error' in response:
            show_error(response)
            return

        self.tags_list_cb['values'] = response['response']
        messagebox.showinfo(message='Инвентаризация проведена')

    def read_tag(self):
        self.tag_data_text.delete('0.0', tk.END)  # очищаем поле данных с метки

        reader_id = self.sel_conn_reader.get()
        tag_id = self.sel_tag.get()
        if reader_id == '':
            messagebox.showerror(message='Сначала нужно выбрать ридер')
            return
        if tag_id == '':
            messagebox.showerror(message='Сначала нужно выбрать метку')
            return

        response = Readers.read_tags(reader_id=reader_id, data=(tag_id,))
        if 'error' in response:
            show_error(response)
            return

        self.tag_data_text.insert('0.0', response['response'])  # записываем данные
        messagebox.showinfo(message='Информация с метки считана')

    def write_tag(self):
        reader_id = self.sel_conn_reader.get()
        tag_id = self.sel_tag.get()
        if reader_id == '':
            messagebox.showerror(message='Сначала нужно выбрать ридер')
            return
        if tag_id == '':
            messagebox.showerror(message='Сначала нужно выбрать метку')
            return

        tag_data = self.tag_data_text.get('0.0', tk.END).replace('\n', '')

        response = Readers.write_tags(reader_id=reader_id, data={tag_id: tag_data})
        if 'error' in response:
            show_error(response)
            return

        messagebox.showinfo('Информация записана на метку')

    def clear_tag(self):
        reader_id = self.sel_conn_reader.get()
        tag_id = self.sel_tag.get()
        if reader_id == '':
            messagebox.showerror(message='Сначала нужно выбрать ридер')
            return
        if tag_id == '':
            messagebox.showerror(message='Сначала нужно выбрать метку')
            return

        response = Readers.clear_tags(reader_id=reader_id, data=(tag_id,))
        if 'error' in response:
            show_error(response)
            return

        self.tag_data_text.delete('0.0', tk.END)  # очищаем поле данных с метки
        messagebox.showinfo('Информация удалена с метки')


root = tk.Tk()
root.resizable(0, 0)  # запрет на изменение размеров окна

app = Application(master=root)
app.master.title('Управление ридерами (logic.py)')
app.mainloop()
