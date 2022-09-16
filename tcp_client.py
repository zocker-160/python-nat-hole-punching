#! /usr/bin/env python3

import sys
import logging
import socket
import signal

from threading import Event, Thread
from Util.messages import ConnectionMessage
from Util.util import *

STOP = Event()


def acceptFromPeer(peer: ConnectionMessage):
    logging.info(f"waiting for peer connection from {peer}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(('0.0.0.0', peer.port))
        s.listen(1)
        s.settimeout(5)

        while not STOP.is_set():
            try:
                conn, addr = s.accept()
            except socket.timeout:
                print(".", end="")
                continue
            else:
                print("")

            logging.info(f"connection from {addr} ACCEPT!!")

            # chat logic

            #time.sleep(5)
            #STOP.set()


def messageListener(s: socket.socket):
    while not STOP.is_set():
        try:
            length = intFromBytes(s.recv(4))
            message = s.recv(length)
        except socket.timeout:
            continue

        print("<--", message)

        if message.startswith(b"!exit"):
            STOP.set()
            return


def connectToPeer(local: ConnectionMessage, peer: ConnectionMessage):
    logging.info(f"attempting connection from {local} to {peer}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(local.toTuple())
        s.settimeout(5)

        while not STOP.is_set():
            try:
                s.connect(peer.toTuple())
            except socket.error:
                print(".", end="")
                continue
            else:
                print("")

            logging.info(f"connected from {local} to {peer} SUCCESS!!")

            listener = Thread(target=messageListener, args=(s,))
            listener.start()

            # chat logic
            while not STOP.is_set():
                try:
                    cmd = input()
                except EOFError:
                    STOP.set()
                    break

                if cmd.startswith("!stop"):
                    STOP.set()
                    logging.info("exit triggered")

                    cmd = "!exit triggered by peer - please just hit to exit"
                
                pl = cmd.encode()

                s.send(bytesFromInt(len(pl)))
                s.send(pl)

            listener.join()


def runClient(host: str, port=5050):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        logging.info(f"connecting to {host}:{port}")

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((host, port))

        logging.info("connected to server - starting handshake")

        # server handshake

        privateAddr = ConnectionMessage(*s.getsockname())
        privateAddr.send(s)
        print("-->", privateAddr)

        publicAddr = ConnectionMessage.recv(s)
        print("<--", publicAddr)

        publicAddr.send(s)
        print("-->", publicAddr)

        # wait for connection fo second client

        logging.info("handshake done - waiting for second client")

        try:
            peerAddr = ConnectionMessage.recv(s)
        except AssertionError as e:
            logging.error("peer data is invalid or empty, server probably disconnected")
            logging.exception(e)
            return

        logging.info("second client connected to server")
        logging.info(
            f"client public: {publicAddr}, " \
            + f"client private: {privateAddr}, " \
            + f"peer: {peerAddr}"
        )

        acceptThread = Thread(target=acceptFromPeer, args=(peerAddr,))
        connectThread = Thread(target=connectToPeer, args=(privateAddr, peerAddr))


        #acceptThread.start()
        connectThread.start()

        #acceptThread.join()
        connectThread.join()


def triggerExit(*args, **kargs):
    logging.info("exit triggered")

    if STOP.is_set():
        logging.info("force exit")
        sys.exit()

    STOP.set()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    signal.signal(signal.SIGINT, triggerExit)
    signal.signal(signal.SIGTERM, triggerExit)

    runClient(sys.argv[1], port=5050)
