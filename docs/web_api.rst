Web API - server.py
===================

Принципы работа с API
---------------------

API создавалось согласно архитектурному стилю RESTful API.


Формат запроса
^^^^^^^^^^^^^^

Запросы, предназначенные для определённых ридеров, должны иметь в себе идентификатор ридера.

При выполнении запроса, требующие некоторые данные, эти данные нужно отправлять в формате json.


Формат ответа
^^^^^^^^^^^^^

В качестве ответа на запросы выступают данные в формате json.

Общий формат ответа:

.. code-block:: json

    {
        "response": "какие-то данные"
    }

В качестве значения по ключу "response" может выступать любые типы данных JSON.

При наличии ошибки (в общем случае):

.. code-block:: json

    {
        "error": {
            "error_code": 0,
            "error_msg": "Описание ошибки"
        }
    }

.. note::

    Может быть и такое, что в ответе будут присутствовать оба ключа.

    В зависимости от вызываемого метода формат ответа может отличаться от представленных выше.
    Поэтому также необходимо изучить информацию по каждому из используемых запросов.


Начало работы с API
^^^^^^^^^^^^^^^^^^^

1.  Перед начало работы с ридерами нужно получить данные о уже существующих ридерах: так как настройки сохраняются после
    каждой манипуляции с ними, то может оказаться так, что RFID-модуль будет стартовать полученными ранее данными.

    :http:get:`/readers/` — получение данных о ридерах

2.  Подготовить ридеры к работе

    - Добавить новый ридер: :http:post:`/readers/`
    - Обновить настройки ридера: :http:put:`/readers/<reader_id>/`
    - Если необходимо заменить все настройками ридеров своими: :http:put:`/readers/`

3.  Изменение состояния ридера

    Подключение/отключение ридера может производиться с помощью методов :http:post:`/readers/`,
    :http:put:`/readers/<reader_id>/`, :http:put:`/readers/` при обязательном наличии ключу "state"==true в теле
    запроса

    .. note:: После завершения работы с ридером, его необходимо отключить (но это не точно)

    .. warning:: Важно замечание: невозможно изменить настройки ридера или удалить его, пока он подключен

4.  Работа с метками осуществляется с помощью методов:

    - :http:get:`/readers/<reader_id>/tags/inventory/`
    - :http:get:`/readers/<reader_id>/tags/`
    - :http:put:`/readers/<reader_id>/tags/`
    - :http:delete:`/readers/<reader_id>/tags/`

.. warning:: При вызове методов не забывайте указывать слэш ("/") в конце запроса


Система ошибок
^^^^^^^^^^^^^^

Ниже представлен список ошибок, которые могут возникнуть в ходе работы программы:

=====  =======================================================================
Номер  Описание
=====  =======================================================================
<0     [Ошибки на уровне ридера (FEIG SDK)]
0      Некорректный запрос
1      Неверное количество параметров
2      Некорректное значение идентификатора ридера
3      Некорректное значение параметра шины адреса
4      Некорректное значение параметра номера порта
5      Некорректное значение параметра состояния ридера
6      Некорректное значение идентификатора метки
7      Некорректное значение данных для записи в метку
8      Ридер с данным идентификатором существует
9      Ридера с данным идентификатором не существует
10     Операция не может быть совершена, так как ридер подключён
11     Операция не может быть совершена, так как ридер отключён
12     Операция не может совершена, так как один или больше ридеров подключены
13     Список ридеров уже пуст
100    Вызван метод без указания названий параметров (внутренняя ошибка)
=====  =======================================================================



Разное
------

.. http:get:: /

    Главная страница с описанием API



Управление ридерами
-------------------

.. http:get:: /readers/

    Возвращает список настроек и состояний ридеров

    **Пример запроса**:

    .. sourcecode:: http

        GET /readers/ HTTP/1.1

    **Примеры ответа**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": {
                "2": {
                    "bus_addr": 1,
                    "port_number": 1,
                    "state": false
                },
                "3": {
                    "bus_addr": 50,
                    "port_number": 1,
                    "state": true
                }
            }
        }

    Если нет ни одного ридера:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": {}
        }

    :statuscode 200: нет ошибок


