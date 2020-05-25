FROM ubuntu 
ARG DEBIAN_FRONTEND=noninteractive
RUN mkdir /app
COPY bot.py /app/
COPY requirements.txt /app
COPY geckodriver /usr/bin
RUN cd /app
RUN apt-get update && apt-get install -y python3-pip firefox
RUN pip3 install -r /app/requirements.txt
ENTRYPOINT ["python3", "/app/bot.py"]
