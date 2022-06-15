FROM ubuntu:20.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get update && apt-get install -y git protobuf-compiler curl libgl1-mesa-glx libgomp1 python3.9 python3.9-distutils tzdata

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py --user
RUN rm /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python
ENV CARTOGRAPHER_PATH=/cartographer
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

WORKDIR /code
RUN mkdir -p /cartographer
RUN git clone https://github.com/cartographer-project/cartographer.git $CARTOGRAPHER_PATH
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY . .

RUN find $CARTOGRAPHER_PATH -name *.proto -printf "%P\n" -exec protoc -I=$CARTOGRAPHER_PATH --python_out=./src/ {} \;

RUN python setup.py build
RUN python setup.py install
RUN python setup.py bdist_wheel
RUN python -m pip install ./dist/pbstream-0.0.1-py3-none-any.whl

# restart with a clean image
FROM ubuntu:20.04
COPY requirements.txt .
COPY --from=builder /code/dist/pbstream-0.0.1-py3-none-any.whl .

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
ENV QT_X11_NO_MITSHM=1
ENV XAUTHORITY=/tmp/.docker.xauth
ENV NO_AT_BRIDGE=1

RUN apt-get update && apt-get install -y curl libgl1-mesa-glx libgomp1 python3.9 python3.9-distutils tzdata

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py --user
RUN rm /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python

RUN python -m pip install -r requirements.txt
RUN python -m pip install pbstream-0.0.1-py3-none-any.whl

WORKDIR /code
COPY main.py /code
CMD python main.py info --inputfile=$PBSTREAM_FILE
