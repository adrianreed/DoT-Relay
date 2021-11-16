"""
Classes to handle socket operations
"""
import logging
import socket
import ssl


class SocketStarter:
    """
    Class to initialize standard sockets with basic configuration.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.get_socket = socket.socket

    def udp_base(self):
        """
        Return a standard UDP socket.
        :return: (obj) or False
        """
        try:
            s = self.get_socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return s

    def udp_server(self):
        """
        Return a server UDP socket bound to the instance IP address and port.
        :return: (obj) or False
        """
        s = self.udp_base()
        try:
            s.bind((self.ip, self.port))
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return s

    def tcp_base(self):
        """
        Return a standard TCP socket.
        :return: (obj) or False
        """
        try:
            s = self.get_socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return s

    def tcp_server(self):
        """
        Return a server TCP socket bound to the instance IP address and port.
        This socket will be configured to be reusable when in TIME_WAIT state.
        :return: (obj) or False
        """
        s = self.tcp_base()
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen()
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return s


class SocketWrapper:
    """
    Class to wrap standard TCP sockets in TLS.
    """
    def __init__(self, sock, ip, crt_file):
        self.sock = sock
        self.ip = ip
        self.crt_file = crt_file

    def wrap(self):
        """
        Use instance socket (TCP), IP and path to the SSL CA certs file to return a wrapped socket.
        :return: (obj) or False
        """
        try:
            c = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            c.verify_mode = ssl.CERT_REQUIRED
            c.load_verify_locations(self.crt_file)
            w = c.wrap_socket(self.sock, server_hostname=self.ip)
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return w
