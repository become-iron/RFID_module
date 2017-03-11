# -*- coding: utf-8 -*-
import unittest
import logging
from logic import Readers, Errors


class TestReaders(unittest.TestCase):
    # успешное завершение операции
    success_response = {'response': 0}
    # Некорректное значение идентификатора ридера
    InvalidReaderId_response = dict(error=Errors.InvalidReaderId.to_dict())
    # Невалидное значение параметра шины адреса
    InvalidReaderBusAddr_response = dict(error=Errors.InvalidReaderBusAddr.to_dict())
    # Невалидное значение параметра номера порта
    InvalidReaderPortNumber_response = dict(error=Errors.InvalidReaderPortNumber.to_dict())
    # Ридер с данным идентификатором существует
    ReaderExists_response = dict(error=Errors.ReaderExists.to_dict())
    # Ридера с данным идентификатором не существует
    ReaderNotExists_response = dict(error=Errors.ReaderNotExists.to_dict())
    # Список ридеров уже пуст
    ReadersListAlreadyIsEmpty_response = dict(error=Errors.ReadersListAlreadyIsEmpty.to_dict())

    def log(self, func_name, data):
        result = '[{0}] Тест с ридером {1} не был проведен, так как ридер отключён'.format(func_name, data)
        logging.warning(result)

    def setUp(self):
        Readers.get_readers()

    def tearDown(self):
        Readers.get_readers()

    def test_add_readers(self):
        amount = len(Readers.get_readers()['response'])
        if amount != 0:
            self.assertEqual(self.success_response, Readers.delete_readers())
        else:
            self.assertEqual(self.ReadersListAlreadyIsEmpty_response, Readers.delete_readers())

        for j in range(2):
            for i in range(25):
                if 0 <= i < 5:
                    data = {'reader_id': str(i), 'bus_addr': i, 'port_number': i}
                    if j == 0:
                        # успешное завершение операции
                        self.assertEqual(self.success_response, Readers.add_reader(data=data))
                    else:
                        # Ридер с данным идентификатором существует
                        self.assertEqual(self.ReaderExists_response, Readers.add_reader(data=data))
                elif 5 <= i < 10:
                    # Некорректное значение идентификатора ридера
                    data = {'reader_id': i, 'bus_addr': i, 'port_number': i}
                    self.assertEqual(self.InvalidReaderId_response, Readers.add_reader(data=data))
                elif 10 <= i < 15:
                    # Невалидное значение параметра шины адреса
                    data = {'reader_id': str(i), 'bus_addr': str(i), 'port_number': i}
                    self.assertEqual(self.InvalidReaderBusAddr_response, Readers.add_reader(data=data))
                elif 15 <= i < 20:
                    # Невалидное значение параметра шины адреса
                    data = {'reader_id': str(i), 'bus_addr': str(i), 'port_number': str(i)}
                    self.assertEqual(self.InvalidReaderBusAddr_response, Readers.add_reader(data=data))
                else:
                    # Невалидное значение параметра номера порта
                    data = {'reader_id': str(i), 'bus_addr': i, 'port_number': str(i)}
                    self.assertEqual(self.InvalidReaderPortNumber_response, Readers.add_reader(data=data))

    def test_get_reader(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            self.assertEqual(Readers.get_reader(reader_id=str(i))['response'][str(i)],
                             Readers.get_readers()['response'][str(i)])

    def test_update_reader(self):
        amount = len(Readers.get_readers()['response'])
        for j in range(2):
            for i in range(amount):
                number = i + 100

                # Ридера с данным идентификатором не существует
                data = {'reader_id': str(number), 'bus_addr': i, 'port_number': i, 'state': True}
                # self.assertEqual(
                #     {'error': {'error_code': -106,
                #                'error_msg': 'Error in Module FEDM: Unknown transfer parameter or parameter value is out of valid range'}},
                #     Readers.update_reader(reader_id=str(i), data=data))
                # self.assertEqual(
                #     {'error': {'error_code': -120,
                #                'error_msg': 'Error in Module FEDM: No reader found'}},
                #     Readers.update_reader(reader_id=str(i), data=data))
                # self.assertEqual(
                #     {'error': {'error_code': -1033,
                #                'error_msg': 'FECOM: (-1033) communication process not started'}},
                #     Readers.update_reader(reader_id=str(number), data=data))

                # успешное завершение операции
                data = {'reader_id': str(number), 'bus_addr': number, 'port_number': number, 'state': False}
                self.assertEqual(self.success_response, Readers.update_reader(reader_id=str(i), data=data))

                # Ридера с данным идентификатором не существует
                data = {'reader_id': number, 'bus_addr': number, 'port_number': number, 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # Ридера с данным идентификатором не существует
                data = {'reader_id': str(number), 'bus_addr': str(number), 'port_number': str(number), 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # Ридера с данным идентификатором не существует
                data = {'reader_id': str(number), 'bus_addr': str(number), 'port_number': number, 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # Ридера с данным идентификатором не существует
                data = {'reader_id': str(number), 'bus_addr': number, 'port_number': str(number), 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # успешное завершение операции
                data = {'reader_id': str(number), 'bus_addr': number, 'port_number': number, 'state': True}
                self.assertEqual(
                    {'error': {'error_code': -1033,
                               'error_msg': 'FECOM: (-1033) communication process not started'}},
                    Readers.update_reader(reader_id=str(number), data=data))
                # self.assertEqual(self.success_response, Readers.update_reader(reader_id=str(number), data=data))

                # успешное завершение операции
                data = {'reader_id': str(i), 'bus_addr': number, 'port_number': number, 'state': False}
                self.assertEqual(self.success_response, Readers.update_reader(reader_id=str(number), data=data))

                # Некорректное значение идентификатора ридера
                data = {'reader_id': i, 'bus_addr': number, 'port_number': number, 'state': False}
                self.assertEqual(self.InvalidReaderId_response,
                                 Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра шины адреса
                data = {'reader_id': str(i), 'bus_addr': str(number), 'port_number': str(number), 'state': False}
                self.assertEqual(self.InvalidReaderBusAddr_response,
                                 Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра шины адреса
                data = {'reader_id': str(i), 'bus_addr': str(number), 'port_number': number, 'state': False}
                self.assertEqual(self.InvalidReaderBusAddr_response,
                                 Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра номера порта
                data = {'reader_id': str(i), 'bus_addr': number, 'port_number': str(number), 'state': False}
                self.assertEqual(self.InvalidReaderPortNumber_response,
                                 Readers.update_reader(reader_id=str(i), data=data))

    def test_inventory(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            if Readers[str(i)]['state'] is True:
                self.assertEqual(self.success_response, Readers.inventory(reader_id=str(i)))
            else:
                self.log(self.test_clear_tags.__name__, i)

    def test_read_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            if Readers[str(i)]['state'] is True:
                data = {'tag_ids': list(range(20))[:i]}
                self.assertEqual(self.success_response, Readers.read_tags(reader_id=str(i), data=data))
            else:
                self.log(self.test_clear_tags.__name__, i)

    def test_write_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            if Readers[str(i)]['state'] is True:
                data = {'tag_ids': {a: a for a in list(range(100))}}
                self.assertEqual(self.success_response, Readers.write_tags(reader_id=str(i), data=data))
            else:
                self.log(self.test_clear_tags.__name__, i)

    def test_clear_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            if Readers[str(i)]['state'] is True:
                data = {'tag_ids': {a: a for a in list(range(100))}}
                self.assertEqual(self.success_response, Readers.write_tags(reader_id=str(i), data=data, clear=True))
            else:
                self.log(self.test_clear_tags.__name__, i)

    def test_delete_reader(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            self.assertEqual(self.success_response, Readers.delete_reader(reader_id=str(i)))