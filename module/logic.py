# -*- coding: utf-8 -*-
import configparser as cp

from reader import Reader, log

__all__ = ('Readers',)


def make_response(response=None, error=None, error_params=None) -> dict:
    """
    Формулирует ответ на запрос
    Принимает:
        - response: данные, которые необходимо вернут
        - error (Errors.Error): ошибка
        - error_params: какие-либо данные/параметры, которые могли привести к ошибке
    """
    result = {}
    if response is not None:
        result.update({'response': response})
    if error is not None:
        result.update({'error': {'error_code': error.code, 'error_msg': error.msg}})
        if error_params is not None:
            result['error'].update({'error_params': error_params})
    return result


def check_for_errors(*errors):
    """
    Декоратор для проверки наличия ошибок во время работы с RFID
    Применяется только к методам
    """
    # WARN для верной работы декоратора необходимо всегда указывать названия параметров при вызове декорируемых методов
    def check_decorator(func):
        def wrapper(self, *args, **kwargs):  # self, так как декоратор применяется к методам
            for error in errors:
                if len(args) > 0:
                    log.warning(Errors.ArgsWithoutKeywords.log(func.__name__))
                if (error.param is None and error.check()) \
                        or (error.param in kwargs and error.check(kwargs[error.param])):
                    # TODO сделать вывод более информативным
                    log.error(error.log(func.__name__))
                    return make_response(error=error)
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
            # Можно использовать для передачи дополнительной информации
            # Например:
            # Errors.InvalidReaderBusAddr(bus_addr)
            new_msg = '{0} ({1})'.format(self.msg, msg) if msg is not None else self.msg
            return Errors.Error(self.code, new_msg, self.param, self.check)

        def log(self, func_name=None, *params) -> str:
            """
            Возвращает строку, специально подготовленную для логирования
            Шаблон: [func_name(params)] msg
            Принимает:
                - func_name (str, необяз.): имя функции, в которой произошла ошибка
                - *params: данные, которые привели к ошибке
            """
            result = ''
            if func_name is not None:
                result += '[' + func_name
            if len(params) > 0:
                result += '(' + ', '.join(map(repr, params)) + ')'
            result += '] ' + self.msg
            return result

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
                log.error(self.log(func_name))
            return result

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
        6, 'Некорректное значение идентификатора метки')  # TODO возможно, не понадобится
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
        'reader_id', lambda x: Readers[x]['state'] is True)
    ReaderIsDisconnected = Error(
        11, 'Операция не может быть совершена, так как ридер отключён',
        'reader_id', lambda x: Readers[x]['state'] is False)
    OneOrMoreReadersAreConnected = Error(
        12, 'Операция не может совершена, так как один или больше ридеров подключены',
        None, lambda: not all(map(lambda rid: Readers[rid]['state'] is False, Readers)))
    ReadersListAlreadyIsEmpty = Error(
        13, 'Список ридеров уже пуст',
        None, lambda: len(Readers) == 0)
    # ошибка для внутренней работы (только для вывода в лог)
    ArgsWithoutKeywords = Error(
        100, 'Вызван метод без указания названий параметров, что может привести к неверной работе')


