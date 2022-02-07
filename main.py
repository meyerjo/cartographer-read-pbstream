import argparse
from collections import defaultdict

from pbstream_reader import PBstream_Reader

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['info', 'iterate'])
    parser.add_argument('--inputfile', type=str)
    ARGS = parser.parse_args()

    if ARGS.action == 'info':
        PBstream_Reader.info(ARGS.inputfile)
    elif ARGS.action == 'iterate':
        loaded = defaultdict(list)
        with PBstream_Reader(ARGS.inputfile) as reader:
            for msg in reader:
                # print(msg)
                fields = msg.ListFields()
                if len(fields) == 0:
                    continue
                for (field_descriptor, message) in fields:
                    loaded[field_descriptor.name].append(message)
