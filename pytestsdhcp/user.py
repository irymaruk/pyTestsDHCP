# -*- coding: utf-8 -*-
from copy import deepcopy
import random
from pydhcplib.dhcp_packet import *
import struct
import time
from user_default_params import *
from client import Client
import logging
from packet_utils import PacketTypes, PacketUtils


class User():
    """
    Базовый клас. При инициализации используются параметры указанные в файле Config.json в блоке Users по ключу "name"\
    переданному в конструктор создания обекта.
    Например
    user1 = User()
    user2 = User(user2)
    """
    def __init__(self, name='user1'):
        self.name = name
        self.mx1 = Client.get('mx1')
        if len(RelayAgents) == 2:
            self.mx2 = Client.get('mx2')
        self.packets = {PacketTypes.DISCOVER: [],
                        PacketTypes.OFFER: [],
                        PacketTypes.REQUEST: [],
                        PacketTypes.DECLINE: [],
                        PacketTypes.ACK: [],
                        PacketTypes.NAK: [],
                        PacketTypes.RELEASE: [],
                        PacketTypes.INFORM: [],
                        PacketTypes.OTHER: [],}
        self._current_packet_send = None
        self._current_packet_receive = None
        self._last_xid = 0
        self._mx = None
        self.mac_addr_str = Users[self.name]['chaddr']
        self.Agent_Circuit_ID = Users[self.name]['Agent_Circuit_ID']
        self.Agent_Remote_ID = Users[self.name]['Agent_Remote_ID']
        logging.info('Default User params %s', Users[self.name])
        logging.info('User created with name = "%s"', self.name)

############################ packet sending ############################


    def send_packet(self, mx=None, wait_replay=True):
        """
        Отправка подготовленного пакета через RelayAgent, указанный в параметре *mx*

        :param mx: возможные значения *mx1* и *mx2*. Default = mx1
        :param wait_replay: ожидать ответного пакета. Default = True

        :return: None
        """
        self._mx = mx if mx else self.mx1
        self._save_packet_before_send()
        self._mx.send_packet(self._current_packet_send)
        logging.info('"%s" send %s with new xid = %s', self.name, self._get_str_type_packet_send(), self.get_xid_send())
        if wait_replay:
            self.get_current_packet_receive()

    def resend_last_renew(self, count=1):
        """
        Переслать последний отправленний пакет Request Renew

        :param count: количесво раз. Default = mx1
        :return: None
        """
        for i in xrange(count):
            self._current_packet_send = self._get_last_request_renew()
            logging.info('Prepare last Renew with xid = %s for sending', self.get_xid_send())
            self.send_packet()

############################ packet create ############################

    def create_discover_packet(self):
        """
        Создает DHCP-паке Discover с параметрами данного клиента

        :return: None
        """
        self._current_packet_send = DhcpPacket()
        self._current_packet_send.SetOption("op", [1])
        self._current_packet_send.SetOption("htype", [1])
        self._current_packet_send.SetOption("hlen", [6])
        self.set_packet_broadcast(log=False)
        self._current_packet_send.SetOption("dhcp_message_type", [1])
        self.set_packet_opt82(self.Agent_Circuit_ID, log=False)
        self.set_packet_chaddr(self.mac_addr_str, log=False)
        logging.info('Discover packet with default user params created')


############################ packet convert ############################

    def convert_offer_to_request_select(self):
        """
        На основании последнего полученного пакета Offer создает Request Select

        :return: None
        :exception: AttributeError если еще не было Offer
        """
        packet = self._get_last_offer()
        if not packet:
            self._raise_no_packet_exception()
        self._current_packet_send = PacketUtils.convert_offer_to_request_select(self._get_last_offer())
        logging.info('Last Offer packet with xid = %s converted to Request Select and ready to send', self.get_xid_send())


    def convert_request_select_to_renew(self):
        """
        На основании последнего отправленного пакета Request Select создает Request Renew

        :return: None
        :exception: AttributeError если еще не было Request Select
        """
        packet = self._get_last_request_select()
        if not packet:
            self._raise_no_packet_exception()
        self._current_packet_send = PacketUtils.convert_request_select_to_renew(packet)
        logging.info('Last Request Select packet with xid = %s converted to Request Renew and ready to send', self.get_xid_send())

    def convert_request_select_to_release(self):
        """
        На основании последнего отправленного пакета Request Select создает Release

        :return: None
        :exception: AttributeError если еще не было Release
        """
        packet = self._get_last_request_select()
        if not packet:
            self._raise_no_packet_exception()
        self._current_packet_send = PacketUtils.convert_request_select_to_release(packet)
        logging.info('Last Request Select packet with xid = %s converted to Release and ready to send', self.get_xid_send())

############################ packet getters ############################

    def get_xid_received(self):
        return PacketUtils.convert_ipv4_to_str(self.get_current_packet_receive().GetOption('xid'))

    def get_xid_send(self):
        return PacketUtils.convert_ipv4_to_str(self._current_packet_send.GetOption('xid'))

    def get_last_offer_lease_time(self):
        """
        Возвращает Lease time последнего полученного пакета Offer

        :return: Lease time в сек.
        :exception: AttributeError если еще не было Offer
        """
        packet = self._get_last_offer()
        if not packet:
            self._raise_no_packet_exception()
        lt = packet.GetOption('ip_address_lease_time')
        lt_str = int(PacketUtils.convert_32bit_to_str(lt))
        logging.info('Last Offer receive Lease time = %s', lt_str)
        return lt_str


