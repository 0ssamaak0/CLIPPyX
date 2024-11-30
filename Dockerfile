#FROM nvidia/cuda:11.8.0-base-ubuntu22.04
FROM pytorch/pytorch:2.2.1-cuda11.8-cudnn8-runtime

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update 
# RUN apt-get install -y \
#        build-essential 
#        python3 python3-dev python3-pip python-is-python3 
RUN apt-get install -y \
        libgl1-mesa-dev \
        libglib2.0-0 libsm6 libxrender1 libxext6
 
COPY . ./

RUN python -m pip install -r requirements.txt

CMD ["python","main.py"]
