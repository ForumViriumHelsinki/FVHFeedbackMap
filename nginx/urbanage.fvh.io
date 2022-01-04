server {
    listen 80;
    server_name urbanage.fvh.io;

    # Let's encrypt's temporary directory
    location '/.well-known/acme-challenge' {
        default_type "text/plain";
        root /var/www/letsencrypt;
    }
    location / {
        return 301 https://urbanage.fvh.io$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name urbanage.fvh.io;

    client_max_body_size 4G;

    access_log /site/urbanage.fvh.io/logs/nginx-access.log;
    error_log /site/urbanage.fvh.io/logs/nginx-error.log;

    ssl_certificate /etc/letsencrypt/live/urbanage.fvh.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/urbanage.fvh.io/privkey.pem;
    include /etc/nginx/ssl-security.conf;

    location /staticfiles/ {
        alias /site/urbanage.fvh.io/FVHFeedbackMap/django_server/staticfiles/;
    }

    location /media/ {
        alias /site/urbanage.fvh.io/FVHFeedbackMap/django_server/media/;
    }

    location ~* ^/(admin|rest|openapi|swagger) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location / {
        alias /site/urbanage.fvh.io/FVHFeedbackMap/react_ui/build/;
    }

}
