# -*- coding: utf-8 -*-
import yaml

try:
    with open('config.json') as json_file:
        json_data = yaml.safe_load(json_file)
        using_config = json_data['using_config']
        GlobalParams = json_data['GlobalParams']
        RelayAgents = json_data['RelayAgents']
        DhcpSrv = json_data[using_config]['DhcpSrv']
        Users = json_data[using_config]['Users']
except IOError, msg:
    print msg

if __name__ == '__main__':
    pass
