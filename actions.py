from config import Configuration, DockerRule, RedirectRule, ReverseProxyRule
from tabulate import tabulate
from typing import List, Optional
from os import path

def ls(configuration: Configuration) -> None:
    ssl = [[entry.domain_name, entry.exists() and 'yes' or 'no'] for entry in configuration.ssl_entries]
    print(tabulate(ssl, headers=['Domain', 'Configured'], tablefmt='orgtbl'))

def ls_ssl(configuration: Configuration) -> None:
    entries = [[*entry.to_columns(), configuration.get_ssl_by_domain(entry.domain_name).exists() and 'yes' or 'no'] for entry in configuration.rules]
    print(tabulate(entries, headers=['Domain', 'Type', 'Configuration', 'Enabled', 'Secured'], tablefmt='orgtbl'))
    print()

def confirm(message: str):
    """Prompt the user to confirm an action.

    The prompt treats Enter as the default "yes" answer. Returns True for
    yes, False for no. Keeps prompting until a valid answer is given.
    """
    prompt = f"{message} [Y/n]: "
    while True:
        try:
            resp = input(prompt)
        except EOFError:
            # If input is not available, treat as negative to be safe
            return False

        # Default to 'yes' when pressing Enter
        if resp == "":
            return True

        value = resp.strip().lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False

        print("Please enter 'y' or 'n' (default: 'y').")

def assert_domain_is_available(configuration: Configuration, domain_name: str):
    existing_rule = configuration.get_rule_by_domain(domain_name)
    if existing_rule is not None:
        if not confirm("A rule with given domain name already exists. Do you want to replace it?"):
            raise Exception("Operation was aborted.")


def assert_port_is_available(configuration: Configuration, port: int):
    existing_rule = configuration.get_rule_by_port(port)
    if existing_rule is not None:
        raise Exception(f"Error: A rule with given port already exists: {existing_rule.domain_name}. Please remove it beforehand if you want to replace the configuration.")



def apply(configuration: Configuration):
    configuration.save()
    configuration.apply_to_nginx_config()

    basename = path.basename(configuration.out_file)

    print(f"wrote file to {configuration.out_file}.")
    print()
    print("if not happend, enable the configuration in nginx:")
    print(f"sudo ln -s /etc/nginx/sites-available/{basename} /etc/nginx/sites-enabled/{basename}")
    print()
    print("run `service nginx reload` to apply the changes.")

    print("To apply these changes, run: \nsudo service nginx reload")


def add_docker(configuration: Configuration, domain_name: str, port: int) -> None:
    assert_domain_is_available(configuration, domain_name)
    assert_port_is_available(configuration, port)
    configuration.add_rule(DockerRule(domain_name, port, True))
    apply(configuration)


def add_redirect(configuration: Configuration, source: str, target: str) -> None:
    assert_domain_is_available(configuration, source)
    configuration.add_rule(RedirectRule(source, target, True))
    apply(configuration)


def add_reverse_proxy(configuration: Configuration, domain_name: str, upstream: str) -> None:
    assert_domain_is_available(configuration, domain_name)
    configuration.add_rule(ReverseProxyRule(domain_name, upstream, True))
    apply(configuration)


def setup_ssl(configuration: Configuration, domains: Optional[List[str]], wildcard: bool = False) -> None:
    if domains:
        raise Exception("Specifying individual domains is not supported, yet.")
    if wildcard:
        raise Exception("Wildcards are not supported on this command, but are supposed to be supported soon.")

    ssl_entries = [entry for entry in configuration.ssl_entries if not entry.exists()]

    if len(ssl_entries) == 0:
        print("You're all set. Each rule is already secured.")
        return

    ssls = [[entry.domain_name] for entry in configuration.ssl_entries if entry.exists()]
    issue_script = "acme.sh --issue --nginx " + ' '.join(f"-d {ssl.domain_name}" for ssl in ssl_entries)
    install_script = '\n'.join(f"""
acme.sh --install-cert -d {ssl.domain_name} \\
    --key-file       {ssl.pem_file}  \\
    --fullchain-file {ssl.cert_file} \\
    --reloadcmd     "service nginx force-reload"
""".strip() for ssl in ssl_entries)

    print()
    print("The following domains need to be secured:\n")
    print(tabulate(ssls, headers=['Domain'], tablefmt='orgtbl'))

    print(f"""
To enable ssl support for all of them follow the following steps:
(The following tutorial worked at the writing of 2025-11-3. Learn more at https://acme.sh)

1. Install acme.sh:
curl https://get.acme.sh | sh -s email=my@example.com
source ~/.bashrc

2. Issue all certs:
{issue_script}

3. Add them to nginx
{install_script}
""")

def remove_site(configuration: Configuration, domain_name: str) -> None:
    configuration.remove_rule(domain_name)
    apply(configuration)


def disable_site(configuration: Configuration, domain_name: str) -> None:
    rule = configuration.get_rule_by_domain(domain_name)
    rule.enabled = False
    apply(configuration)


def enable_site(configuration: Configuration, domain_name: str) -> None:
    rule = configuration.get_rule_by_domain(domain_name)
    rule.enabled = True
    apply(configuration)