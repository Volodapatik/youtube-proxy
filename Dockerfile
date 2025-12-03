FROM docker.io/invidious/invidious:latest

# Копируем наш конфиг поверх стандартного
COPY config.yml /etc/invidious/config.yml

# Убедимся, что приложение использует нашу конфигурацию
ENV INVIDIOUS_CONFIG=/etc/invidious/config.yml

# Expose порт
EXPOSE 3000
