#!/usr/bin/env python3

from time import sleep

#!/usr/bin/env python3

import yaml
import os, sys
import subprocess
import time

CONFIG_DIR = os.environ.get("CONFIG_DIR", "/config")
EMAIL = os.environ.get("EMAIL")
SLEEP = 86400


if not EMAIL:
    print("ERROR: Envvar EMAIL is not set")
    sys.exit(1)


### Request any new domains we haven't registered with certbot
for file in os.listdir(CONFIG_DIR):
    if not (file.endswith(".yaml") or file.endswith(".yml")):
        continue
    with open(os.path.join(CONFIG_DIR, file)) as stream:
        data = yaml.safe_load(stream)
        if data is None:
            continue

        ssl = data["ssl"]
        if (not os.path.exists(f"/etc/letsencrypt/live/{data['host']}")) and ssl:
            hostname = data["host"]
            cmd = [
                "/usr/bin/certbot",
                "run",
                "--nginx",
                "-m",
                EMAIL,
                "-d",
                hostname,
                "--agree-tos",
                "-n",
            ]
            if "TEST_CERT" in os.environ:
                cmd.append("--test-cert")
            print(f"Running: {cmd}")
            subprocess.run(cmd)


### Run renewal in a loop
while True:
    time.sleep(SLEEP)
    subprocess.run(["certbot", "renew"])
