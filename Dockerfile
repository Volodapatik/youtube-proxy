FROM ghcr.io/iv-org/invidious:latest

COPY config.yml /etc/invidious/config.yml
ENV INVIDIOUS_CONFIG=/etc/invidicious/config.yml
EXPOSE 3000
