from config import Configuration
from tabulate import tabulate
from typing import List, Optional

def do_ls(configuration: Configuration) -> None:
    print()
    print("======================")
    print("| SSL Certificates   |")
    print("======================")
    ssl = [[entry.domain_name, entry.exists() and 'yes' or 'no'] for entry in configuration.ssl_entries]
    print(tabulate(ssl, headers=['Domain', 'Configured'], tablefmt='orgtbl'))

    print()

    print("======================")
    print("| Rules              |")
    print("======================")
    entries = [[*entry.to_columns(), configuration.get_ssl_by_domain(entry.domain_name).exists() and 'yes' or 'no'] for entry in configuration.entries]
    print(tabulate(entries, headers=['Domain', 'Type', 'Configuration', 'Enabled', 'Secured'], tablefmt='orgtbl'))
    print()


def add_docker(subdomain: str, port: int) -> None:
    print(f"Add docker: subdomain={subdomain}, port={port}")


def add_redirect(source: str, target: str) -> None:
    print(f"Add redirect: from={source} to={target}")


def add_reverse_proxy(subdomain: str, upstream: str) -> None:
    print(f"Add reverse-proxy: subdomain={subdomain}, upstream={upstream}")


def setup_ssl(domains: Optional[List[str]], wildcard: bool = False) -> None:
    if not domains:
        msg = "Setup SSL for all configured domains (stub)"
        if wildcard:
            msg += " (wildcard enabled)"
        print(msg)
    else:
        doms = ', '.join(domains)
        if wildcard:
            print(f"Setup SSL for: {doms} (wildcard enabled)")
        else:
            print(f"Setup SSL for: {doms}")


def remove_site(subdomain: str) -> None:
    print(f"Remove site: {subdomain}")


def disable_site(subdomain: str) -> None:
    print(f"Disable site: {subdomain}")


def enable_site(subdomain: str) -> None:
    print(f"Enable site: {subdomain}")