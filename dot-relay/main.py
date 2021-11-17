"""
App to relay DNS requests over TLS against a public resolver.
"""
import sys
import logging
from util import Environment, udp_to_tcp_data, tcp_to_udp_data
from sockethandlers import SocketStarter, ssl_client


def relay_dns_request(ssl_clt, resolver, request):
    """
    Connect to a remote host and send a DNS request.

    :param ssl_clt: (obj) Client SSL socket
    :param resolver: (str, int) IP address and port
    :param request: (bytes) DNS request
    :return:
    """
    try:
        ssl_clt.connect(resolver)
        logging.info(f'Resolver certificate: {ssl_clt.getpeercert()}')
    except Exception as e:
        logging.error(e)
        return False

    ssl_clt.sendall(request)
    response = ssl_clt.recv(2048)
    ssl_clt.close()

    if not response:
        return False
    return response


def main():
    # Initialize logging
    log_format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(filename='../app.log', stream=sys.stdout, format=log_format, level=logging.INFO)

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
        server = SocketStarter().tcp_server(ip, port, timeout=30, reuse=True)
    else:
        server = SocketStarter().udp_server(ip, port)

    if not server:
        return 1

    # Main loop
    while True:
        logging.info('Listening for requests.')
        if server_protocol == 'tcp':
            connection, client_address = server.accept()
            client_request = connection.recv(1024)
        else:
            client_request, client_address = server.recvfrom(512)
            # Make UDP datagram into TCP ready data
            client_request = udp_to_tcp_data(client_request)

        msg = f'Forwarding request from {client_address} to resolver: {resolver[0]}'
        logging.info(msg)

        client = ssl_client(ssl_ca_certs, resolver[0], 30)
        resolver_response = relay_dns_request(client, resolver, client_request)

        if not resolver_response:
            msg = f'Couldn\'t get response for {client_address} request from resolver: {resolver[0]}'
            logging.warning(msg)
            continue

        logging.info(f'Answering original request to {client_address}.')
        if server_protocol == 'tcp':
            connection.sendall(resolver_response)
        else:
            # Make TCP data into UDP datagram
            resolver_response = tcp_to_udp_data(resolver_response)
            server.sendto(resolver_response, client_address)


if __name__ == '__main__':
    sys.exit(main())
