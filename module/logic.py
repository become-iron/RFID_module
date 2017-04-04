# -*- coding: utf-8 -*-
import configparser as cp
import logging

from reader import Reader

__all__ = ('Readers',)

# конфигурация логирования
# "[MODULE] LEVEL: 0000-00-00 00:00:00,000   MSG"
logging.basicConfig(format='[%(module)s] %(levelname)s: %(asctime)-15s   %(message)s', level=logging.WARNING)


def check_for_errors(*errors):
    """
    Декоратор для проверки наличия ошибок во время работы с RFID
    Применяется только к методам

    Принимает:
        - *errors (Errors.Error): ошибки, на которые необходимо провести проверку
    """
    # WARN для верной работы декоратора необходимо всегда указывать названия параметров при вызове декорируемых методов
    def check_decorator(func):
        def wrapper(self, *args, **kwargs):  # указан self, так как декоратор применяется к методам
            for error in errors:
                if len(args) > 0:
                    Errors.ArgsWithoutKeywords.log_error(func.__name__, *args, **kwargs)
                if (error.param is None and error.check()) \
                        or (error.param in kwargs and error.check(kwargs[error.param])):
                    error.log_error(func.__name__, *args, **kwargs)
                    return dict(error=error.to_dict())
            return func(self, *args, **kwargs)
        return wrapper
    return check_decorator


class Errors:
    """Вспомогательный объект для хранения возникающих ошибок (кодов и описаний)"""
    # TODO попытаться привести к более красивому виду
    class Error:
        def __init__(self, code: int, msg: str, param=None, check=None):
            self.code = code  # код ошибки
            self.msg = msg  # текст ошибки
            self.param = param  # имя параметра, необходимого для проверки
            self.check = check  # функция для проверки (возвращает True в случае возникновения ошибки)

        def __call__(self, msg=None):
            """Возвращает новый экземпляр класса Error с дополненным из параметра msg сообщением"""
            # Можно использовать для передачи дополнительной информации
            # Например:
            # Errors.InvalidReaderBusAddr(bus_addr)
            new_msg = '{0} ({1})'.format(self.msg, msg) if msg is not None else self.msg
            return Errors.Error(self.code, new_msg, self.param, self.check)

        def log_error(self, func_name, *args, **kwargs) -> None:
            """
            Производит логирование ошибки с использованием специального шаблона
            Шаблон: [func_name(params)] msg
            Принимает:
                - func_name (str): имя функции, в которой произошла ошибка
                - *args, **kwargs: данные, которые привели к ошибке
            """
            result = '[{}({})] {}'.format(
                func_name,
                ', '.join(tuple(map(repr, args)))
                + (', ' if args and kwargs else '')
                + ', '.join(tuple(map(lambda k: '{}={!r}'.format(k, kwargs[k]), kwargs))),
                self.msg
            )
            logging.warning(result)

        def auto_check(self, func_name, *args):
            """
            Проводит проверку и записывает в лог ошибку в случае её возникновения
            Для использования внутри методов класса Readers
            Принимает:
                - func_name (str, необяз.): имя функции, в которой произошла ошибка
                - *args: параметры, при которых необходимо провести проверку
            """
            result = self.check(*args)
            if result:
                self('AUTOCHECK').log_error(func_name, *args)
            return result

        def to_dict(self) -> dict:
            return {'error_code': self.code, 'error_msg': self.msg}

    InvalidRequest = Error(
        0, 'Некорректный запрос'
    )
    InvalidParameterSet = Error(
        1, 'Некорректный набор параметров',
        'data', lambda x: not all(map(lambda i: i in x, ('reader_id', 'bus_addr', 'port_number'))))
    InvalidReaderId = Error(
        2, 'Некорректное значение идентификатора ридера',
        'reader_id', lambda x: not isinstance(x, str)
    )
    InvalidReaderBusAddr = Error(
        3, 'Некорректное значение параметра шины адреса',
        'bus_addr', lambda x: not isinstance(x, int) or not (0 <= x <= 255))
    InvalidReaderPortNumber = Error(
        4, 'Некорректное значение параметра номера порта',
        'port_number', lambda x: not isinstance(x, int))
    InvalidReaderState = Error(
        5, 'Некорректное значение параметра состояния ридера',
        'state', lambda x: not isinstance(x, bool))
    InvalidTagId = Error(
        6, 'Некорректное значение идентификатора метки')
    InvalidTagData = Error(
        7, 'Некорректное значение данных для записи в метку')
    ReaderExists = Error(
        8, 'Ридер с данным идентификатором существует',
        'reader_id', lambda x: x in Readers)
    ReaderNotExists = Error(
        9, 'Ридера с данным идентификатором не существует',
        'reader_id', lambda x: x not in Readers)
    ReaderIsConnected = Error(
        10, 'Операция не может быть совершена, так как ридер подключён',
        'reader_id', lambda x: Readers[x].connected is True)
    ReaderIsDisconnected = Error(
        11, 'Операция не может быть совершена, так как ридер отключён',
        'reader_id', lambda x: Readers[x].connected is False)
    OneOrMoreReadersAreConnected = Error(
        12, 'Операция не может совершена, так как один или больше ридеров подключены',
        None, lambda: not all(map(lambda rid: Readers[rid].connected is False, Readers)))
    ReadersListAlreadyIsEmpty = Error(
        13, 'Список ридеров уже пуст',
        None, lambda: len(Readers) == 0)
    # ошибка для внутренней работы (только для вывода в лог)
    # TODO если работа будет осуществляться не через WebAPI, то должно быть передано: передавать в любом случае?
    ArgsWithoutKeywords = Error(
        100, 'Вызван метод без указания названий параметров, что может привести к неверной работе')


