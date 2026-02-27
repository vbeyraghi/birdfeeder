# -----------------------------------
# HTTP port 80 → Redirect to HTTPS
# -----------------------------------
server {
    listen 80;
    server_name ${DOMAIN};

    root ${REPO_PATH};

    # Certbot will manage ssl_certificate and ssl_certificate_key

    # HSTS (optional; enable once you’re certain)
    # add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location = / {
        return 302 /birdfeeder/;
    }

    # -------------------------
    # Angular Frontend at /birdfeeder/
    # -------------------------
    location /birdfeeder/ {
        alias ${REPO_PATH}/browser/;
        try_files $uri $uri/ /app/index.html;
    }

    # -------------------------
    # HLS Stream at /streams/
    # -------------------------
    location /streams/ {
        # Basic Auth
        auth_basic "Restricted Stream";
        auth_basic_user_file /etc/nginx/.htpasswd;

        # Rate limit (uses zone from nginx.conf)
        limit_req zone=mylimit burst=100 nodelay;

        # CORS
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type" always;

        # MIME
        types {
            application/vnd.apple.mpegurl m3u8;
            video/mp2t ts;
        }

        # Playlists: must NOT be cached
        location ~ \.m3u8$ {
            add_header Cache-Control "no-store" always;
        }

        # Segments: small cache is fine (optional)
        location ~ \.ts$ {
            add_header Cache-Control "public, max-age=1, immutable" always;
        }

        autoindex off;
        try_files $uri =404;
    }
}