class _Readers:
    """Хранение настроек ридеров и их состояний"""
    def __init__(self):
        self._file = 'reader_settings.ini'  # путь к файлу с настройками ридеров
        # вид поля _readers:
        # {'идентификатор_ридера': {
        #     'bus_addr': 0,  # адрес шины (int)
        #     'port_number': 0,  # номер COM-порта (int)
        #     'state': False,  # подключён или отключён ридер (bool): True - подключён, False - отключён
        #     'reader': None,  # объект ридера (Reader) или None, если ридер отключён
        # },
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

    @check_for_errors(Errors.InvalidParameterSet)
    def add_reader(self, data: dict):
        """
        Добавляет ридер
        Принимает:
            - data (dict): словарь со следущим обязательным набором ключей: reader_id, bus_addr, port_number.
              При наличии в data необязательного ключа state==True произойдёт подключениие ридера
        """
        # TODO добавить ли возможность сразу подключать ридер
        # TODO такую ли структуру надо использовать?
        reader_id = data['reader_id']
        bus_addr = data['bus_addr']
        port_number = data['port_number']
        state = False
        reader = None
        for error, param in \
                ((Errors.ReaderExists, reader_id),
                 (Errors.InvalidReaderId, reader_id),
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

    @check_for_errors(Errors.OneOrMoreReadersAreConnected)
    def update_readers(self, data: dict):
        """Заменяет все настройки ридеров переданными"""
        # TODO
        return make_response(error=Errors.Error(100500, 'Not Implemented'))
        # проводим валидация новых данных
        # if 'reader_ids' not in data:
        #     return make_response()
        # удаляем старые данные
        # self._readers = {}
        # устанавливаем новые данные

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
        # TODO подумать, можно ли привести к виду получше
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

        if 'reader_id' in data \
                and data['reader_id'] != reader_id:  # проверка на случай, если новый id совпадает со старым
            new_reader_id = data['reader_id']
            if Errors.InvalidReaderId.auto_check('update_reader', new_reader_id):
                return make_response(error=Errors.InvalidReaderId)
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
        reader = self[reader_id]['reader']
        response = reader.inventory()
        if isinstance(response, int):
            return make_response(error=Errors.Error(response, reader.get_error_text(response)))
        return make_response(response=response)

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
        reader = self[reader_id]['reader']

        if 'tag_ids' in data:
            # TODO валидация значений меток
            tag_ids = data['tag_ids']
        else:
            tag_ids = reader.inventory()
            if isinstance(tag_ids, int):
                return make_response(error=Errors.Error(tag_ids, reader.get_error_text(tag_ids)))

        result = {}
        errors = {}
        for tag_id in tag_ids:
            response = reader.read_tag(tag_id)
            if isinstance(response, int):
                errors.update({tag_id: {'error_code': response, 'error_msg': reader.get_error_text(response)}})
            else:
                result.update({tag_id: response})

        result = None if len(result) == 0 else result
        errors = None if len(errors) == 0 else errors

        return make_response(response=result, error=errors)

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
        """
        # WARN из-за того, что для очистки меток не используется отдельная \
        # WARN функция, при логировании будет выходить название этой

        # TEMP нужно будет определиться с форматом данных на метках
        reader = self[reader_id]['reader']

        # TODO валидация значений меток

        result = {}
        errors = {}
        for tag_id in data:
            if clear:
                tag_data = ''  # TEMP TODO какие-то данные для очистки меток
            else:
                tag_data = data[tag_id]
            r_code = reader.write_tag(tag_id, tag_data)  # TEMP
            if r_code != 0:
                errors.update({tag_id: {'error_code': r_code, 'error_msg': reader.get_error_text(r_code)}})
            else:
                result.update({tag_id: r_code})

        result = None if len(result) == 0 else result
        errors = None if len(errors) == 0 else errors

        return make_response(response=result, error=errors)


Readers = _Readers()  # WARN: объект в глобальной области видимости, через который следует работать с ридерами

if __name__ == '__main__':
    from pprint import pprint
    pprint(Readers.get_readers())
    Readers.add_reader(data=dict(reader_id="1", bus_addr=1, port_number=1))
    Readers.add_reader(data=dict(reader_id="2", bus_addr=1, port_number=1))
    pprint(Readers.add_reader(data=dict(reader_id='3', bus_addr=1, port_number=1)))
    pprint(Readers.add_reader(data=dict(reader_id='4', bus_addr=3, port_number=3)))
    pprint(Readers.update_reader(reader_id="3", data={"bus_addr": 50}))
    pprint(Readers.get_readers())
    # pprint(Readers.delete_readers())
    # pprint(Readers.delete_readers())
    # print(len(Readers))
    # pprint(Errors.__dict__)
    # print(Errors.InvalidReaderBusAddr('meow'))