class _Readers:
    """Хранение настроек ридеров и их состояний"""
    def __init__(self):
        self.file = 'reader_settings.ini'  # путь к файлу с настройками ридеров
        # вид поля _readers:
        # {'идентификатор_ридера': Reader(1, 1),
        # ...}
        self._readers = {}
        self._read_settings()  # чтение настроек из файла при инициализации

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
        """Читает настройки из файла"""
        settings = cp.ConfigParser()
        settings.read(self.file)
        self._update({
             reader_id: Reader(
                 int(settings[reader_id]['bus_addr']),
                 int(settings[reader_id]['port_number'])
             )
             for reader_id in settings if reader_id != 'DEFAULT'
        })

    def _save_settings(self):
        """Записывает настройки в файл"""
        settings = cp.ConfigParser()
        for reader_id, reader in sorted(self._items(), key=lambda x: x[0]):
            settings[reader_id] = {
                'bus_addr': reader.bus_addr,
                'port_number': reader.port_number
            }
        with open(self.file, 'w') as file:
            settings.write(file)

    def get_readers(self):
        """Возвращает информацию о ридерах: идентификаторы, настройки, состояния"""
        result = {
            reader_id: {
                'bus_addr': self[reader_id].bus_addr,
                'port_number': self[reader_id].port_number,
                'state': self[reader_id].connected,
            }
            for reader_id in self
            }
        return dict(response=result)

    @check_for_errors(Errors.InvalidParameterSet)
    def add_reader(self, data: dict):
        """
        Добавляет ридер
        Принимает:
            - data (dict): словарь со следущим обязательным набором ключей: reader_id, bus_addr, port_number.
              При наличии в data необязательного ключа state==True произойдёт подключениие ридера
        """
        func_name = 'add_reader'

        reader_id = data['reader_id']
        bus_addr = data['bus_addr']
        port_number = data['port_number']

        for error, param in \
                ((Errors.ReaderExists, reader_id),
                 (Errors.InvalidReaderId, reader_id),
                 (Errors.InvalidReaderBusAddr, bus_addr),
                 (Errors.InvalidReaderPortNumber, port_number)):
            if error.auto_check(func_name, param):
                return dict(error=error.to_dict())

        reader = Reader(bus_addr, port_number)

        if 'state' in data:
            state = data['state']
            error = Errors.InvalidReaderState
            if error.auto_check(func_name, state):
                return dict(error=error.to_dict())
            if state:
                r_code = self[reader_id].connect()
                if r_code != 0:
                    error = Errors.Error(r_code, reader.get_error_text(r_code))
                    error.log_error('add_reader', data=data)
                    return dict(error=error.to_dict())

        self._update({reader_id: reader})

        self._save_settings()
        return dict(response=0)

    @check_for_errors(Errors.OneOrMoreReadersAreConnected)
    def update_readers(self, data: dict):
        """Заменяет все настройки ридеров переданными"""
        responses = {}
        errors = {}

        for reader_id in data:
            response = Readers.update_reader(reader_id=reader_id, data=data[reader_id])
            if 'error' in response:
                errors.update({reader_id: response['error']})
            else:
                responses.update({reader_id: response['response']})

        return dict(error=errors, response=responses)

    @check_for_errors(Errors.ReadersListAlreadyIsEmpty, Errors.OneOrMoreReadersAreConnected)
    def delete_readers(self):
        """Удаляет ридеры"""
        self._readers = {}
        self._save_settings()
        return dict(response=0)

    @check_for_errors(Errors.ReaderNotExists)
    def get_reader(self, reader_id: str):
        """Возвращает настройки и состояние ридера по идентификатору"""
        result = {reader_id: {
            'bus_addr': self[reader_id].bus_addr,
            'port_number': self[reader_id].port_number,
            'state': self[reader_id].connected,
        }}
        return dict(response=result)

    @check_for_errors(Errors.ReaderNotExists)
    def update_reader(self, reader_id: str, data: dict):
        """
        Обновляет настройки ридера
        Принимает:
            - reader_id (str)
            - data (dict): словарь со следущим возможным набором ключей: reader_id, bus_addr, port_number, state.
              При наличии в data ключа state произойдёт подключениие/отключение ридера
        """
        func_name = 'update_reader'

        # если в запросе нет ни одного параметра на обновление
        if all(map(lambda x: x not in data, ('reader_id', 'bus_addr', 'port_number', 'state'))):
            error = Errors.InvalidParameterSet
            error.log_error(func_name, reader_id=reader_id, data=data)
            return dict(error=error.to_dict())

        for error, param in (
                (Errors.ReaderExists, 'reader_id'),
                (Errors.InvalidReaderId, 'reader_id'),
                (Errors.InvalidReaderBusAddr, 'bus_addr'),
                (Errors.InvalidReaderPortNumber, 'port_number'),
                (Errors.InvalidReaderState, 'state'),):
            if param in data:
                if error.auto_check(func_name, data[param]):
                    return dict(error=error.to_dict())

        reader = self[reader_id]
        connected = reader.connected

        if connected and 'state' in data and not data['state']:  # отключить
            self[reader_id].disconnect()
            connected = False

        # попытка обновить параметры включенного ридера
        if connected and ('reader_id' in data or 'bus_addr' in data or 'port_number' in data):
            print(connected, reader_id, data, self._readers, sep='\n')
            error = Errors.ReaderIsConnected
            error.log_error(func_name, reader_id=reader_id, data=data)
            return dict(error=error.to_dict())

        if not connected:
            if 'reader_id' in data:
                new_reader_id = data['reader_id']
                self._update({new_reader_id: self._readers.pop(reader_id)})
                reader_id = new_reader_id
                reader = self[reader_id]
            if 'bus_addr' in data:
                reader.bus_addr = data['bus_addr']
            if 'port_number' in data:
                reader.port_number = data['port_number']

        if not connected and 'state' in data and data['state']:  # подключить
            r_code = self[reader_id].connect()
            if r_code != 0:
                error = Errors.Error(r_code, reader.get_error_text(r_code))
                error.log_error(func_name, reader_id=reader_id, data=data)
                return dict(error=error.to_dict())

        self._save_settings()
        return dict(response=0)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsConnected)
    def delete_reader(self, reader_id: str):
        """Удаляет ридер"""
        del self[reader_id]
        self._save_settings()
        return dict(response=0)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def inventory(self, reader_id: str):
        """Возвращает идентификаторы меток"""
        reader = self[reader_id]
        response = reader.inventory()
        if isinstance(response, int):  # произошла ошибка
            error = Errors.Error(response, reader.get_error_text(response))
            error.log_error('inventory', reader_id=reader_id)
            return dict(error=error.to_dict())
        return dict(response=response)

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def read_tags(self, reader_id: str, data: dict):
        """
        Возвращает информацию с меток
        Если в параметре data отсутствует поле data, произойдёт
        считывание с меток, находящихся в зоне действия антенны

        Требуемый формат параметра data:
            ['1', '2', '3', ...]
        """
        # TEMP нужно будет определиться с форматом данных на метках
        reader = self[reader_id]

        # WARN если в запросе по ключу "data" будет пустой массив, ничего не вернётся
        if data:
            # TODO валидация значений меток
            tag_ids = data
        else:
            tag_ids = reader.inventory()
            if isinstance(tag_ids, int):
                error = Errors.Error(tag_ids, reader.get_error_text(tag_ids))
                error.log_error('read_tags', reader_id=reader_id, data=data)
                return dict(error=error.to_dict())

        responses = {}
        errors = {}
        for tag_id in tag_ids:
            response = reader.read_tag(tag_id)
            if isinstance(response, int):
                errors.update({tag_id: {'error_code': response, 'error_msg': reader.get_error_text(response)}})
            else:
                responses.update({tag_id: response})

        result = {}

        if responses:
            result.update(dict(response=responses))
        if errors:
            result.update(dict(error=errors))

        return result

    @check_for_errors(Errors.ReaderNotExists, Errors.ReaderIsDisconnected)
    def write_tags(self, reader_id: str, data: dict, clear=False):
        """
        Записывает информацию в метки
        Принимает:
            - reader_id (str)
            - data (dict): информация для записи на метки
            - clear (bool): нужно ли очистить информацию вместо записи

        Требуемый формат параметра data:
            {
                '1': '213',
                '2': 'sdf',
                ...
            }
            или для очистки
            [
                '1',
                '2',
                ...
            ]
        """
        # TEMP нужно будет определиться с форматом данных на метках
        reader = self[reader_id]

        # TODO валидация значений меток

        responses = {}
        errors = {}
        for tag_id in data:
            if clear:
                tag_data = ''  # пустая строка для записи в метку
            else:
                tag_data = data[tag_id]
            r_code = reader.write_tag(tag_id, tag_data)  # TEMP
            if r_code != 0:
                error = Errors.Error(r_code, reader.get_error_text(r_code))
                error.log_error('write_tags', reader_id=reader_id, tag_id=tag_id, tag_data=tag_data)
                errors.update({tag_id: {'error_code': r_code, 'error_msg': reader.get_error_text(r_code)}})
            else:
                responses.update({tag_id: r_code})

        result = {}
        if responses:
            result.update(dict(response=responses))
        if errors:
            result.update(dict(error=errors))

        return result


Readers = _Readers()  # WARN: объект в глобальной области видимости, через который следует работать с ридерами
