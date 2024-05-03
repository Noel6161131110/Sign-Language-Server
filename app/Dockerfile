FROM python:3.11.8-slim-bookworm

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libpq-dev \
    python3-dev \
    gcc \
    libglib2.0-0 \
    pkg-config \
    libhdf5-dev 

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Upgrade pip
RUN pip install --upgrade pip

# Install h5py and other dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --force-reinstall h5py
RUN pip install -r requirements.txt

RUN python -m pip install mediapipe
RUN python -m pip install tensorflow==2.12.0