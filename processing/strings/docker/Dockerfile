FROM ubuntu:latest

RUN apt-get update && apt-get install -y strings --no-install-recommends

VOLUME ["/data"]

WORKDIR /data

ENTRYPOINT ["strings"]
