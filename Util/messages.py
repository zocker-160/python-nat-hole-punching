
from io import BytesIO
from socket import socket

from Util.client import Client
from Util.util import intFromBytes, writeInt, writeString, readInt, readString


class ConnectionMessage:

    message_length: int
    ip: str
    port: str

    @staticmethod
    def recv(conn: socket):
        length = intFromBytes(conn.recv(4))
        payload = conn.recv(length)

        assert len(payload) == length

        payload = BytesIO(payload)

        ip = readString(payload)
        port = readInt(payload)

        assert len(ip) > 0
        assert port > 0

        return ConnectionMessage(ip, port)

    @staticmethod
    def fromClient(client: Client):
        return ConnectionMessage(client.publicIP, client.port)

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port


    def send(self, conn: socket):
        length = BytesIO()
        payload = BytesIO()

        writeString(payload, self.ip)
        writeInt(payload, self.port)
        payload = payload.getvalue()

        writeInt(length, len(payload))

        payload = length.getvalue() + payload

        conn.send(payload)

    def toTuple(self) -> tuple[str, int]:
        return (self.ip, self.port)

    def __eq__(self, __o: object) -> bool:
        return self.ip == __o.ip and self.port == __o.port

    def __str__(self) -> str:
        return f"(IP: {self.ip}, PORT: {self.port})"