.. http:post:: /readers/

    Добавляет настройки для ридера. При наличии в data необязательного ключа state==True произойдёт подключениие ридера

    **Пример запроса**:

    .. sourcecode:: http

        POST /readers/ HTTP/1.1
        Content-Type: application/json

        {
            "reader_id": "1",
            "bus_addr": 1,
            "port_number": 1
        }

    **Примеры ответа**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    Если отправлено параметров меньше, чем необходимо, или названия параметров некорректны:

    .. sourcecode:: http

        HTTP/1.0 400 BAD REQUEST
        Content-Type: application/json

        {
          "error": {
            "error_code": 1,
            "error_msg": "Неверное количество параметров"
          }
        }

    .. sourcecode:: http

        HTTP/1.0 400 BAD REQUEST
        Content-Type: application/json

        {
            "error": {
                "error_code": 8,
                "error_msg": "Ридер с данным идентификатором существует"
            }
        }

    :statuscode 200: нет ошибок
    :statuscode 400: ошибка в запросе, ошибки в названиях полей, передан не json

    :Возможные ошибки: 1, 2, 3, 4, 8


.. http:put:: /readers/

    Заменяет все настройки ридеров переданными

    > NOT IMPLEMENTED YET


.. http:delete:: /readers/

    Удаляет все настройки ридеров

    **Пример запроса**:

    .. sourcecode:: http

        DELETE /readers/ HTTP/1.1

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    :statuscode 204: настройки удалены

    :Возможные ошибки: 12, 13



Управление отдельным ридером
----------------------------

.. http:get:: /readers/<reader_id>/

    Возвращает настройки и состояние ридера

    **Пример запроса**:

    .. sourcecode:: http

        GET /readers/1/ HTTP/1.1

    **Пример ответа**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": {
                "1": {
                    "bus_addr": 255,
                    "port_number": 1,
                    "state": false
                }
            }
        }

    :statuscode 200: возвращены настройки
    :statuscode 404: ридер не найден

    :Возможные ошибки: 9


.. http:put:: /readers/<reader_id>/

    Обновляет настройки и состояние ридера

    **Пример запроса**:

    .. sourcecode:: http

        PUT /readers/1/ HTTP/1.1
        Content-Type: application/json

        {
            "bus_addr": 255,
            "port_number": 1,
        }

    **Пример ответа**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    :statuscode 200: настройки обновлены
    :statuscode 400: ошибка в запросе, ошибки в названиях полей, передан не json
    :statuscode 404: ридер не найден

    :Возможные ошибки:  <0, 2, 3, 4, 5, 8, 9, 10


.. http:delete:: /readers/<reader_id>/

    Удаляет ридер

    **Пример запроса**:

    .. sourcecode:: http

        DELETE /readers/1/ HTTP/1.1

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    :statuscode 200: настройки удалены
    :statuscode 404: ридер не найден

    :Возможные ошибки:  9, 10



Работа с метками
----------------

.. http:get:: /readers/<reader_id>/tags/inventory/

    Возвращает идентификаторы меток

    **Пример запроса**:

    .. sourcecode:: http

        GET /readers/1/tags/inventory/ HTTP/1.1

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": ["meow", "woof"]
        }

    :statuscode 200: идентификаторы возвращены
    :statuscode 404: ридер не найден

    :Возможные ошибки:  <0, 9, 11


.. http:get:: /readers/<reader_id>/tags/

    Возвращает информацию с меток

    **Пример запроса**:

    .. sourcecode:: http

        GET /readers/1/tags/ HTTP/1.1
        Content-Type: application/json

        [
            "meow",
            "woof"
        ]

    Если в параметре data отсутствует поле data, произойдёт считывание с меток, находящихся в зоне действия антенны:

    .. sourcecode:: http

        GET /readers/1/tags/ HTTP/1.1

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": {
                "meow": "Vasya",
                "woof": "Kys-kys-kys"
            }
        }

    :statuscode 200: информация возвращена
    :statuscode 400: ошибка в запросе, передан не json
    :statuscode 404: ридер не найден

    :Возможные ошибки:  <0, 9, 11


.. http:put:: /readers/<reader_id>/tags/

    Записывает информацию в метки

    **Пример запроса**:

    .. sourcecode:: http

        PUT /readers/1/tags/ HTTP/1.1
        Content-Type: application/json

        {
            "meow": "Vasya",
            "woof": "Kys-kys-kys"
        }

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    :statuscode 200: информация записана
    :statuscode 400: ошибка в запросе, ошибки в названиях полей, передан не json
    :statuscode 404: ридер не найден

    :Возможные ошибки:  <0, 9, 11


.. http:delete:: /readers/<reader_id>/tags/

    Очищает информацию с меток

    **Пример запроса**:

    .. sourcecode:: http

        DELETE /readers/1/tags/ HTTP/1.1
        Content-Type: application/json

        [
            "meow",
            "woof"
        ]

    **Пример ответа**:

    .. TODO

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "response": 0
        }

    :statuscode 200: информация удалена
    :statuscode 400: ошибка в запросе, ошибки в названиях полей, передан не json
    :statuscode 404: ридер не найден

    :Возможные ошибки:  <0, 9, 11
