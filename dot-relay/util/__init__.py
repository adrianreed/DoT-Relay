"""
Utility classes and methods.
"""
import logging
import os


class Environment:
    """
    Class to retrieve environment data.
    """
    def __init__(self):
        self.ls_ip = '0.0.0.0'
        self.ls_port = 53
        self.ls_proto = os.environ.get('LISTEN_PROTOCOL', 'tcp')
        self.res_ip = os.environ.get('RESOLVER_IP', '1.1.1.1')
        self.res_port = int(os.environ.get('RESOLVER_PORT', 853))
        self.ssl_ca_certs = os.environ.get('SSL_CA_CERTS', '/etc/ssl/certs/ca-certificates.crt')

    def get_environment(self):
        """
        Return dict with environment variables (or default values).
        :return: (dict)
        """
        env = dict(
            ls_ip=self.ls_ip,
            ls_port=self.ls_port,
            ls_proto=self.ls_proto,
            res_ip=self.res_ip,
            res_port=self.res_port,
            ssl_ca_certs=self.ssl_ca_certs
        )
        for e in env:
            msg = f'{e}: set to \'{env[e]}\''
            logging.info(msg)
        return env


def udp_to_tcp_data(d):
    """
    Append two byte length field to UDP datagram, to send it over TCP.

    :param d: (bytes) UDP DNS request
    :return: (bytes) TCP ready DNS request
    """
    length = len(d)
    length_hex = hex(length)[2:].zfill(4)
    prefix = bytes.fromhex(length_hex)
    d = prefix + d
    return d


def tcp_to_udp_data(d):
    """
    Trim TCP packet to send it over UDP.

    :param d: (bytes) TCP DNS response
    :return: (bytes) UDP ready DNS response
    """
    d = d[2:]
    return d
