# -*- coding: utf-8 -*-
import configparser as cp

from reader import Reader, log

__all__ = ('Readers',)


def log_pattern(msg, func_name=None, *params):
    result = ''
    if func_name is not None:
        result += '[' + func_name
    if len(params) > 0:
        result += '(' + ', '.join(map(repr, params)) + ')'
    result += '] ' + msg
    return result


def make_response(response=None, error=None) -> dict:
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
                if len(args) > 1:  # > 1, так как в методах первым аргументом всегда передаётся self
                    log.warning(log_pattern(
                        'Вызван метод без указания названий параметров, что может привести к неверной работе',
                        func.__name__))
                if (error.param is None and error.check()) \
                        or (error.param in kwargs and error.check(kwargs[error.param])):
                    # TODO сделать вывод более информативным
                    log.error(log_pattern(error.msg, func.__name__))
                    return make_response(error=error)
            return func(*args, **kwargs)
        return wrapper
    return check_decorator


class Errors:
    """Вспомогательный объект ддя хранения возникающих ошибок (кодов и описаний)"""
    # TODO попытаться привести к более красивому виду
    # TODO невозможно передавать значения, привёдшие к ошибке
    class Error:
        def __init__(self, code: int, msg: str, param=None, check=None):
            self.code = code  # код ошибки
            self.msg = msg  # текст ошибки
            self.param = param  # имя параметра, необходимого для проверки
            self.check = check  # функция для проверки (возвращает True в случае возникновения ошибки)

        def __call__(self, msg):
            # Можно использовать для передачи дополнительной информации
            # Например:
            # Errors.InvalidReaderBusAddr(bus_addr)
            new_msg = '{0} ({1})'.format(self.msg, msg)
            return Errors.Error(self.code, new_msg, self.param, self.check)

        # def __repr__(self):
        #     return 'Errors._Error(code={!r}, msg={!r}, param={!r}, check={!r})'\
        #         .format(self.code, self.msg, self.param, self.check)

        def auto_check(self, func_name, *args):
            """
            Проводит проверку и записывает в лог ошибку в случае её возникновения

            :param func_name:
            :param args:
            :return:
            """
            result = self.check(*args)
            if result:
                log.error(log_pattern(self.msg, func_name))
            return result

    InvalidReaderBusAddr = Error(
        0, 'Невалидное значение параметра шины адреса',
        'bus_addr', lambda x: not isinstance(x, int))
    InvalidReaderPortNumber = Error(
        0, 'Невалидное значение параметра номера порта',
        'port_number', lambda x: not isinstance(x, int))
    InvalidReaderState = Error(
        0, 'Невалидное значение параметра состояния ридера',
        'state', lambda x: not isinstance(x, bool))
    WrongAmountOfParams = Error(
        0, 'Неверное количество параметров',
        'data', lambda x: not all(map(lambda i: i in x, ('reader_id', 'bus_addr', 'port_number'))))
    ReaderExists = Error(
        0, 'Ридер с данным идентификатором существует',
        'reader_id', lambda x: x in Readers)
    ReaderNotExists = Error(
        0, 'Ридера с данным идентификатором не существует',
        'reader_id', lambda x: x not in Readers)
    ReaderIsConnected = Error(
        0, 'Операция не может быть совершена, так как ридер подключён',
        'reader_id', lambda x: Readers[x]['state'] is True)
    ReaderIsDisconnected = Error(
        0, 'Операция не может быть совершена, так как ридер отключён',
        'reader_id', lambda x: Readers[x]['state'] is False)
    OneOrMoreReadersAreConnected = Error(
        0, 'Операция не может совершена, так как один или больше ридеров подключены',
        None, lambda: not all(map(lambda rid: Readers[rid]['state'] is False, Readers)))
    ReadersListAlreadyIsEmpty = Error(
        0, 'Список ридеров уже пуст',
        None, lambda: len(Readers) == 0)


