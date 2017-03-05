# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from logic import Readers, Errors, make_response


class TestReaders(unittest.TestCase):
    # успешное завершение операции
    success_response = {'response': 0}
    # Некорректное значение идентификатора ридера
    InvalidReaderId_response = make_response(error=Errors.InvalidReaderId)
    # Невалидное значение параметра шины адреса
    InvalidReaderBusAddr_response = make_response(error=Errors.InvalidReaderBusAddr)
    # Невалидное значение параметра номера порта
    InvalidReaderPortNumber_response = make_response(error=Errors.InvalidReaderPortNumber)
    # Ридер с данным идентификатором существует
    ReaderExists_response = make_response(error=Errors.ReaderExists)
    # Ридера с данным идентификатором не существует
    ReaderNotExists_response = make_response(error=Errors.ReaderNotExists)
    # Список ридеров уже пуст
    ReadersListAlreadyIsEmpty_response = make_response(error=Errors.ReadersListAlreadyIsEmpty)

    def setUp(self):
        pprint(Readers.get_readers())

    def tearDown(self):
        pprint(Readers.get_readers())

    def test_add_readers(self):
        amount = len(Readers.get_readers()['response'])
        if amount != 0:
            self.assertEqual(self.success_response, Readers.delete_readers())
        else:
            self.assertEqual(self.ReadersListAlreadyIsEmpty_response, Readers.delete_readers())

        for j in range(2):
            for i in range(25):
                print('i:', i, ', j:', j)
                if i in range(0, 5):
                    data = {'reader_id': str(i), 'bus_addr': i, 'port_number': i}
                    if j == 0:
                        # успешное завершение операции
                        self.assertEqual(self.success_response, Readers.add_reader(data=data))
                    else:
                        # Ридер с данным идентификатором существует
                        self.assertEqual(self.ReaderExists_response, Readers.add_reader(data=data))
                elif i in range(5, 10):
                    # Некорректное значение идентификатора ридера
                    data = {'reader_id': i, 'bus_addr': i, 'port_number': i}
                    self.assertEqual(self.InvalidReaderId_response, Readers.add_reader(data=data))
                elif i in range(10, 15):
                    # Невалидное значение параметра шины адреса
                    data = {'reader_id': str(i), 'bus_addr': str(i), 'port_number': i}
                    self.assertEqual(self.InvalidReaderBusAddr_response, Readers.add_reader(data=data))
                elif i in range(15, 20):
                    # Невалидное значение параметра шины адреса
                    data = {'reader_id': str(i), 'bus_addr': str(i), 'port_number': str(i)}
                    self.assertEqual(self.InvalidReaderBusAddr_response, Readers.add_reader(data=data))
                else:
                    # Невалидное значение параметра номера порта
                    data = {'reader_id': str(i), 'bus_addr': i, 'port_number': str(i)}
                    self.assertEqual(self.InvalidReaderPortNumber_response, Readers.add_reader(data=data))

                pprint(data)

    def test_get_reader(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            pprint(i)
            pprint(Readers.get_reader(reader_id=str(i)))

    def test_update_reader(self):
        amount = len(Readers.get_readers()['response'])
        for j in range(2):
            for i in range(amount):
                number = i + 100
                print('i:', i, ', j:', j)

                # Ридера с данным идентификатором не существует
                data = {'reader_id': str(number), 'bus_addr': i, 'port_number': i, 'state': True}
                pprint(Readers.update_reader(reader_id=str(i), data=data))
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

                # Невалидное значение параметра шины адреса
                data = {'reader_id': str(number), 'bus_addr': str(number), 'port_number': str(number), 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра шины адреса
                data = {'reader_id': str(number), 'bus_addr': str(number), 'port_number': number, 'state': False}
                self.assertEqual(self.ReaderNotExists_response, Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра номера порта
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
                self.assertEqual(self.InvalidReaderBusAddr_response, Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра шины адреса
                data = {'reader_id': str(i), 'bus_addr': str(number), 'port_number': number, 'state': False}
                self.assertEqual(self.InvalidReaderBusAddr_response, Readers.update_reader(reader_id=str(i), data=data))

                # Невалидное значение параметра номера порта
                data = {'reader_id': str(i), 'bus_addr': number, 'port_number': str(number), 'state': False}
                self.assertEqual(self.InvalidReaderPortNumber_response, Readers.update_reader(reader_id=str(i), data=data))

    def test_inventory(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            print("test_inventory", i)
            pprint(Readers.inventory(reader_id=str(i)))
            # self.assertEqual(self.success_response, Readers.inventory(reader_id=str(i)))

    def test_read_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            print("test_read_tags", i)
            data = {'tag_ids': list(range(20))[:i]}

            pprint(data)
            pprint(Readers.read_tags(reader_id=str(i), data=data))
            # self.assertEqual(self.success_response, Readers.read_tags(reader_id=str(i)))

    def test_write_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            print("test_write_tags", i)
            data = {'tag_ids': {a: a for a in list(range(100))}}
            pprint(Readers.write_tags(reader_id=str(i), data=data))
            # self.assertEqual(self.success_response, Readers.write_tags(reader_id=str(i)))

    def test_clear_tags(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            print("test_clear_tags", i)
            data = {'tag_ids': {a: a for a in list(range(100))}}
            pprint(Readers.write_tags(reader_id=str(i), data=data, clear=True), )
            # self.assertEqual(self.success_response, Readers.clear_tags(reader_id=str(i)))

    def test_delete_reader(self):
        amount = len(Readers.get_readers()['response'])
        for i in range(amount):
            self.assertEqual(self.success_response, Readers.delete_reader(reader_id=str(i)))

if __name__ == '__main__':
    unittest.main()