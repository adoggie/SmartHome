#coding:utf-8

# -*- coding: utf-8 -*-

import socket

SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
SERVICE_NAME = 'my_service'


class Connection():
    def __init__(self, s, data, addr):
        self.__s = s
        self.__data = data
        self.__addr = addr
        self.is_find_service = False

    def handle_request(self):
        if self.__data.startswith('M-SEARCH * HTTP/1.1\r\n'):
            self.__handle_search()
        elif self.__data.startswith('HTTP/1.1 200 OK\r\n'):
            self.__handle_ok()

    def __handle_search(self):
        props = self.__parse_props(['HOST', 'MAN', 'ST', 'MX'])
        if not props:
            return

        # if props['HOST'] != '%s:%d' % (SSDP_ADDR, SSDP_PORT) \
        #         or props['MAN'] != '"ssdp:discover"' \
        #         or props['ST'] != 'ssdp:all':
        #     return

        if props['HOST'] != '%s:%d' % (SSDP_ADDR, SSDP_PORT) \
                or props['MAN'] != '"ssdp:discover"' \
                or props['ST'] != 'fanbei-smarthome:device':
            return

        # print 'RECV: %s' % str(self.__data)
        # print 'ADDR: %s' % str(self.__addr)

        # response = 'HTTP/1.1 200 OK\r\nST: %s\r\n\r\n' % SERVICE_NAME
        print self.__data
        print 'get discover ..'
        response = \
            """NOTIFY * HTTP/1.1\r\n"""\
            """HOST: 239.255.255.250:1900\r\n"""\
            """NT: fanbei-smarthome:device\r\n"""\
            """NTS: ssdp:alive\r\n"""\
            """USN: uuid:f40c2981-7329-40b7-8b04-27f187aecfb8\r\n"""\
            """LOCATION: http://192.168.14.17:8080\r\n"""\
            """CACHE-CONTROL: max-age=1800\r\n"""\
            """DEVICE_TYPE: bridge\r\n\r\n"""

        self.__s.sendto(response, self.__addr)
        print response
        print self.__addr

    def __handle_ok(self):
        props = self.__parse_props(['ST'])
        if not props:
            return

        if props['ST'] != SERVICE_NAME:
            return

        print 'RECV: %s' % str(self.__data)
        print 'ADDR: %s' % str(self.__addr)
        print 'Find service!!!!'

        self.is_find_service = True

    def __parse_props(self, target_keys):
        lines = self.__data.split('\r\n')

        props = {}
        for i in range(1, len(lines)):
            if not lines[i]:
                continue

            index = lines[i].find(':')
            if index == -1:
                return None

            props[lines[i][:index]] = lines[i][index + 1:].strip()

        if not set(target_keys).issubset(set(props.keys())):
            return None

        return props


class SSDPServer():
    def __init__(self,local_ip):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # local_ip = socket.gethostbyname(socket.gethostname())
        # print socket.gethostname()
        # local_ip = "192.168.14.17"
        any_ip = '0.0.0.0'

        # 绑定到任意地址和SSDP组播端口上
        self.__s.bind((any_ip, SSDP_PORT))


        # INFO: 使用默认值
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
        #                     socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
        # INFO: 添加到多播组
        self.__s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(SSDP_ADDR) + socket.inet_aton(local_ip))
        self.local_ip = local_ip

    def start(self):
        print 'ssdp server started..'
        while True:
            data, addr = self.__s.recvfrom(2048)
            # print data
            # if data.find('SEARCH') != -1:
            #     print 'got some data from group:', addr,'\n', data
            conn = Connection(self.__s, data, addr)
            conn.handle_request()
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
        #                     socket.inet_aton(SSDP_ADDR) + socket.inet_aton(self.local_ip))
        # self.__s.close()


if __name__ == '__main__':
    # port = SSDPServer("192.168.14.17")
    # port = SSDPServer("192.168.0.108")
    port = SSDPServer("192.168.0.110")
    port.start()
