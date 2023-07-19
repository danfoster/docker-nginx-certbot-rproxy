FROM nginx:1.25

RUN apt-get update && apt-get install -y \
    python3 \
    python3-jinja2 \
    python3-yaml \
    ssl-cert \
    certbot \
    python3-certbot-nginx \
    && rm -rf /var/lib/apt/lists/*
RUN rm -f /etc/nginx/conf.d/default.conf
RUN mkdir /config
ADD scripts/gen_config.py /usr/local/bin/
ADD scripts/manage_certs.py /usr/local/bin/
ADD scripts/30-gen_config.sh /docker-entrypoint.d/
ADD scripts/40-manage_certs.sh /docker-entrypoint.d/
