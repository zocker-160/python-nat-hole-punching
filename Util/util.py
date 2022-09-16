
from io import BufferedReader, BufferedWriter


def intFromBytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder="little", signed=False)

def bytesFromInt(value: int) -> bytes:
    return int.to_bytes(value, 4, byteorder="little", signed=False)


def writeInt(f: BufferedWriter, value: int):
    f.write(bytesFromInt(value))

def readInt(f: BufferedReader) -> int:
    return intFromBytes(f.read(4))


def writeString(f: BufferedReader, value: str):
    data = value.encode()
    writeInt(f, len(data))
    f.write(data)

def readString(f: BufferedReader) -> str:
    length = readInt(f)
    return f.read(length).decode()
