# -*- coding: utf-8 -*-
import configparser as cp
import logging as log
from reader import Reader
from collections import namedtuple

log.basicConfig(format='%(levelname)s: %(asctime)-15s. %(message)s', level=log.INFO)


# коды возникших ошибок
class Errors:
    """Вспомогательный объект ддя хранения возникающих ошибок (кодов и описаний)"""
    _error = namedtuple('Error', ('code', 'msg'))
    ReaderAlreadyExists = _error(0, 'Ридер с идентификатором "{0}" уже существует')
    ReaderNotExists = _error(1, 'Ридера с идентификатором "{0}" не существует')
    ReaderAlreadyIsConnected = _error(2, '')
    ReaderAlreadyIsDisconnected = _error(3, '')
    InvalidReaderParameter = _error(4, '')


class Readers:
    """Хранение настроек ридеров и их состояний"""
    _file = 'reader_settings.ini'
    _settings = {}

    @staticmethod
    def _read_settings():
        """Читает настройки из файла"""
        settings = cp.ConfigParser()
        settings.read(Readers._file)
        for reader_id in settings:
            if reader_id == 'DEFAULT':
                continue
            Readers._settings.update({reader_id: {
                'bus_addr': settings[reader_id]['bus_addr'],
                'port_number': settings[reader_id]['port_number'],
                'state': False,
                'reader': None,
            }})

    @staticmethod
    def save_settings():
        """Записывает настройки в файл"""
        settings = cp.ConfigParser()
        for reader_id, reader_settings in sorted(Readers._settings.items(), key=lambda x: x[0]):
            settings[reader_id] = {
                'bus_addr': reader_settings['bus_addr'],
                'port_number': reader_settings['port_number']
            }
        with open(Readers._file, 'w') as file:
            settings.write(file)

    @staticmethod
    def add_reader(reader_id: str, bus_addr: int, port_number: int):
        reader_id = str(reader_id)
        if reader_id not in Readers._settings:
            Readers._settings.update({
                reader_id: {
                    'bus_addr': bus_addr,
                    'port_number': port_number,
                    'state': False,  # состояние: False - подключен, True - выключен
                    'reader': None,
                }
            })
        else:
            warn = 'Ридер с идентификатором "{0}" уже существует'.format(reader_id)
            log.warning(warn)
            # TODO возвращать ошибку?



    @staticmethod
    def delete_readers():
        Readers._settings = {}

    @staticmethod
    def update_reader():
        pass

    @staticmethod
    def contains(item):
        return item in Readers._settings


# noinspection PyProtectedMember
Readers._read_settings()  # инициализация настройками из файла

if __name__ == '__main__':
    Readers.add_reader('1', 1, 1)
    Readers.add_reader('2', 3, 3)
    print(Readers.contains('2'))
    print(Readers.contains('3'))
    print(Readers.contains('4'))
