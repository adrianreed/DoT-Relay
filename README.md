# DNS over TLS Relay
Python app to relay DNS queries to a TLS enabled public resolver. 

## Usage

1) In the Dockerfile, set the following variables:
   1) LISTEN_PROTOCOL to 'tcp' or 'udp' to switch between TCP/UDP server.
   2) RESOLVER_IP and RESOLVER_PORT with the info of the public resolver you want to relay requests to.
2) Build image:
```
## For TCP (after setting LISTEN_PROTOCOL='tcp' in the Dockerfile)
$ docker build -f Dockerfile -t dotrelay:tcp .

## For UDP (after setting LISTEN_PROTOCOL='udp' in the Dockerfile)
$ docker build -f Dockerfile -t dotrelay:udp .
```
3) Start container:
```
## For TCP
$ docker run --rm -it -p 53:53/tcp dotrelay:tcp

## For UDP
$ docker run --rm -it -p 53:53/udp dotrelay:udp
```
4) Test with a dig query: 
```
## For TCP
$ dig @{host_ip} n26.com +tcp

## For UDP
$ dig @{host_ip} n26.com
```


## Implementation
- Independently of whether the server is in TCP or UDP mode, all relayed requests will be performed over TLS/TCP traffic.
- Client data is, as much as possible, kept untouched by the code itself. The exception is when running in UDP mode; since a datagram is received, we need to make a 'manual' injection of bytes to comply with TCP standards (rfc1035, section 4.2.2). Just as well, once we receive a response from the public resolver, the TCP packet needs to be trimmed before it can be sent back as a UDP datagram. That said, all operations are handled by standard Python libraries and no methods have direct access to the decoded content of the data.
- By default, the original ca-certificates.crt file from the official Docker image we use (python:3.9-slim) will be used to perform the TLS verification.

Workflow:
1) Gather environment info and setup parameters.
2) Initiate server according to configuration parameters retrieved (TCP or UDP).
3) Listen for DNS requests from clients. Data received will be manipulated *if required* (see step 3 of 'Details').
5) Relay the request over TCP/TLS to a public DNS resolver and wait for a response.
7) Return the response from the public DNS resolver, back to the origina client. Data received will be manipulated *if required* (see step 3 of 'Details').

Code details:
1) The app lives within the dot-relay/ directory (from where it can be packaged via setup.py).
2) The Dockerfile provides a default configuration of the environment and creates the app entrypoint.
3) main.py gathers info, initiates the servers and the listening loop, and performs all the necessary calls to complete the workflow.
4) 'sockethandlers' provides classes and methods to work with sockets and TLS wrapping. *All* socket creation and configuration is abstracted by these classes and methods. As a standard: all these methods will return a socket object (or False if an error occurs). 
5) 'util' provides a mix of utility classes and methods to gather and process different types of data. Because of the nature of the module there's no guidelines here, but docstrings should be enough to understand what's going on.
6) setup.py can be used to package the code into a tarball/zip with:
```
$ python3 setup.py sdist --formats=gztar,zip
```
