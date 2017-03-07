# -*- coding: utf-8 -*-
import unittest
from requests import get, post, put, delete
import os
import server


class TestServer(unittest.TestCase):
    def test_documentation(self):
        for file in os.listdir("../docs/_build/html/"):
            if file.endswith(".html"):
                r = get('http://localhost:5000/docs/' + file)
                self.assertEqual(r.status_code, 200)

    def test_get_readers(self):
        r = get('http://localhost:5000/readers/')
        data = {"response": {}}
        for i in range(5):
            data["response"].update({str(i): {"""bus_addr""": i, """port_number""": i, """state""": False}})
        self.assertEqual(r.json(), data)

    def test_add_reader(self):
        self.test_delete_readers()
        for i in range(5):
            r = post(url='http://localhost:5000/readers/', json={"""reader_id""": str(i), """bus_addr""": i, """port_number""": i})
            self.assertEqual(r.json(), {"response": 0})
            self.assertEqual(r.status_code, 201)

    def test_delete_readers(self):
        r = get(url='http://localhost:5000/readers/')
        amount = len(r.json()['response'])

        r = delete(url='http://localhost:5000/readers/')
        if amount != 0:
            self.assertEqual(r.json(), {"response": 0})
        else:
            self.assertEqual(r.json(), {'error': {'error_code': 13, 'error_msg': 'Список ридеров уже пуст'}})

        self.assertEqual(r.status_code, 200)

    def test_get_reader(self):
        self.test_add_reader()
        for i in range(5):
            r = get(url='http://localhost:5000/readers/' + str(i))
            data = {"response": {str(i): {"""bus_addr""": i, """port_number""": i, """state""": False}}}
            self.assertEqual(r.json(), data)

    def test_update_reader(self):
        for j in range(2):
            for i in range(5):
                if j == 0:
                    number = i + 100
                else:
                    number = i
                    i += 100
                r = put(url='http://localhost:5000/readers/' + str(i) + '/',
                        json={"""bus_addr""": number, """port_number""": number})
                self.assertEqual(r.status_code, 200)
                r = put(url='http://localhost:5000/readers/' + str(i) + '/',
                        json={"""reader_id""": str(number)})
                self.assertEqual(r.status_code, 200)
                r = put(url='http://localhost:5000/readers/' + str(number) + '/',
                        json={"""state""": True})
                self.assertEqual(r.status_code, 400)
                # self.assertEqual(r.status_code, 200)

    def test_delete_reader(self):
        r = get(url='http://localhost:5000/readers/')
        amount = len(r.json()['response'])
        for i in range(5):
            r = delete(url='http://localhost:5000/readers/' + str(i) + '/')
            if amount != 0:
                self.assertEqual(r.json(), {"response": 0})
            else:
                self.assertEqual(r.json(), {'error': {'error_code': 9, 'error_msg': 'Ридера с данным идентификатором не существует'}})
            self.assertEqual(r.status_code, 200)

    def test_inventory(self):
        for i in range(5):
            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/inventory/')
            self.assertEqual(r.status_code, 200)

    def test_read_tags(self):
        for i in range(5):
            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                    json=[])
            self.assertEqual(r.status_code, 200)

            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/inventory/')
            self.assertEqual(r.status_code, 200)
            resp = r.json()['response']

            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                    json=resp)
            self.assertEqual(r.status_code, 200)

            for j in resp:
                r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                        json=list(j))
                self.assertEqual(r.status_code, 200)

    def test_write_tags(self):
        for i in range(5):
            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/inventory/')
            self.assertEqual(r.status_code, 200)
            resp = r.json()['response']
            data = {n: str(m) + ' done' for m, n in enumerate(resp)}

            r = put(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                    json=data)
            self.assertEqual(r.status_code, 200)

    def test_clear_tags(self):
        for i in range(5):
            r = delete(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                       json=[])
            self.assertEqual(r.status_code, 200)

            r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/inventory/')
            self.assertEqual(r.status_code, 200)
            resp = r.json()['response']

            r = delete(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                       json=resp)
            self.assertEqual(r.status_code, 200)

            for j in resp:
                r = get(url='http://localhost:5000/readers/' + str(i) + '/tags/',
                        json=list(j))
                self.assertEqual(r.status_code, 200)
