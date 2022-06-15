from __future__ import annotations

import gzip
import struct
from collections import defaultdict
from pathlib import Path
from typing import Union

from cartographer.mapping.proto import serialization_pb2


class PBstream_Reader:
    version_magic = 0x7b1d1f7b5bf501db

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.filehandle.close()

    def __init__(self, file_name: Union[str, Path]) -> None:
        file_name = Path(file_name) if isinstance(file_name, str) else file_name
        assert file_name.exists(), 'file_name exists'
        self.file_name = file_name
        self.filehandle = None
        self.initial_offset = 0
        self.serialization_header = None

    @staticmethod
    def info(file_name: Union[str, Path]) -> None:
        """print info """
        assert Path(file_name).exists(), f"file_name {file_name} does not exist"
        print(f'Info about: {file_name}')
        loaded_data = defaultdict(int)
        i = 0
        with PBstream_Reader(file_name) as pb:
            header = pb.serialization_header
            for msg in pb:
                if i % 1000 == 0:
                    print(f'Msg {i}', end='\r')
                fields = msg.ListFields()
                if len(fields) == 0: continue
                i += 1
                for (field_descriptor, messsage) in fields:
                    loaded_data[field_descriptor.name] += 1
        print(f'Serialization Header-Format Version: {header.format_version}')
        max_key_length = max(list(map(len, loaded_data.keys())))
        max_charlength_items = len(str(max([v for _, v in loaded_data.items()])))
        print(f'{"Fieldname": <{max_key_length+7}}\t#Entries')
        for field_name, counter in loaded_data.items():
            print(f'Field: {field_name: <{max_key_length}}\t{counter: >{max_charlength_items}} {"entries" if counter != 1 else "entry"}')

    def _read_header(self) -> None:
        """ reads the header information. raises an AssertionError if expectations are not met """
        assert self.filehandle is not None, 'self.filehandle has to be set'
        assert self.initial_offset == 0, 'no read operation should occur prior to _read_header'
        # check the first 8 bit
        data = self.filehandle.read(8)
        assert self.version_magic == self._readsize(data), "version magic does not match the file start"

        data = self.filehandle.read(8)
        message_length = self._readsize(data)
        # save the initial offset to seek back later
        self.initial_offset = 16 + message_length
        data = self.filehandle.read(message_length)
        compress_data = self.decompress(data)
        self.serialization_header = serialization_pb2.SerializationHeader()
        self.serialization_header.ParseFromString(compress_data)
        assert self.serialization_header.format_version in [1, 2]

    def __enter__(self) -> PBstream_Reader:
        """ entering the context messenger """
        self.filehandle = open(self.file_name, 'rb')

        # read the header if expectiations are not met error is raised
        self._read_header()
        return self

    def _readsize(self, data: bytes) -> int:
        """ bytes are interpreteted as little-endian unsigned long long """
        return struct.unpack_from("<Q", data)[0]

    def decompress(self, data: bytes) -> bytes:
        """ use gzip to decompress the data"""
        return gzip.decompress(data)

    def __iter__(self) -> PBstream_Reader:
        self.n = 0
        return self

    def __next__(self) -> serialization_pb2.SerializedData:
        """ read the size of the next field """
        data = self.filehandle.read(8)
        """ if no data available we raise StopIteration """
        if len(data) == 0:
            raise StopIteration()
        message_length = self._readsize(data)
        # read data of given length and decompress them
        data = self.filehandle.read(message_length)
        compress_data = self.decompress(data)
        # deserialize the data
        content = serialization_pb2.SerializedData()
        content.ParseFromString(compress_data)
        self.n += 1
        return content
