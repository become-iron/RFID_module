# -*- coding: utf-8 -*-
import configparser as cp
from collections import namedtuple

from reader import Reader, log

__all__ = ('Readers',)


def _make_response(response=None, error=None) -> dict:
    """Формулирует ответ на запрос"""
    result = {}
    if response is not None:
        result.update({'response': response})
    if error is not None:
        result.update({'error': {'error_code': error.code, 'error_msg': error.msg}})
    return result


def check_for_errors(*errors):
    """Декоратор для проверки наличия ошибок во время работы с RFID"""
    # WARN для верной работы декоратора необходимо всегда указывать названия параметров при вызове декорируемых объектов
    def check_decorator(func):
        def wrapper(*args, **kwargs):
            for error in errors:
                if (error.param is None and error.check()) \
                        or (error.param in kwargs and error.check(kwargs[error.param])):
                    return _make_response(error=error)
            return func(*args, **kwargs)
        return wrapper
    return check_decorator


class _Errors:
    """Вспомогательный объект ддя хранения возникающих ошибок (кодов и описаний)"""
    _error = namedtuple('Error', ('code', 'msg', 'param', 'check'))

    InvalidReaderBusAddr = _error(0,
                                  'Невалидное значение параметра шины адреса',
                                  'bus_addr',
                                  lambda x: not isinstance(x, int))
    InvalidReaderPortNumber = _error(0,
                                     'Невалидное значение параметра номера порта',
                                     'port_number',
                                     lambda x: not isinstance(x, int))
    InvalidReaderState = _error(0,
                                'Невалидное значение параметра состояния ридера',
                                'state',
                                lambda x: not isinstance(x, bool))
    ReaderAlreadyExists = _error(0,
                                 'Ридер с данным идентификатором уже существует',
                                 'reader_id',
                                 lambda x: x in Readers)
    ReaderNotExists = _error(0,
                             'Ридера с данным идентификатором не существует',
                             'reader_id',
                             lambda x: x not in Readers)
    ReaderIsConnected = _error(0,
                               'Операция не может быть совершена, так как ридер подключён',
                               'reader_id',
                               lambda x: Readers[x]['state'] is True)
    ReaderIsDisconnected = _error(0,
                                  'Операция не может быть совершена, так как ридер отключён',
                                  'reader_id',
                                  lambda x: Readers[x]['state'] is False)
    OneOrMoreReadersAreConnected = _error(0,
                                          'Операция не может совершена, так как один или больше ридеров подключены',
                                          None,
                                          lambda: not all(map(lambda rid: Readers[rid]['state'] is False, Readers)))
    ReadersListAlreadyIsEmpty = _error(0,
                                       'Список ридеров уже пуст',
                                       None,
                                       lambda: len(Readers) == 0)

    @staticmethod
    def cast_error(r_code: int, error_msg: str):
        """Для оформления ошибки, возникшей на уровне FEIG SDK"""
        # r_code < 0
        return _Errors._error(r_code, error_msg)


# noinspection PyProtectedMember
class _MetaReaders(type):
    def __iter__(self):
        yield from Readers._readers

    def __getitem__(self, item):
        return Readers._readers[item]

    def __contains__(self, item):
        return item in Readers._readers

    def __len__(self):
        return len(Readers._readers)


