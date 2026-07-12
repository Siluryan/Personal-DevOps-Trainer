# Nginx para o PDT atrás de Cloudflare Tunnel.
# Substitua __DOMAIN__ pelo domínio (apex + www separados por espaço).
# Escuta apenas em localhost; cloudflared encaminha tráfego público para :8080.

upstream pdt_app {
    server 127.0.0.1:8000 fail_timeout=0;
    keepalive 32;
}

limit_req_zone $binary_remote_addr zone=pdt_login:10m rate=10r/m;

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

map $http_x_forwarded_proto $pdt_forwarded_proto {
    default $http_x_forwarded_proto;
    ''      https;
}

server {
    listen 127.0.0.1:8080;
    server_name __DOMAIN__;

    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(self), camera=(), microphone=(self)" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Content-Security-Policy "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' data: https://unpkg.com https://cdn.jsdelivr.net; connect-src 'self' wss: https:; frame-src 'none';" always;

    client_max_body_size 25m;
    client_body_timeout  30s;
    client_header_timeout 30s;
    keepalive_timeout    65;
    server_tokens        off;

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

    location /accounts/login/ {
        limit_req zone=pdt_login burst=20 nodelay;
        proxy_pass http://pdt_app;
        include /etc/nginx/snippets/pdt_proxy.conf;
    }

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
