"""
App to relay DNS requests over TLS against a public resolver.
"""
import sys
import logging
from util import Environment, udp_to_tcp_data, tcp_to_udp_data
from sockethandlers import SocketStarter, SocketWrapper


def relay_dns_request(request, ip, port, resolver, certs):
    """
    Create a TLS wrapped TCP socket, connect to a remote host and send a DNS request.

    :param request: (bytes) DNS request
    :param ip: (str)
    :param port: (int)
    :param resolver: (str, int) IP address and port
    :param certs: (str) Filesystem path
    :return:
    """
    c = SocketStarter(ip, port)
    clt_socket = c.tcp_base()
    if not clt_socket:
        return False

    w = SocketWrapper(clt_socket, resolver[0], certs)
    wrapped_socket = w.wrap()
    if not wrapped_socket:
        return False

    try:
        wrapped_socket.connect(resolver)
    except Exception as e:
        logging.error(e)
        print(e)
        return False

    logging.info(f'Resolver certificate:\n{wrapped_socket.getpeercert()}')
    wrapped_socket.sendall(request)
    response = wrapped_socket.recv(2048)
    clt_socket.close()
    if not response:
        return False
    return response


def main():
    # Initialize logging
    log_format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(filename='../app.log', format=log_format, level=logging.INFO)

    logging.info('Retrieving environment and configuration data.')
    e = Environment().get_environment()
    ip = e.get('ls_ip')
    port = e.get('ls_port')
    server_protocol = e.get('ls_proto')
    resolver_ip = e.get('res_ip')
    resolver_port = e.get('res_port')
    ssl_ca_certs = e.get('ssl_ca_certs')
    resolver = (resolver_ip, resolver_port)

    logging.info(f'Starting server.')
    if server_protocol == 'tcp':
        s = SocketStarter(ip, port)
        srv_socket = s.tcp_server()
    else:
        s = SocketStarter(ip, port)
        srv_socket = s.udp_server()

    if not srv_socket:
        return 1

    # Main loop
    while True:
        logging.info('Listening for requests.')
        if server_protocol == 'tcp':
            connection, client_address = srv_socket.accept()
            client_request = connection.recv(1024)
        else:
            client_request, client_address = srv_socket.recvfrom(512)
            # Make UDP datagram into TCP ready data
            client_request = udp_to_tcp_data(client_request)

        logging.info(f'Forwarding request from {client_address} to resolver: {resolver[0]}')
        resolver_response = relay_dns_request(client_request, ip, port, resolver, ssl_ca_certs)
        if not resolver_response:
            msg = f'Couldn\'t get response for {client_address} request from resolver: {resolver[0]}'
            logging.warning(msg)
            print(msg)
            continue

        logging.info(f'Answering original request to {client_address}.')
        if server_protocol == 'tcp':
            connection.sendall(resolver_response)
        else:
            # Make TCP data into UDP datagram
            resolver_response = tcp_to_udp_data(resolver_response)
            srv_socket.sendto(resolver_response, client_address)


if __name__ == '__main__':
    sys.exit(main())
