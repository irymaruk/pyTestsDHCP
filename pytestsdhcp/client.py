# -*- coding: utf-8 -*-
from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *
import thread
from user_default_params import *
import logging


class Client(DhcpClient):
    """
    Класс отвечающий за реализацию поведение Relay Agent (Juniper MX).

    """
    __mx1 = None
    __mx2 = None

    @classmethod
    def get(cls, name='mx1'):
        """
        Метод возвращает объект данного класа (Relay Agent).

        :param name: имя релей агента. Задается в config.json RelayAgents. Например: "mx1" или "mx2".

        :return: объект класса *Client*
        """
        if name == 'mx1':
            if not cls.__mx1:
                cls.__mx1 = Client(mx_ip=RelayAgents['mx1'])
            return cls.__mx1
        if name == 'mx2':
            if not cls.__mx2:
                cls.__mx2 = Client(mx_ip=RelayAgents['mx2'])
            return cls.__mx2
        else:
            raise AttributeError

    def __init__(self, mx_ip):
        DhcpClient.__init__(self, mx_ip, 67, 68)
        self.mx_ip = mx_ip
        self.dhcp_server_addr = DhcpSrv
        self.receive_packet_queue = []
        self.logger_mx = self._init_logger()
        try:
            self.BindToAddress()
            thread.start_new_thread(self.start_listen_port, ())
        except Exception, err:
            logging.exception(err)
            raise
        logging.info('MX ip = %s ready for sending packets to DHCP server ip = %s', self.mx_ip, self.dhcp_server_addr)

    def _init_logger(self):
        logger_mx = logging.getLogger('mx_log')
        logger_mx.setLevel(logging.DEBUG)
        fh = logging.FileHandler('packets.log', mode='w')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        fh.setFormatter(formatter)
        logger_mx.addHandler(fh)
        return logger_mx

    def start_listen_port(self):
        while True:
            self.GetNextDhcpPacket()

    def get_packet_hwmac(self, packet):
        return hwmac(packet.packet_data[28:34])

    def get_received_packet_with_xid(self, xid):
        return next((packet for packet in self.receive_packet_queue if packet.GetOption('xid') == xid), None)


    def send_packet(self, packet):
        packet.SetOption("giaddr", map(int, self.mx_ip.split('.')))
        packet.SetOption("hops", [1])
        self.SendDhcpPacketTo(packet, self.dhcp_server_addr, 67)
        self.logger_mx.debug('Send packet to %s:\n %s', self.dhcp_server_addr, packet.str())

    def HandleDhcpAll(self, packet):
        self.receive_packet_queue.append(packet)
        self.logger_mx.debug('Recived packet from %s:\n %s', packet.GetOption('server_identifier'), packet.str())


if __name__ == '__main__':
    pass
