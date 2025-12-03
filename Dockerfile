FROM docker.io/invidious/invidious:release-2024.11.16-2

COPY config.yml /etc/invidious/config.yml
ENV INVIDIOUS_CONFIG=/etc/invidious/config.yml
EXPOSE 3000
