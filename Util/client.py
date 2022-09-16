
from io import BufferedReader, BytesIO
from socket import socket

from Util.util import readInt, readString, writeInt, writeString


class Client:

    def __init__(self, publicIP: str, privateIP: str,  port: int, conn: socket):
        self.publicIP = publicIP
        self.privateIP = privateIP
        self.port = port
        self.conn = conn

    def __str__(self) -> str:
        return f"({self.publicIP}, {self.privateIP}, {self.port})"
