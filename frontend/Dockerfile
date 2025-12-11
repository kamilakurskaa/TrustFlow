# frontend/Dockerfile
FROM nginx:alpine

# Копируем ВСЕ статические файлы фронтенда
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]