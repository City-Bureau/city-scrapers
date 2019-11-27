FROM python:3.7.5-alpine

# Install core dependencies
RUN apk update && \
    apk add gcc libc-dev libffi-dev openssl-dev libxml2-dev libxslt-dev

# Install some nice tools
RUN apk add bash git vim less nano

WORKDIR /usr/src/app/

# Install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install source code
COPY . .

CMD [ "bash" ]