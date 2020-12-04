FROM python:3-alpine
ENV CRON_DICT_UPDATE='30 9 * * *'
ENV TZ=Asia/Shanghai
ENV USE_TELEGRAM=False
ENV TG_TOKEN=TOKEN
ENV TG_CHAT_IDS=[]
ENV CONFIG_PATH="/config/config.json"
RUN adduser app -D
RUN apk add --no-cache tzdata build-base libffi-dev openssl-dev
WORKDIR /tmp
ADD requirements.txt ./
RUN pip3 install -r requirements.txt && rm requirements.txt
USER app
WORKDIR /app
ADD *.py ./
VOLUME ["/config"]
CMD ["python3", "./docker.py" ]