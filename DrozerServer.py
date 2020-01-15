# -*- coding: UTF-8 -*-
from drozer.console.session import Session
from drozer.connector import ServerConnector

# Drozer 自身配置信息
class Arguments():

    def __init__(self,_ipAdrr):
        self.server = _ipAdrr

    accept_certificate = False
    command = "connect"
    debug = False
    device = None
    file = []
    no_color = False
    onecmd = None
    password = False
    ssl = False


class DrozerServer():

    def __init__(self, _ipAdrr):
        arguments = Arguments(_ipAdrr)
        server = ServerConnector(arguments, None)
        devices = server.listDevices().system_response.devices
        device = devices[0].id
        response = server.startSession(device, None)
        session_id = response.system_response.session_id
        self.session = Session(server, session_id, arguments)

    def getSession(self):
        return self.session