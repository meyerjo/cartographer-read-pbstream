# Python reading pbstream file

Export the proto description from cartographer

## Getting started

1. Clone [cartographer](https://github.com/cartographer-project/cartographer) project to ``<CARTOGRAPHER_PATH>``
2. export all proto files to python``find CARTOGRAPHER_PATH -name *.proto -printf "%P\n" -exec protoc -I=CARTOGRAPHER_PATH --python_out=. {} \;``

## Print info

``python main.py info --inputfile=<*.pbstream file>`` to print a summary
