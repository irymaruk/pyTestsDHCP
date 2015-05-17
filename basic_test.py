# -*- coding: utf-8 -*-
import pytest
from src.user import User

def test_1():
    user = User()
    user.create_discover_packet()
    user.send_packet()
    user.set_packet_opt82('ISKRATEL:kv-257-1019 atm 3/5:1.40')
    user.set_packet_chaddr('FF:11:22:33:44:56')
    user.send_packet()
    user.convert_offer_to_request_select()
    user.send_packet()
    user.convert_request_select_to_renew()
    user.send_packet()
    user.resend_last_renew()
    user.resend_last_renew()
    lease_time = user.get_last_offer_lease_time()
    user.wait(lease_time/19)
    user.resend_last_renew()
    user.convert_request_select_to_release()
    user.send_packet(wait_replay=False)


def test_2():
    user = User()
    user.create_discover_packet()
    user.set_packet_opt82('ISKRATEL:kv-257-1019 atm 3/77:1.40')
    user.send_packet()
    user.convert_offer_to_request_select()
    user.send_packet()
    lease_time = user.get_last_offer_lease_time()
    user.wait(lease_time/20)
    user.convert_request_select_to_renew()
    user.send_packet()
    user.resend_last_renew(2)
    user.convert_request_select_to_release()
    user.send_packet(wait_replay=False)

if __name__ == "__main__":
    pytest.main('-q -s --color=yes -k test_2')