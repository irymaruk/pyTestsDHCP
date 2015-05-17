Документация к модулю pyTestDHCP
********************************

Описание модуля
---------------
Модуль предназначен для выполнения функциональных тестов DHCP сервера.

Описание API:
-------------

.. toctree::
   :maxdepth: 2

   api

Структура модуля:
-----------------
::

    pyTestsDHCP
        [docs]
            [build]
                [html]
                    index.html - документация
        [src]         - библиотеки
        basic_test.py - файл тестовых сценариев (test_*.py или *_test.py)
        config.json   - конфигурационные параметры, тестовые данные
        conftest.py   - дефолтные параметры pytest
        start.bat     - запуск тестов
        packets.log   - лог DHCP-пакетов
        test_flow.log - лог тестового сценария

Пример конфигурационного файла
------------------------------
Файл конфигурации записан в формате `json <http://www.json.org/json-ru.html>`_.
::

    {
      "using_config": "QA",

      "GlobalParams" : {
        "implicitly_time_wait": 5
      },

      "RelayAgents": {
          "mx1": "192.168.80.165",
          "mx2": "127.0.0.1"
        },

      "QA" : {
        "DhcpSrv": "192.168.81.173",

        "Users": {
          "user1": {
            "Agent_Circuit_ID": "ISKRATEL:kv-257-1019 atm 3/2:1.40",
            "Agent_Remote_ID": "",
            "chaddr": "FF:11:22:33:44:55"
          },
          "user2": {
            "Agent_Circuit_ID": "ISKRATEL:kv-257-1019 atm 3/5:1.40",
            "Agent_Remote_ID": "",
            "chaddr": "FF:11:22:33:44:55"
          }
        }
      },

      "DEV": {
        "DhcpSrv": "192.168.81.96",

        "Users": {
          "user1": {
            "Agent_Circuit_ID": "ISKRATEL:kv-257-1019 atm 3/1:1.40",
            "Agent_Remote_ID": "",
            "chaddr": "FF:11:22:33:44:56"
          }
        }
      }
    }

Основные параметры:

 - *using_config* -- какой из описаных далее словарей использовать. Предназначен для удобного переключения между
   тестовыми стендами.
 - *implicitly_time_wait* -- время в секундах ожидания ответного пакета на последний отпраленный запрос.
 - *RelayAgents* -- список локальных интерфейсов (на сервере где запускается тест), которые выполняют роль Relay агентов
   (Juniper MX).
 - *QA* / *DEV* -- имя тестового стенда. Предназначено для групировки специфических для каждого стенда параметров.
 - *DhcpSrv* -- адрес DHCP сервера
 - *Users* -- список тестовых пользователей и их дефолтные параметры

.. note::

    Если на сервере где выполняется тест есть два интерфейса, то можно отправлять пакеты и ожидать ответ через
    определенный интерфейс.


Пример сценария
---------------

Следующий код выполняет такие действия:
 - создем пользователя с параметрами установленными в config.json для "user1"
 - в пакет, подготовленный к отправке, вместо дефолтной устанавливаем свою опцию 82
 - отправляем пакет (ждем ответа в течении 5 сек)
 - из полученного ответа Offer создаем Request Select и отправляем
 - ожидаем половину времени аренды адреса
 - на основании последнего отправленного Request Select создаем Request Renew и отправляем
 - пять раз повторно отправляем последний Request Renew (с ожиданием ответа)
 - на основании последнего отправленного Request Select создаем Release
 - выполняем отправку пакета без ожидания ответа

::

    import pytest
    from src.user import User

    def test_2():
        user = User()
        user.create_discover_packet()
        user.set_packet_opt82('ISKRATEL:kv-257-1019 atm 3/77:1.40')
        user.send_packet()
        user.convert_offer_to_request_select()
        user.send_packet()
        lease_time = user.get_last_offer_lease_time()
        user.wait(lease_time/2)
        user.convert_request_select_to_renew()
        user.send_packet()
        user.resend_last_renew(5)
        user.convert_request_select_to_release()
        user.send_packet(wait_replay=False)

Запуск
------
Запуск тестов выполняется через start.bat. который вызывает модуль `pytest <http://pytest.org/latest/>`_

.. note::
    Поиск тестов выполняется следующим образом: рекурсивно по всем каталогам, начиная от текущего, ищим модули (файлы)
    а в них класы и функции имя которых подходит под test_* или *_test.
    Ключ -k переопределяет патерн поиска файлов, например на "test_2"

Логирование
-----------

Во время выполнения теста формируется (дописывается) лог файл test_flow.log в котором фиксируются все выполненные
действия клиента, отправленные и полученные пакеты и т.д.
Та же информация дублируется на консоль.

Дополнительно формируется файл packets.log, в которм фиксируются все отправленные и принятые DHCP-пакеты.

