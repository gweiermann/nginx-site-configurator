import argparse
from os import path
from typing import List
from config import Configuration

try:
    import argcomplete
except Exception:
    argcomplete = None


def _get_config_filename() -> str:
    """Return the path to ``sites.json`` shipped with the CLI."""
    script_directory = path.dirname(path.realpath(__file__))
    return path.join(script_directory, "sites.json")


def _known_hostnames() -> List[str]:
    """Load hostnames from the configuration file for autocomplete consumers."""
    try:
        configuration = Configuration.load(_get_config_filename())
    except Exception:
        return []
    return [rule.hostname for rule in configuration.rules]


def _hostname_completer(prefix, parsed_args, **_kwargs):
    """Provide hostname suggestions filtered by ``prefix`` for argcomplete."""
    return [host for host in _known_hostnames() if host.startswith(prefix)]

def parse_args():
    parser = argparse.ArgumentParser(
        prog='nginx-cli',
        description='For setting up reverse proxies (docker apps), redirects and SSL.',
        epilog='Consult https://github.com/gweiermann/nginx-site-configurator for more information.')

    parser.add_argument('--install', action='store_true', help='Install nginx-cli into ~/.local/bin and configure shell integration.')
    parser.add_argument('--uninstall', action='store_true', help='Remove nginx-cli and undo shell integration changes.')

    subparsers = parser.add_subparsers(dest='command')

    # ls
    parser_ls = subparsers.add_parser('ls', help='Lists the whole configuration.')
    parser_ls.add_argument('--ssl', action='store_true', help='List all SSL certificates instead of rules.')

    # apply
    parser_apply = subparsers.add_parser('apply', help='Updates the nginx configuration with the current setup.')

    # add
    parser_add = subparsers.add_parser('add', help='Adds an entry to the configuration.')
    add_sub = parser_add.add_subparsers(dest='add_type', required=True)

    p_docker = add_sub.add_parser('docker', help='Add docker-backed site')
    p_docker.add_argument('hostname', help='sub.domain.tld for the site')
    p_docker.add_argument('port', type=int, help='Local port where docker container listens')

    p_redirect = add_sub.add_parser('redirect', help='Add a redirect from one host to another')
    p_redirect.add_argument('source', help='sub.domain.tld to redirect from')
    p_redirect.add_argument('target', help='Destination domain (e.g. other.domain.tld)')

    p_rp = add_sub.add_parser('reverse-proxy', help='Add a reverse proxy to an upstream URL')
    p_rp.add_argument('hostname', help='sub.domain.tld for the proxy')
    p_rp.add_argument('upstream', help='Upstream URL, e.g. https://example.com')

    # setup-ssl
    parser_ssl = subparsers.add_parser('setup-ssl', help='Create/renew SSL certificates')
    hosts_option = parser_ssl.add_argument('--for', dest='hosts', action='append', metavar='DOMAIN',
                                           help='Host to enable SSL for. Can be repeated; if omitted, acts on all hosts.')
    parser_ssl.add_argument('--wildcard', action='store_true', dest='wildcard',
                            help='Enable wildcard support for hostnames (treat patterns like *.domain.tld)')

    # remove/disable/enable
    parser_remove = subparsers.add_parser('remove', help='Remove one or more entries from the configuration')
    remove_arg = parser_remove.add_argument('hostname', nargs='+', help='One or more sub.domain.tld values to remove')

    parser_disable = subparsers.add_parser('disable', help='Disable a configured site')
    disable_arg = parser_disable.add_argument('hostname', help='sub.domain.tld to disable')

    parser_enable = subparsers.add_parser('enable', help='Enable a configured site')
    enable_arg = parser_enable.add_argument('hostname', help='sub.domain.tld to enable')

    if argcomplete:
        try:
            remove_arg.completer = _hostname_completer
            disable_arg.completer = _hostname_completer
            enable_arg.completer = _hostname_completer
            hosts_option.completer = _hostname_completer
            argcomplete.autocomplete(parser)
        except Exception:
            # don't fail if argcomplete misbehaves
            pass

    args = parser.parse_args()

    if args.install and args.uninstall:
        parser.error("--install and --uninstall cannot be used together.")

    if not args.install and not args.uninstall and args.command is None:
        parser.error('No command provided. Run with --help for usage information.')

    return args