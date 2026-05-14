FROM nginx:latest
WORKDIR /etc/nginx

COPY nginx.conf /etc/nginx

CMD ["nginx", "-c", "/etc/nginx/nginx.conf"]
