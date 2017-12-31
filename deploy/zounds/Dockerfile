FROM ubuntu:16.04

MAINTAINER John Vinyard <john.vinyard@gmail.com>

RUN apt-get update --fix-missing && apt-get install -y \
    g++ \
    autoconf \
    autogen \
    automake \
    libtool \
    pkg-config \
    libogg0 \
    libogg-dev \
    libvorbis0a \
    libvorbis-dev \
    libsamplerate0 \
    libsamplerate0-dev \
    libx11-dev \
    python-dev \
    libfreetype6-dev \
    libpng12-dev \
    libffi-dev \
    python-pip \
    wget \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    git \
    mercurial \
    subversion

RUN wget http://downloads.xiph.org/releases/flac/flac-1.3.1.tar.xz \
    && tar xf flac-1.3.1.tar.xz \
    && cd flac-1.3.1 \
    && ./configure --libdir=/usr/lib/x86_64-linux-gnu && make && make install \
    && cd .. \
    && rm -rf flac-1.3.1

    RUN wget https://github.com/erikd/libsndfile/archive/1.0.26.tar.gz -O libsndfile-1.0.26.tar.gz \
    && tar -xzf libsndfile-1.0.26.tar.gz \
    && cd libsndfile-1.0.26 \
    && ./autogen.sh \
    && ./configure --libdir=/usr/lib/x86_64-linux-gnu \
    && make \
    && make install \
    && cd .. \
    && rm -rf libsndfile-1.0.26

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh \
    && wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh \
    && /bin/bash /Miniconda-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm /Miniconda-latest-Linux-x86_64.sh

ENV PATH /opt/conda/bin:$PATH

RUN conda install -y numpy=1.12.1 scipy=0.19 && conda clean -i -l -t -y

RUN pip install zounds==0.26.12 && rm -rf /root/.cache/pip/*