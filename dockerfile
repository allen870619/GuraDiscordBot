FROM python:3.9.6
MAINTAINER Allen Lee <allen870619@gmail.com>

# action
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Taipei
COPY . /gura_bot
WORKDIR /gura_bot
RUN pip3 install -r requirments.txt
CMD ["python3", "main.py"]