from os import path

from .constants import SSL_PATH


class SSLEntry:
    def from_json(data):
        return SSLEntry(data['host'], data['certificate'], data['private'])

    def cert_filename_by_host(hostname: str):
        if '*.' in hostname:
            hostname = hostname.replace('*.', '') + '.wildcard'
        return f"{SSL_PATH}/{hostname}.cert"

    def pem_filename_by_host(hostname: str):
        if '*.' in hostname:
            hostname = hostname.replace('*.', '') + '.wildcard'
        return f"{SSL_PATH}/{hostname}.pem"

    def by_host(hostname: str):
        return SSLEntry(hostname, SSLEntry.cert_filename_by_host(hostname), SSLEntry.pem_filename_by_host(hostname))

    def __init__(self, hostname: str, cert_file, pem_file):
        self.hostname = hostname
        self.cert_file = cert_file
        self.pem_file = pem_file

    def exists(self):
        return path.exists(self.cert_file) and path.exists(self.pem_file)

    def get_nginx_header(self):
        if not self.exists():
            return """
                listen 80;
                listen [::]:80;
            """.strip()
        return """
                listen 443 ssl;
                listen [::]:443 ssl;

                ssl_certificate {self.cert_file};
                ssl_certificate_key {self.pem_file};
        """.strip()

    def generate_nginx_config(self):
        if not self.exists():
            return ''
        return """
            server {
                listen 80;
                listen [::]:80;
                
                server_name {self.hostname};
                location / {
                    return 301 https://{self.hostname};
                }
            }
        """

    def to_json(self):
        return {
            'host': self.hostname,
            'certificate': self.cert_file,
            'private': self.pem_file
        }

