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
        result.update({'error_code': error.code, 'error_msg': error.msg})
    return result


class _Errors:
    """Вспомогательный объект ддя хранения возникающих ошибок (кодов и описаний)"""
    _error = namedtuple('Error', ('code', 'msg'))

    InvalidReaderParameter = _error(0, 'Невалидное значение параметра')
    ReaderAlreadyExists = _error(0, 'Ридер с данным идентификатором уже существует')
    ReaderNotExists = _error(0, 'Ридера с данным идентификатором не существует')
    ReaderAlreadyIsConnected = _error(0, 'Ридер с данным идентификаторм уже присоединён')
    ReaderAlreadyIsDisconnected = _error(0, 'Ридер с данным идентификатором уже отсоединён')
    ReadersListAlreadyIsEmpty = _error(0, 'Список ридеров уже пуст')
    ReaderIsConnected = _error(0, 'Операция не может быть совершена, так как ридер подключён')
    OneOrMoreReadersAreConnected = _error(0, 'Операция не может совершена, так как один или больше ридеров подключены')

    @staticmethod
    def cast_error(r_code: int, error_msg: str):
        """Для оформления ошибки, возникшей на уровне FEIG SDK"""
        # r_code < 0
        return _Errors._error(r_code, error_msg)


class Readers:
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
                'bus_addr': Readers._readers['bus_addr'],
                'port_number': Readers._readers['port_number'],
                'state': Readers._readers['state'],
            }
            for reader_id in Readers._readers
        }
        return _make_response(response=result)

    @staticmethod
    def add_reader(reader_id: str, bus_addr: int, port_number: int):
        """Добавляет ридер"""
        # TODO исправить сигнатуру
        # TODO валидация данных
        # TODO создавать ли сразу экземпляр класса Reader?
        reader_id = str(reader_id)
        if reader_id in Readers._readers:
            error = _Errors.ReaderAlreadyExists
            return _make_response(error=error)
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
    def delete_readers():
        """Удаляет ридеры"""
        if len(Readers._readers) == 0:
            error = _Errors.ReadersListAlreadyIsEmpty
            return _make_response(error=error)
        if not all(map(lambda reader_id: Readers._readers[reader_id]['state'] is False, Readers._readers)):
            error = _Errors.OneOrMoreReadersAreConnected
            return _make_response(error=error)
        Readers._readers = {}
        return _make_response(response=0)

    @staticmethod
    def get_reader(reader_id: int):
        """Возвращает настройки и состояние ридера по идентификатору"""
        if reader_id not in Readers._readers:
            error = _Errors.ReaderNotExists
            return _make_response(error=error)
        result = {reader_id: {'bus_addr': Readers._readers['bus_addr'], 'port_number': Readers._readers['port_number']}}
        return _make_response(response=result)

    @staticmethod
    def update_reader(reader_id: str, updates):
        # TODO валидация данных
        if reader_id not in Readers._readers:
            error = _Errors.ReaderNotExists
            return _make_response(error=error)
        if Readers._readers[reader_id]['state'] is True:
            error = _Errors.ReaderIsConnected
            return _make_response(error=error)
        if 'reader_id' in updates:
            if updates['reader_id'] in Readers._readers:
                error = _Errors.ReaderAlreadyExists
                return _make_response(error=error)
            # TODO дописать случая изменения идентификатора
        if 'bus_addr' in updates:
            Readers._readers[reader_id]['bus_addr'] = updates['bus_addr']
        if 'port_number' in updates:
            Readers._readers[reader_id]['port_number'] = updates['port_number']
        return _make_response(response=0)

    @staticmethod
    def delete_reader(reader_id: int):
        if reader_id not in Readers._readers:
            error = _Errors.ReaderNotExists
            return _make_response(error=error)
        if Readers._readers[reader_id]['state'] is True:
            error = _Errors.ReaderIsConnected
            return _make_response(error=error)
        del Readers._readers[reader_id]
        return _make_response(response=0)

    @staticmethod
    def start_reader(reader_id: int):
        if reader_id not in Readers._readers:
            error = _Errors.ReaderNotExists
            return _make_response(error=error)
        if Readers._readers[reader_id]['state'] is True:
            error = _Errors.ReaderAlreadyIsConnected
            return _make_response(error=error)
        reader = Readers._readers[reader_id]
        if not isinstance(reader['reader'], Reader):
            reader['reader'] = Reader()
        r_code = reader['reader'].connect(reader['bus_addr'], reader['port_number'])
        if r_code != 0:
            error = _Errors.cast_error(*r_code)
            return _make_response(error=error)
        reader['state'] = True
        return _make_response(response=0)

    @staticmethod
    def stop_reader(reader_id: int):
        # TODO
        pass

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




    # @staticmethod
    # def contains(item):
    #     return item in Readers._readers


# noinspection PyProtectedMember
Readers._read_settings()  # инициализация настройками из файла

if __name__ == '__main__':
    Readers.add_reader('1', 1, 1)
    Readers.add_reader('2', 3, 3)
    # print(Readers.contains('2'))
    # print(Readers.contains('3'))
    # print(Readers.contains('4'))
