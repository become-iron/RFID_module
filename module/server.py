# -*- coding: utf-8 -*-
import os.path
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from logic import Readers

# Полезные ссылки:
# Representational state transfer — https://en.wikipedia.org/wiki/Representational_state_transfer

app = Flask(__name__)


@app.route('/')
def index_redirect():
    """Редирект с главной страницы на документацию"""
    return redirect(url_for('documentation'))


@app.route('/docs/', defaults={'filename': 'index.html'})
@app.route('/docs/<path:filename>')
def documentation(filename):
    # WARN не пересылается путь по адресу http://127.0.0.1:5000/docs/_static/fonts/fontawesome-webfont.woff2?v=4.6.3
    path_to_docs = '../docs/_build/html/'
    if not os.path.isdir(path_to_docs):
        return 'Документация недоступна, так как ещё не была собрана'
    return send_from_directory(
        path_to_docs,
        filename
    )


@app.route('/readers/', methods=['GET'])
def get_readers():
    """Возвращает список настроек для ридеров"""
    # curl -i -X GET http://localhost:5000/readers/
    # curl -i http://localhost:5000/readers/
    # curl -L http://localhost:5000/readers/
    # curl http://localhost:5000/readers/
    # -i возвращает информацию о странице
    # -L выполняет перенаправление
    # если перейти по адресу http://localhost:5000/readers , выполнится перенаправление на http://localhost:5000/readers/ с кодом 301

    http_code = 200  # возвращен список настроек
    response = Readers.get_readers()

    return jsonify(response), http_code


@app.route('/readers/', methods=['POST'])
def add_reader():
    """Добавляет настройки для ридера"""
    # curl -i -H "Content-Type: application/json" -X POST -d "{"""reader_id""": """1""", """bus_addr""": 1, """port_number""": 1}" http://localhost:5000/readers/

    http_code = 201     # создан новый ресурс (с настройками)
    response = Readers.add_reader(data=request.json)

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


@app.route('/readers/', methods=['PUT'])
def update_readers():
    """Заменяет все настройки ридеров переданными"""
    # curl -i -H "Content-Type: application/json" -X PUT -d "{"""bus_addr""": 23, """port_number""": 1}" http://localhost:5000/readers/

    http_code = 200     # настройки обновлены
    response = Readers.update_readers(data=request.json)

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


@app.route('/readers/', methods=['DELETE'])
def delete_readers():
    """Удаляет все настройки ридеров"""
    # curl -i -X DELETE http://localhost:5000/readers/

    http_code = 200     # настройки удалены
    response = Readers.delete_readers()

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/', methods=['GET'])
def get_reader(reader_id):
    """Возвращает настройки ридера"""
    # curl -i -X GET http://localhost:5000/readers/1/
    # curl -i http://localhost:5000/readers/1/

    http_code = 200     # возвращен список настроек
    response = Readers.get_reader(reader_id=reader_id)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/', methods=['PUT'])
def update_reader(reader_id):
    """Обновляет настройки ридера"""
    # curl -i -H "Content-Type: application/json" -X PUT -d "{"""reader_id""": """1""", """bus_addr""": 23, """port_number""": 1}" http://localhost:5000/readers/1/

    http_code = 200     # настройки обновлены
    response = Readers.update_reader(reader_id=reader_id, data=request.json)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден
        else:
            http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/', methods=['DELETE'])
def delete_reader(reader_id):
    """Удаляет ридер"""
    # curl -i -X DELETE http://localhost:5000/readers/1/

    http_code = 200     # настройки удалены
    response = Readers.delete_reader(reader_id=reader_id)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден

    return jsonify(response), http_code


# Эта функция, скорее всего, не нужна
@app.route('/readers/<reader_id>/tags/inventory/', methods=['GET'])
def inventory(reader_id):
    """Возвращает идентификаторы меток"""

    http_code = 200     # идентификаторы возвращены
    response = Readers.inventory(reader_id=reader_id)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/tags/', methods=['GET'])
def read_tags(reader_id):
    """Возвращает информацию с меток"""

    http_code = 200     # информация возвращена
    response = Readers.read_tags(reader_id=reader_id, data=request.json)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден
        else:
            http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/tags/', methods=['PUT'])
def write_tags(reader_id):
    """Записывает информацию в метки"""

    http_code = 200     # информация записана
    response = Readers.write_tags(reader_id=reader_id, data=request.json)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден
        else:
            http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


@app.route('/readers/<reader_id>/tags/', methods=['DELETE'])
def clear_tags(reader_id):
    """Очищает информацию с меток"""
    # curl -i -X DELETE http://localhost:5000/readers/tags/

    http_code = 200     # информация удалена
    response = Readers.write_tags(reader_id=reader_id, data=request.json, clear=True)

    if 'error' in response:
        if response['error']['error_code'] == 0:
            http_code = 404     # Ридер не найден
        else:
            http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify(response), http_code


if __name__ == '__main__':
    app.run(debug=True)
