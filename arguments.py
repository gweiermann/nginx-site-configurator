import argparse
from config import Configuration

try:
    import argcomplete
except Exception:
    argcomplete = None

def parse_args():
    # TODO: add autocomplete
    # domain_names = [rule.domain_name for rule in configuration.rules] 

    parser = argparse.ArgumentParser(
        prog='nginx-cli',
        description='For setting up reverse proxies (docker apps), redirects and SSL.',
        epilog='Consult https://github.com/gweiermann/nginx-site-configurator for more information.')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # ls
    parser_ls = subparsers.add_parser('ls', help='Lists the whole configuration.')
    parser_ls.add_argument('--ssl', action='store_true', help='List all SSL certificates instead of rules.')

    # apply
    parser_apply = subparsers.add_parser('apply', help='Updates the nginx configuration with the current setup.')

    # add
    parser_add = subparsers.add_parser('add', help='Adds an entry to the configuration.')
    add_sub = parser_add.add_subparsers(dest='add_type', required=True)

    p_docker = add_sub.add_parser('docker', help='Add docker-backed site')
    p_docker.add_argument('subdomain', help='sub.domain.tld for the site')
    p_docker.add_argument('port', type=int, help='Local port where docker container listens')

    p_redirect = add_sub.add_parser('redirect', help='Add a redirect from one host to another')
    p_redirect.add_argument('source', help='sub.domain.tld to redirect from')
    p_redirect.add_argument('target', help='Destination domain (e.g. other.domain.tld)')

    p_rp = add_sub.add_parser('reverse-proxy', help='Add a reverse proxy to an upstream URL')
    p_rp.add_argument('subdomain', help='sub.domain.tld for the proxy')
    p_rp.add_argument('upstream', help='Upstream URL, e.g. https://example.com')

    # setup-ssl
    parser_ssl = subparsers.add_parser('setup-ssl', help='Create/renew SSL certificates')
    parser_ssl.add_argument('--for', dest='domains', action='append', metavar='DOMAIN',
                            help='Domain to enable SSL for. Can be repeated; if omitted, acts on all domains.')
    parser_ssl.add_argument('--wildcard', action='store_true', dest='wildcard',
                            help='Enable wildcard support for subdomains (treat patterns like *.domain.tld)')

    # remove/disable/enable
    parser_remove = subparsers.add_parser('remove', help='Remove an entry from the configuration')
    parser_remove.add_argument('subdomain', help='sub.domain.tld to remove')

    parser_disable = subparsers.add_parser('disable', help='Disable a configured site')
    parser_disable.add_argument('subdomain', help='sub.domain.tld to disable')

    parser_enable = subparsers.add_parser('enable', help='Enable a configured site')
    parser_enable.add_argument('subdomain', help='sub.domain.tld to enable')

    if argcomplete:
        try:
            argcomplete.autocomplete(parser)
        except Exception:
            # don't fail if argcomplete misbehaves
            pass

    return parser.parse_args()