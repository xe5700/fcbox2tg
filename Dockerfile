FROM python:3-alpine
ENV TZ=Asia/Shanghai
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
CMD ["python3", "./mainapp.py" ]