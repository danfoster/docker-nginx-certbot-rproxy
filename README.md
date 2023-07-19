# Nginx Reverse Proxy with Letsencrypt support

This docker container provides an opinionated solution to managing a nginx reverse proxy with SSL support. SSL certificates are provided by letsencrypt.

It attempts to provide a similar solution to a kubernetes Ingress with cert-manager, but for a single docker host.


## Configuration

### Files

You need to provide a configuration directory that contains a number of YAML file - one per vhost. The files must end in the extension `.yml` or `.yaml`. An example file would be:

```
host: test1.zem.org.uk
ssl: true
proxies:
 - path: /
   target: https://example.com
```

### Environment

The following environment  variables are mandatory:

 * `EMAIL`: The e-mail address used to register with the ACME server for lets encrypt certificates



## Usage

The following mounts/volumes are expected:

* The configuration directory described above should be mounted to `/config`
* A empty directory / volume should be mounted to `/etc/letsencrypt` for persistent storage of the keys/certificates

### Docker

```
docker run -v $HOME/config:/config -v $HOME/le:/etc/letsencrypt -p 80:80 -p 443:443 -e EMAIL=you@example.com nginx-certbot-rproxy
```

### docker-compose

```
services:
  web: 
    image: nginx-certbot-rproxy
    ports:
      - 80:80
      - 443:443
    volumes:
      - type: bind
        source: /path/to/config
        target: /config
      - le:/etc/letsencrypt
    volumes:
     le:
    environment:
      - EMAIL=you@example.com
```


## How it works

On container start, suitable nginx configurations will be generated from your configuration. If SSL is enabled, but the certificate has not been registered with letsencrypt yet, a temporary self-signed certificate will be used to allow nginx to start.

Once nginx is started, for any certificate that doesn't exist in the letsencrypt cache, a new one will be registered using the `certbot run --nginx ...` command. This will use the standard certbot nginx module to update the nginx configuration to use the correct SSL certificates and restart nginx.

Then once per 24-hours, `certbot renew` will be run.

On subsequent restart of the container, because the certificate exists in your letsencrypt cache, the nginx config will point to the correct certificate to start with. It will also not attempt to run `certbot run ...` for those certificates and instead rely on `certbot renew` 