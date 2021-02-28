FROM debian:buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    nano \
    sed  \
    curl \
    git \
    wget \
    gnupg2 \
    python3-pip \
    software-properties-common


RUN wget -O - https://qgis.org/downloads/qgis-2020.gpg.key | gpg --import
RUN gpg --fingerprint F7E06F06199EF2F2
RUN gpg --export --armor F7E06F06199EF2F2 | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import
RUN chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg

RUN apt-add-repository 'deb https://qgis.org/debian-ltr buster main'

RUN apt-get update && apt-get install -y \
    qgis \
    python3-qgis

RUN mkdir /code

RUN python3 -m pip install --upgrade pip

WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2
