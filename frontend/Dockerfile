FROM nginx:alpine

# Удаляем дефолтные файлы
RUN rm -rf /usr/share/nginx/html/*
RUN rm -f /etc/nginx/conf.d/default.conf

# Копируем конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем файлы фронтенда
COPY --chown=nginx:nginx . /usr/share/nginx/html/

# Удаляем лишнее
RUN rm -f /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/nginx.conf

# Права доступа
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