class _Readers:
    """Хранение настроек ридеров и их состояний"""
    def __init__(self):
        self._file = 'reader_settings.ini'
        self._readers = {}
        self._read_settings()

    def __contains__(self, item):
        return item in self._readers

    def __delitem__(self, key):
        del self._readers[key]

    def __getitem__(self, item):
        return self._readers[item]

    def __len__(self):
        return len(self._readers)

    def __iter__(self):
        yield from self._readers

    def _update(self, other: dict):
        self._readers.update(other)

    def _items(self):
        return self._readers.items()

    def _read_settings(self):
        """Читает настройки из файла. Должен быть вызван единожды при импортировании модуля"""
        settings = cp.ConfigParser()
        settings.read(self._file)
        self._update({
             reader_id: {
                'bus_addr': int(settings[reader_id]['bus_addr']),
                'port_number': int(settings[reader_id]['port_number']),
                'state': False,
                'reader': None,
             }
             for reader_id in settings if reader_id != 'DEFAULT'
        })

    def _save_settings(self):
        """Записывает настройки в файл"""
        settings = cp.ConfigParser()
        for reader_id, reader_settings in sorted(self._items(), key=lambda x: x[0]):
            settings[reader_id] = {
                'bus_addr': reader_settings['bus_addr'],
                'port_number': reader_settings['port_number']
            }
        with open(self._file, 'w') as file:
            settings.write(file)

    def get_readers(self):
        """Возвращает информацию о ридерах: идентификаторы, настройки, состояния"""
        result = {
            reader_id: {
                'bus_addr': self[reader_id]['bus_addr'],
                'port_number': self[reader_id]['port_number'],
                'state': self[reader_id]['state'],
            }
            for reader_id in self
            }
        return make_response(response=result)

    @check_for_errors(Errors.WrongAmountOfParams)
    def add_reader(self, data: dict):
        """
        Добавляет ридер
        Принимает:
            - data (dict): словарь со следущим обязательным набором ключей: reader_id, bus_addr, port_number.
              При наличии в data необязательного ключа state==True произойдёт подключениие ридера
        """
        # TODO добавить ли возможность сразу подключать ридер
        reader_id = data['reader_id']
        bus_addr = data['bus_addr']
        port_number = data['port_number']
        state = False
        reader = None
        for error, param in \
                ((Errors.ReaderExists, reader_id),
                 (Errors.InvalidReaderBusAddr, bus_addr),
                 (Errors.InvalidReaderPortNumber, port_number)):
            if error.auto_check('add_reader', param):
                return make_response(error=error)

        if 'state' in data:
            if Errors.InvalidReaderState.auto_check('add_reader', data['state']):
                return make_response(error=Errors.InvalidReaderState)
            if data['state'] is True:
                reader = Reader()
                r_code = reader.connect(bus_addr, port_number)
                if r_code != 0:
                    return make_response(error=Errors.Error(r_code, reader.get_error_text(r_code)))
                state = True

        self._update({
            reader_id: {
                'bus_addr': bus_addr,
                'port_number': port_number,
                'state': state,
                'reader': reader,
            }
        })
        self._save_settings()
        return make_response(response=0)

    def update_readers(self):
        # TODO
        pass

    @check_for_errors(Errors.ReadersListAlreadyIsEmpty, Errors.OneOrMoreReadersAreConnected)
    def delete_readers(self):
        """Удаляет ридеры"""
        self._readers = {}
        self._save_settings()
        return make_response(response=0)

    @check_for_errors(Errors.ReaderNotExists)
    def get_reader(self, reader_id: str):
        """Возвращает настройки и состояние ридера по идентификатору"""
        result = {reader_id: {
            'bus_addr': self[reader_id]['bus_addr'],
            'port_number': self[reader_id]['port_number'],
            'state': self[reader_id]['state']
        }}
        return make_response(response=result)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsConnected)
    def update_reader(self, reader_id: str, data: dict):
        """
        Обновляет настройки ридера
        Принимает:
            - reader_id (str)
            - data (dict): словарь со следущим возможным набором ключей: reader_id, bus_addr, port_number, state.
              При наличии в data ключа state произойдёт подключениие/отключение ридера
        """
        # WARN TODO CHECK: обязательно нужно протестировать хорошо
        result = {}
        # CHECK: возможно, необходимо глубокое копирование, в частности проверить возможные траблы с копированием ридера
        # копируем существующие настройки ридера
        result.update({reader_id: {key: value for key, value in self[reader_id].items()}})

        for error, param in \
                ((Errors.InvalidReaderBusAddr, 'bus_addr'),
                 (Errors.InvalidReaderPortNumber, 'port_number')):
            if param in data:
                if error.auto_check('update_reader', data[param]):
                    return make_response(error=error)
                result[reader_id][param] = data[param]

        if 'state' in data:
            state = data['state']
            if Errors.InvalidReaderState.auto_check('update_reader', state):
                return make_response(error=Errors.InvalidReaderState)
            if data['state'] is True and result[reader_id]['state'] is False:
                # ридер выключен, включаем
                reader = Reader()
                r_code = reader.connect(result[reader_id]['bus_addr'], result[reader_id]['port_number'])
                if r_code != 0:
                    return make_response(error=Errors.Error(r_code, reader.get_error_text(r_code)))
                result[reader_id]['reader'] = reader
                result[reader_id]['state'] = True
            elif data['state'] is False and result[reader_id]['state'] is True:
                # ридер включён, выключаем
                result[reader_id]['reader'].disconnect()
                result[reader_id]['reader'] = None
                result[reader_id]['state'] = False

        if 'reader_id' in data:
            new_reader_id = data['reader_id']
            if Errors.ReaderExists.auto_check('update_reader', new_reader_id):
                return make_response(error=Errors.ReaderExists)
            result[new_reader_id] = result.pop(reader_id)
            del self[reader_id]

        self._update(result)
        self._save_settings()
        return make_response(response=0)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsConnected)
    def delete_reader(self, reader_id: str):
        """Удаляет ридер"""
        del self[reader_id]
        self._save_settings()
        return make_response(response=0)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def inventory(self, reader_id: str):
        """Возвращает идентификаторы меток"""
        response = self[reader_id]['reader'].inventory()
        if isinstance(response, int):
            return make_response(error=Errors.Error(response, self[reader_id]['reader'].get_error_text(response)))
        return response

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def read_tags(self, reader_id: str):
        """Возвращает информацию с меток"""
        # TODO
        pass

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def write_tags(self, reader_id: str):
        """Записывает информацию в метки"""
        # TODO
        pass

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def clear_tags(self, reader_id: str):
        """Очищает информацию с меток"""
        # TODO
        pass


Readers = _Readers()  # WARN: объект в глобальной области видимости, через который следует работать с ридерами

if __name__ == '__main__':
    from pprint import pprint
    pprint(Readers.get_readers())
    pprint(Readers.add_reader(data=dict(reader_id='3', bus_addr=1, port_number=1)))
    pprint(Readers.add_reader(data=dict(reader_id='4', bus_addr=3, port_number=3)))
    pprint(Readers.update_reader(reader_id="3", data={"bus_addr": 50}))
    pprint(Readers.get_readers())
    pprint(Readers.delete_readers())
    pprint(Readers.delete_readers())
    # print(len(Readers))
    # pprint(Errors.__dict__)
    # print(Errors.InvalidReaderBusAddr('meow'))
