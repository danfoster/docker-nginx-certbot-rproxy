#!/usr/bin/env python3

import yaml
import os
from jinja2 import Environment, select_autoescape


CONFIG_DIR = os.environ.get("CONFIG_DIR", "/config")
OUTPUT_DIR = "/etc/nginx/conf.d"

CONFIG_TEMPLATE = """
server {
    listen       80;
    server_name  {{host}};

    root   /usr/share/nginx/html;
    index  index.html index.htm;

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
    
    {% if ssl %}
    location /.well-known {
        try_files $uri $uri/ =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
    {% endif %}
}

{% if ssl %}
server {
    listen 443 ssl;
    server_name {{host}};
    
    {% if certexists %}
    ssl_certificate /etc/letsencrypt/live/{{host}}/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/{{host}}/privkey.pem; # managed by Certbot
    {% else %}
    ssl_certificate     /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    {% endif %}
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    
    root   /usr/share/nginx/html;
    index  index.html index.htm;
    
    {% for proxy in proxies %}
    location {{proxy.path}} {
        proxy_pass {{proxy.target}};
    }
    {% endfor %}
}
{% endif %}
"""

for file in os.listdir(CONFIG_DIR):
    if not (file.endswith(".yaml") or file.endswith(".yml")):
        continue
    with open(os.path.join(CONFIG_DIR, file)) as stream:
        data = yaml.safe_load(stream)
        if data is None:
            continue
        env = Environment(autoescape=select_autoescape())
        template = env.from_string(CONFIG_TEMPLATE)

        certexists = False
        if os.path.exists(f"/etc/letsencrypt/live/{data['host']}"):
            certexists = True
        data["certexists"] = certexists
        output = template.render(**data)
        with open(os.path.join(OUTPUT_DIR, f"{data['host']}.conf"), "w") as outputfile:
            outputfile.write(output)