Пример файла test_flow.log:
+++++++++++++++++++++++++++
::

    2015-05-16 21:18:45,516 : INFO :

         ##########   NEW TEST SESSION STARTED   ##########

    2015-05-16 21:18:45,516 : INFO : Test "basic_test.test_2" started
    2015-05-16 21:18:45,517 : INFO : MX ip = 192.168.80.165 ready for sending packets to DHCP server ip = 192.168.81.96
    2015-05-16 21:18:45,517 : INFO : MX ip = 127.0.0.1 ready for sending packets to DHCP server ip = 192.168.81.96
    2015-05-16 21:18:45,519 : INFO : Default User params {'Agent_Circuit_ID': 'ISKRATEL:kv-257-1019 atm 3/2:1.40', 'chaddr': 'FF:11:22:33:44:55', 'Agent_Remote_ID': ''}
    2015-05-16 21:18:45,519 : INFO : User created with name = "user1"
    2015-05-16 21:18:45,519 : INFO : Discover packet with default user params created
    2015-05-16 21:18:45,519 : INFO : Set option "option 82" as = "ISKRATEL:kv-257-1019 atm 3/77:1.40"
    2015-05-16 21:18:45,519 : INFO : "user1" send DISCOVER with new xid = 1291845632
    2015-05-16 21:18:46,019 : INFO : Receive packet OFFER with xid = 1291845632
    2015-05-16 21:18:46,020 : INFO : Last Offer packet with xid = 1291845632 converted to Request Select and ready to send
    2015-05-16 21:18:46,023 : INFO : "user1" send REQUEST with new xid = 1308622848
    2015-05-16 21:18:46,523 : INFO : Receive packet ACK with xid = 1308622848
    2015-05-16 21:18:46,525 : INFO : Last Offer receive Lease time = 120
    2015-05-16 21:18:46,525 : INFO : Start waiting for 6 seconds...
    2015-05-16 21:18:52,525 : INFO : Stop waiting
    2015-05-16 21:18:52,526 : INFO : Last Request Select packet with xid = 1308622848 converted to Request Renew and ready to send
    2015-05-16 21:18:52,529 : INFO : "user1" send REQUEST with new xid = 67108864
    2015-05-16 21:18:53,029 : INFO : Receive packet ACK with xid = 67108864
    2015-05-16 21:18:53,029 : INFO : Prepare last Renew with xid = 67108864 for sending
    2015-05-16 21:18:53,030 : INFO : "user1" send REQUEST with new xid = 268435456
    2015-05-16 21:18:53,530 : INFO : Receive packet ACK with xid = 268435456
    2015-05-16 21:18:53,530 : INFO : Prepare last Renew with xid = 268435456 for sending
    2015-05-16 21:18:53,532 : INFO : "user1" send REQUEST with new xid = 687865856
    2015-05-16 21:18:54,032 : INFO : Receive packet ACK with xid = 687865856
    2015-05-16 21:18:54,033 : INFO : Last Request Select packet with xid = 1308622848 converted to Release and ready to send
    2015-05-16 21:18:54,033 : INFO : "user1" send RELEASE with new xid = 687865856
    2015-05-16 21:18:54,035 : INFO : Test "basic_test.test_2" finished


Пример файла packets.log:
+++++++++++++++++++++++++
::

    2015-05-16 21:24:58,496 : DEBUG : Send packet to 192.168.81.96:
     # Header fields
    op : BOOTREQUEST
    htype : 1
    hlen : 6
    hops : 1
    xid : 1224736768
    secs : 0
    flags : 32768
    ciaddr : 0.0.0.0
    yiaddr : 0.0.0.0
    siaddr : 0.0.0.0
    giaddr : 192.168.80.165
    chaddr : ff:11:22:33:44:55
    sname :
    file :
    # Options fields
    dhcp_message_type : DHCP_DISCOVER
    relay_agent :

    2015-05-16 21:24:58,611 : DEBUG : Recived packet from [192, 168, 81, 96]:
     # Header fields
    op : BOOTREPLY
    htype : 1
    hlen : 6
    hops : 1
    xid : 1224736768
    secs : 0
    flags : 32768
    ciaddr : 0.0.0.0
    yiaddr : 12.1.5.89
    siaddr : 0.0.0.0
    giaddr : 192.168.80.165
    chaddr : ff:11:22:33:44:55
    sname : usapp1
    file :
    # Options fields
    server_identifier : 3232256352
    relay_agent :
    subnet_mask : 255.255.255.0
    domain_name_server : 192.168.85.50 - 192.168.80.100 -
    dhcp_message_type : DHCP_OFFER
    router : 10.12.11.1 -
    ip_address_lease_time : 120



Навигация
=========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