class Readers(object, metaclass=_MetaReaders):
    """Хранение настроек ридеров и их состояний"""
    _file = 'reader_settings.ini'
    _readers = {}

    @staticmethod
    def _read_settings():
        """Читает настройки из файла. Должен быть вызван единожды при импортировании модуля"""
        settings = cp.ConfigParser()
        settings.read(Readers._file)
        Readers._readers.update({
             reader_id: {
                'bus_addr': int(settings[reader_id]['bus_addr']),
                'port_number': int(settings[reader_id]['port_number']),
                'state': False,
                'reader': None,
             }
             for reader_id in settings if reader_id != 'DEFAULT'
        })

    @staticmethod
    def save_settings():
        """Записывает настройки в файл"""
        settings = cp.ConfigParser()
        for reader_id, reader_settings in sorted(Readers._readers.items(), key=lambda x: x[0]):
            settings[reader_id] = {
                'bus_addr': reader_settings['bus_addr'],
                'port_number': reader_settings['port_number']
            }
        with open(Readers._file, 'w') as file:
            settings.write(file)

    @staticmethod
    def get_readers():
        """Возвращает информацию о ридерах: идентификаторы, настройки, состояния"""
        result = {
            reader_id: {
                'bus_addr': Readers._readers[reader_id]['bus_addr'],
                'port_number': Readers._readers[reader_id]['port_number'],
                'state': Readers._readers[reader_id]['state'],
            }
            for reader_id in Readers._readers
        }
        return _make_response(response=result)

    @staticmethod
    @check_for_errors(_Errors.InvalidReaderBusAddr, _Errors.InvalidReaderPortNumber, _Errors.ReaderAlreadyExists)
    def add_reader(reader_id: str, bus_addr: int, port_number: int):
        """Добавляет ридер"""
        # TODO исправить сигнатуру
        # TODO валидация данных
        # TODO создавать ли сразу экземпляр класса Reader?
        reader_id = str(reader_id)
        # if reader_id in Readers._readers:
        #     error = _Errors.ReaderAlreadyExists
        #     return _make_response(error=error)
        Readers._readers.update({
            reader_id: {
                'bus_addr': bus_addr,
                'port_number': port_number,
                'state': False,  # состояние: False - подключен, True - выключен
                'reader': None,
            }
        })
        return _make_response(response=0)

    @staticmethod
    @check_for_errors(_Errors.ReadersListAlreadyIsEmpty, _Errors.OneOrMoreReadersAreConnected)
    def delete_readers():
        """Удаляет ридеры"""
        Readers._readers = {}
        return _make_response(response=0)

    @staticmethod
    @check_for_errors(_Errors.ReaderNotExists)
    def get_reader(reader_id: int):
        """Возвращает настройки и состояние ридера по идентификатору"""
        result = {reader_id: {'bus_addr': Readers._readers['bus_addr'], 'port_number': Readers._readers['port_number']}}
        return _make_response(response=result)

    @staticmethod
    @check_for_errors(_Errors.ReaderNotExists, _Errors.ReaderIsConnected)
    def update_reader(reader_id: str, updates):
        # TODO переключение состояния ридера
        # TODO валидация данных
        if 'reader_id' in updates:
            if updates['reader_id'] in Readers._readers:
                error = _Errors.ReaderAlreadyExists
                return _make_response(error=error)
            # TODO дописать для случая изменения идентификатора
        if 'bus_addr' in updates:
            Readers._readers[reader_id]['bus_addr'] = updates['bus_addr']
        if 'port_number' in updates:
            Readers._readers[reader_id]['port_number'] = updates['port_number']
        return _make_response(response=0)

    @staticmethod
    @check_for_errors(_Errors.ReaderNotExists, _Errors.ReaderIsConnected)
    def delete_reader(reader_id: int):
        del Readers._readers[reader_id]
        return _make_response(response=0)

    @staticmethod
    def inventory(reader_id: int):
        # TODO
        pass

    @staticmethod
    def read_tags(reader_id: int):
        """Возвращает информацию с меток"""
        # TODO
        pass

    @staticmethod
    def write_tags(reader_id: int):
        """Записывает информацию в метки"""
        # TODO
        pass

    @staticmethod
    def clear_tags(reader_id: int):
        """Очищает информацию с меток"""
        # TODO
        pass


# noinspection PyProtectedMember
Readers._read_settings()  # инициализация настройками из файла

if __name__ == '__main__':
    from pprint import pprint
    pprint(Readers.add_reader(reader_id='3', bus_addr=1, port_number=1))
    pprint(Readers.add_reader(reader_id='4', bus_addr=3, port_number=3))
    pprint(Readers.get_readers())
    pprint(Readers.delete_readers())
    pprint(Readers.delete_readers())
    # print(len(Readers))
