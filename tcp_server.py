#! /usr/bin/env python3


import sys
import logging
import socket

from Util.messages import ConnectionMessage
from Util.client import Client

from Util.util import *

connected: list[Client] = list()

clients = dict()

def runServer(host="0.0.0.0", port=5050):
    logging.info("starting...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        logging.info(f"binding TCP socket on port {port}")

        # reuse sockest in TIME_WAIT state (Linux only)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))

        # set backlog of unaccepted connections to 1
        s.listen(1)
        s.settimeout(30)
    
        while True:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                logging.debug("closing connection")
                s.close()
                logging.debug("exit...")
                sys.exit()

            logging.info(f"incoming connection: {addr}")

            # do handshake

            privateAddr = ConnectionMessage.recv(conn)
            print("<--", privateAddr)

            publicAddr = ConnectionMessage(*addr)
            publicAddr.send(conn)
            print("-->", publicAddr)

            addrCheck = ConnectionMessage.recv(conn)
            print("<--", addrCheck)

            if publicAddr == addrCheck:
                logging.info("client reply matches")
                connected.append(
                    Client(publicAddr.ip, privateAddr.ip, publicAddr.port, conn))

            else:
                logging.error(f"client reply is different: {publicAddr} vs {addrCheck}")
                s.close()
                sys.exit()

            if len(connected) == 2:
                logging.info(f"sending {connected[0]} to {connected[1]}")
                ConnectionMessage.fromClient(connected[0]).send(connected[1].conn)

                logging.info(f"sending {connected[1]} to {connected[0]}")
                ConnectionMessage.fromClient(connected[1]).send(connected[0].conn)

                connected.clear()
            else:
                logging.info("waiting for second client to connect")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    runServer()
