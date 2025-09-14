#!/usr/bin/python3

import json
import re
from os import path

script_directory = path.dirname(path.realpath(__file__))

config_filename = path.join(script_directory, "sites.json")

def read_config(filename):
    with open(filename, 'r') as f:
        raw = f.read()
    return json.loads(raw)


def find_ssl_certificate(certs, domain):
    for cert_domain, files in certs:
        if re.search("^" + cert_domain.replace('.', r'\.').replace('*', '[^.]+') + "$", domain):
            return files
    return None


def upgrade_https(domain):
    return f"""
    server {{
        listen 80;
        listen [::]:80;
        
        server_name {domain};
        location / {{
            return 301 https://{domain};
        }}
    }}"""




def build_domain_redirect(_from, to, *, temporary = True, ssl):
    return f"""
    server {{
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name {_from};

        {ssl}

        return {307 if temporary else 301} $scheme://{to}$request_uri;
    }}"""


def build_reverse_proxy(url, domain, *, ssl):
    return f"""
    server {{
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name {domain};

        {ssl}

        location / {{
            proxy_pass {url};
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # WebSocket support (nginx 1.4)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }}
    }}"""


def build_spa(root, conf, *, ssl):
    domain = conf['domain']

    rewrite = ""
    if 'rewrite' in conf:
        rewrite = f"location / {{ rewrite ^/$ https://$server_name{conf['rewrite']}; }}"

    return f"""
    server {{
        listen 443 ssl;
        listen [::]:443 ssl;
        server_name {domain};

        {ssl}

        root {root};

        location / {{
            if ($request_uri ~ ^/(.*)\.html(\?|$)) {{
                return 302 /$1;
            }}
            try_files $uri $uri.html $uri/ =404;
        }}
        {rewrite}
    }}
    """


config = read_config(config_filename)
out_file = config['out_file']
certs = config['ssl'].items()

def get_cert(domain):
    files = find_ssl_certificate(certs, domain)
    if files is None:
        raise Exception(f"There's no certificate for domain {domain}")
    return f"""
        ssl_certificate {files['certificate']};
        ssl_certificate_key {files['private']};""".strip()

out = []

for entry in config['entries']:
    domain = entry['domain']
    out.append(upgrade_https(domain))

    if 'redirect' in entry:
        to = entry['redirect']
        out.append(build_domain_redirect(domain, to, temporary=True, ssl=get_cert(domain)))
    elif 'from_port' in entry:
        port = entry['from_port']
        out.append(build_reverse_proxy(f"http://localhost:{port}", domain, ssl=get_cert(domain)))
    elif 'reverse_proxy' in entry:
        url = entry['reverse_proxy']
        out.append(build_reverse_proxy(url, domain, ssl=get_cert(domain)))

def pretty(code):
    return '\n'.join(map(lambda x: x.replace('    ', '', 1), code.split('\n')))

output = f"### THIS IS AUTOMATICALLY GENERATED through {__file__}. WILL BE OVERWRITTEN, SO DON'T MODIFY. ###\n\n"
output += pretty('\n'.join(out))

with open(out_file, 'w') as f:
    f.write(output)

print(f"wrote file to {out_file}.")
print()
print("if not happend, enable the configuration in nginx:")
print("sudo ln -s /etc/nginx/sites-available/<config-file.conf> /etc/nginx/sites-enabled/<config-file.conf>")
print()
print("run `service nginx reload` to apply the changes.")
