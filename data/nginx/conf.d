server {
    listen 8000;
    server_name 127.0.0.1;

    location / {
        include '/etc/nginx/proxy_params';
        proxy_pass http://127.0.0.1:8000/;  # ! Замените адрес на свой
    }
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /opt/star-burger/;
    }
    location /media/ {
        root /opt/star-burger/;
    }
}