############################ USER setters ############################

    def set_user_opt82(self, value, log=True):
        self.Agent_Circuit_ID = value
        if log:
            logging.info('Set option "option 82" as = "%s" to all user packets', value)

    def set_user_chaddr(self, value, log=True):
        self.mac_addr_str = value
        if log:
            logging.info('Set option "chaddr" as = "%s" to all user packets', value)

    def wait(self, timeout):
        """
        Функция выполняет ожидание заданное в секундах.

        :param timeout: количество секунд
        :return: None
        """
        timeout_int = int(timeout)
        logging.info('Start waiting for %s seconds...', timeout_int)
        time.sleep(timeout_int)
        logging.info('Stop waiting')

############################ packet setters ############################

    def set_packet_opt82(self, value, log=True):
        self._current_packet_send.SetOption("relay_agent", PacketUtils.convert_opt82_from_str(value))
        if log:
            logging.info('Set option "option 82" as = "%s"', value)

    def set_packet_chaddr(self, value, log=True):
        self._current_packet_send.SetOption("chaddr", PacketUtils._convert_chaddr_from_str(value))
        if log:
            logging.info('Set option "chaddr" as = "%s"', value)

    def set_packet_broadcast(self, log=True):
        self._current_packet_send.SetOption("flags", (128, 0))
        if log:
            logging.info('Set broadcast flag')


    def set_packet_unicast(self, log=True):
        self._current_packet_send.SetOption("flags", (0, 0))
        if log:
            logging.info('Set unicast flag')


############################ User internal utils ############################

    def _is_offer_received(self):
        if self.get_current_packet_receive():
            if self.get_current_packet_receive().IsDhcpOfferPacket():
                return True
        return False

    def _wait_for_response_packet(self):
        if self._current_packet_receive:
            return True
        time_out = GlobalParams["implicitly_time_wait"]
        sleep_time = 0.5
        i = 0
        while i <= int(time_out/sleep_time):
            packet = self._mx.get_received_packet_with_xid(self._last_xid)
            if packet:
                self._save_received_packet(packet)
                return True
            time.sleep(sleep_time)
            i += 1
        return False

    def _get_int_packet_type(self, packet):
        if packet.IsDhcpDiscoverPacket():
            return PacketTypes.DISCOVER
        if packet.IsDhcpOfferPacket():
            return PacketTypes.OFFER
        if packet.IsDhcpRequestPacket():
            return PacketTypes.REQUEST
        if packet.IsDhcpDeclinePacket():
            return PacketTypes.DECLINE
        if packet.IsDhcpAckPacket():
            return PacketTypes.ACK
        if packet.IsDhcpNackPacket():
            return PacketTypes.NAK
        if packet.IsDhcpReleasePacket():
            return PacketTypes.RELEASE
        if packet.IsDhcpInformPacket():
            return PacketTypes.INFORM
        return PacketTypes.OTHER

    def _save_packet_before_send(self):
        if not self._current_packet_send:
            raise AttributeError('\n No packet for sending. First create it.')
        self._current_packet_send.SetOption("xid", struct.unpack("4b", struct.pack("I", random.randint(1, 100))))
        self._last_xid = self._current_packet_send.GetOption('xid')
        self.set_current_packet_receive(None)
        packet_type = self._get_int_packet_type(self._current_packet_send)
        packet_copy = deepcopy(self._current_packet_send)
        self.packets[packet_type].append(packet_copy)

    def _save_received_packet(self, packet_link):
        packet_copy = deepcopy(packet_link)
        self.set_current_packet_receive(packet_copy)
        packet_type = self._get_int_packet_type(packet_copy)
        self.packets[packet_type].append(packet_copy)
        logging.info("Receive packet %s with xid = %s", self._get_str_type_packet_received(), self.get_xid_received())

    def _raise_no_packet_exception(self):
        try:
            raise AttributeError("No replay packet received with xid = " + self.get_xid_send())
        except AttributeError, e:
            logging.exception(e)
            raise

    def _get_last_request_select(self):
        return next((pkt for pkt in reversed(self.packets[PacketTypes.REQUEST]) if pkt.IsOption('request_ip_address')), None)

    def _get_last_request_renew(self):
        return next((pkt for pkt in reversed(self.packets[PacketTypes.REQUEST]) if not pkt.IsOption('request_ip_address')), None)

    def _get_last_offer(self):
        if not self.packets[PacketTypes.OFFER]:
            self.get_current_packet_receive()
        return next((pkt for pkt in reversed(self.packets[PacketTypes.OFFER])), AttributeError('No Offers received yet!'))

    def get_current_packet_receive(self):
        self._wait_for_response_packet()
        if not self._current_packet_receive:
            self._raise_no_packet_exception()
        return self._current_packet_receive

    def set_current_packet_receive(self, value):
        self._current_packet_receive = value

    def _get_str_type_packet_send(self):
        return PacketTypes.str_type(self._get_int_packet_type(self._current_packet_send))

    def _get_str_type_packet_received(self):
        return PacketTypes.str_type(self._get_int_packet_type(self.get_current_packet_receive()))


if __name__ == '__main__':
    pass
