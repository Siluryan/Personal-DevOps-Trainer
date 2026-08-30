# Site estático do Applier no mesmo nginx do PDT (127.0.0.1:8080).
# O Host do Cloudflare Tunnel escolhe este bloco; o PDT continua no outro.

server {
    listen 127.0.0.1:8080;
    server_name __APPLIER_DOMAIN__;

    root /var/www/applier;
    index index.html;

    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    server_tokens off;

    location /legal/privacidade {
        try_files /legal/privacidade.html =404;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~ /\.(git|env|hg|svn) {
        deny all;
        return 404;
    }
}
