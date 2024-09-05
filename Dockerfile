FROM debian:bookworm

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    nano \
    sed  \
    curl \
    git \
    wget \
    gnupg2 \
    python3-pip \
    python3-venv \
    libgdal-dev \
    software-properties-common


WORKDIR /etc/apt/keyrings
RUN wget -O /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg 
RUN echo "deb [signed-by=/etc/apt/keyrings/qgis-archive-keyring.gpg] https://qgis.org/debian-ltr bookworm main" | tee /etc/apt/sources.list.d/qgis.list
RUN apt update  && apt install -y \
    qgis \
    python3-qgis

RUN mkdir /code
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 20
# Since python 3.11, one can not install package without be in venv
ENV PIP_BREAK_SYSTEM_PACKAGES 1

COPY ./requirements-lock.txt /code/
COPY ./entrypoint.sh /code/
WORKDIR /code
ENTRYPOINT [ "/code/entrypoint.sh" ]

# COPY ./requirements.txt /code/
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt