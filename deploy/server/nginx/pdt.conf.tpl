# Nginx para o PDT.
# Substitua __DOMAIN__ pelo seu domínio (o user_data faz isso com sed).
# O bloco TLS é injetado pelo certbot --nginx; mantemos só o HTTP aqui.

upstream pdt_app {
    server 127.0.0.1:8000 fail_timeout=0;
    keepalive 32;
}

# Limita rate em endpoints sensíveis (login). Evita burst trivial.
limit_req_zone $binary_remote_addr zone=pdt_login:10m rate=10r/m;

# Mapeamento de upgrade para WebSocket.
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name __DOMAIN__;

    # ACME http-01 challenge é tratado pelo certbot --nginx; o restante
    # vira 301 para HTTPS.
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name __DOMAIN__;

    # Certificados são preenchidos pelo certbot --nginx no primeiro boot.
    # Após emitido, este bloco fica:
    #   ssl_certificate     /etc/letsencrypt/live/__DOMAIN__/fullchain.pem;
    #   ssl_certificate_key /etc/letsencrypt/live/__DOMAIN__/privkey.pem;

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling        on;
    ssl_stapling_verify on;

    # Segurança HTTP
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(self), camera=(), microphone=(self)" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;

    client_max_body_size 25m;
    client_body_timeout  30s;
    client_header_timeout 30s;
    keepalive_timeout    65;
    server_tokens        off;

    # Static (servido por whitenoise dentro do Django, mas acelera com nginx)
    location /static/ {
        alias /opt/pdt/app/pdt/staticfiles/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/pdt/app/pdt/media/;
        expires 7d;
        access_log off;
    }

    # Rate-limit no login do allauth
    location /accounts/login/ {
        limit_req zone=pdt_login burst=20 nodelay;
        proxy_pass http://pdt_app;
        include /etc/nginx/snippets/pdt_proxy.conf;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://pdt_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 1h;
        proxy_send_timeout 1h;
        include /etc/nginx/snippets/pdt_proxy.conf;
    }

    location / {
        proxy_pass http://pdt_app;
        include /etc/nginx/snippets/pdt_proxy.conf;
    }

    location ~ /\.(git|env|hg|svn) {
        deny all;
        return 404;
    }
}
