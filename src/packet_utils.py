# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
from pydhcplib.type_hwmac import hwmac
from pydhcplib.type_ipv4 import ipv4
from pydhcplib.type_strlist import strlist


class PacketTypes():
    """
    Type of DHCP packets
    """
    def __init__(self):
        pass
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    DECLINE = 4
    ACK = 5
    NAK = 6
    RELEASE = 7
    INFORM = 8
    OTHER = 0

    @staticmethod
    def str_type(x):
        return {
            1: 'DISCOVER',
            2: 'OFFER',
            3: 'REQUEST',
            4: 'DECLINE',
            5: 'ACK',
            6: 'NAK',
            7: 'RELEASE',
            8: 'INFORM',
            0: 'OTHER',
        }.get(x, 'OTHER')


class PacketUtils():
    def __init__(self):
        pass

# ########################### convert options value ############################

    @staticmethod
    def convert_opt82_from_str(Agent_Circuit_ID, Agent_Remote_ID=''):
        return [1, len(Agent_Circuit_ID)] + strlist(Agent_Circuit_ID).list() + [2, 1, 1]

    @staticmethod
    def _convert_chaddr_from_str(value):
        return hwmac(value).list() + [0]*10

# ########################### convert types ############################

    @staticmethod
    def convert_ipv4_to_str(value):
        return str(ipv4(value).int())

    @staticmethod
    def convert_32bit_to_str(value):
        return str(ipv4(value).int())

# ########################### packet convert ############################

    @staticmethod
    def convert_offer_to_request_select(packet_in):
        packet = deepcopy(packet_in)
        packet.SetOption("op", [1])
        packet.SetOption("flags", (0, 0))
        yiaddr = packet.packet_data[16:20]
        del packet.options_data["domain_name_server"]
        packet.SetOption("yiaddr", [0, 0, 0, 0])
        packet.SetOption("dhcp_message_type", [3])
        packet.SetOption("request_ip_address", yiaddr)
        return packet

    @staticmethod
    def convert_request_select_to_renew(packet_in):
        packet = deepcopy(packet_in)
        ciaddr = packet.options_data["request_ip_address"]
        packet.SetOption("ciaddr", ciaddr)
        try:
            del packet.options_data["request_ip_address"]
            del packet.options_data["server_identifier"]
        except KeyError, err:
            logging.exception(err)
        return packet

    @staticmethod
    def convert_request_select_to_release(packet_in):
        packet = deepcopy(packet_in)
        packet.SetOption("op", [1])
        packet.SetOption("htype", [1])
        packet.SetOption("hlen", [6])
        packet.SetOption("dhcp_message_type", [7])
        return packet


if __name__ == '__main__':
    pass
