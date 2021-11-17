"""
Classes to handle socket operations
"""
import logging
import socket
import ssl


class SocketStarter:
    """
    Class to initialize and configure sockets.
    """
    def __init__(self):
        self.get_socket = socket.socket

    def _udp_socket(self):
        """
        Return UDP socket.
        :return: (obj) or False
        """
        try:
            s = self.get_socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            logging.error(e)
            return False
        return s

    def udp_client(self):
        """
        Return UDP client.
        :return: (obj) or False
        """
        s = self._udp_socket()
        if not s:
            return False
        return s

    def udp_server(self, ip, port):
        """
        Return UDP server, bound to an IP address and port.
        :param ip: (str)
        :param port: (int)
        :return: (obj) or False
        """
        s = self._udp_socket()
        if not s:
            return False

        try:
            s.bind((ip, port))
        except Exception as e:
            logging.error(e)
            return False
        return s

    def _tcp_socket(self):
        """
        Return TCP socket.
        :return: (obj) or False
        """
        try:
            s = self.get_socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            logging.error(e)
            return False
        return s

    def tcp_client(self, timeout=None):
        """
        Return TCP client.
        :param timeout: (int)
        :return: (obj) or False
        """
        s = self._tcp_socket()
        if not s:
            return False
        if timeout:
            s.settimeout(timeout)
        else:
            s.settimeout(0)
        return s

    def tcp_server(self, ip, port, timeout=None, reuse=False):
        """
        Return TCP server, bound to an IP address and port.
        Reusable when in TIME_WAIT state if reuse=True.
        :param ip: (str)
        :param port: (int)
        :param timeout: (int)
        :param reuse: (bool)
        :return: (obj) or False
        """
        s = self._tcp_socket()
        if not s:
            return False

        if reuse:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if timeout:
            s.settimeout(timeout)
        else:
            s.settimeout(0)

        try:
            s.bind((ip, port))
            s.listen()
        except Exception as e:
            logging.error(e)
            return False
        return s


class ContextStarter:
    """
    Class to initialize and configure SSL contexts.
    """
    def __init__(self, ca_cert_file, server=False, verify=True):
        """
        Initialize SSL context. By default it's a client side, and forces verification.
        :param ca_cert_file: (str) CA Cert file location
        :param server: (bool) Server or not
        :param verify: (bool) Force verify
        """
        self.ca_cert_file = ca_cert_file
        self.server = server
        self.verify = verify
        self.get_context = ssl.SSLContext

        if self.server:
            self.protocol = ssl.PROTOCOL_TLS_SERVER
        else:
            self.protocol = ssl.PROTOCOL_TLS_CLIENT

        if self.verify:
            self.mode = ssl.CERT_REQUIRED
        else:
            self.mode = ssl.CERT_OPTIONAL

    def _setup_ssl_context(self):
        """
        Return configured SSL context.
        :return: (obj)
        """
        try:
            c = self.get_context(self.protocol)
            c.verify_mode = self.mode
            c.load_verify_locations(cafile=self.ca_cert_file)
        except Exception as e:
            logging.error(e)
            return False
        return c

    def wrap(self, sock, ip, hoc=True):
        """
        Wrap a TCP socket in SSL context.
        :param sock: (ojb)
        :param ip: (str)
        :param hoc: (str) Do handshake on connect
        :return: (obj)
        """
        c = self._setup_ssl_context()
        if not c:
            return False

        try:
            w = c.wrap_socket(sock, do_handshake_on_connect=hoc, server_hostname=ip)
        except Exception as e:
            logging.error(e)
            print(e)
            return False
        return w


def ssl_client(certs, ip, timeout):
    """
    Return a SSL client.
    :param certs: (str)
    :param ip: (str)
    :param timeout: (int)
    :return: (obj)
    """
    s = SocketStarter().tcp_client(timeout=timeout)
    if not s:
        return False

    c = ContextStarter(certs, verify=True)
    if not c:
        return False

    w = c.wrap(s, ip)
    if not w:
        return False
    return w


def ssl_server():
    pass
