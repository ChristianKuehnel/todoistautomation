FROM python:alpine3.16

RUN mkdir /config \
  mkdir /todoistautomation
VOLUME /config

COPY requirements.txt /todoistautomation
RUN pip3 install  --no-cache-dir -r /todoistautomation/requirements.txt

COPY todoistautomation.py  /todoistautomation

CMD ["/todoistautomation/todoistautomation.py", "--container"]
