import json

from .constants import DEFAULT_OUT_FILE
from .rule import Rule
from .ssl_entry import SSLEntry
from .utils import bautify_config, host_matches


class Configuration:
    def load(filename):
        try:
            with open(filename, 'r') as f:
                raw = json.load(f)
                out_file = raw['out_file']
                ssl_entries = [SSLEntry.from_json(entry) for entry in raw['ssl']]
                rules = [Rule.from_json(entry) for entry in raw['rules']]
                return Configuration(filename, out_file, ssl_entries, rules)
        except Exception:
            return Configuration(filename, DEFAULT_OUT_FILE, [], [])

    def __init__(self, config_file: str, out_file: str, ssl_entries, rules):
        self.config_file = config_file
        self.out_file = out_file
        self.ssl_entries = ssl_entries
        self.rules = rules

    def get_ssl_by_host(self, hostname: str):
        for ssl_entry in self.ssl_entries:
            if host_matches(hostname, ssl_entry.hostname):
                return ssl_entry
        return None

    def get_rule_by_host(self, hostname: str):
        for rule in self.rules:
            if host_matches(hostname, rule.hostname):
                return rule
        return None

    def get_rule_by_port(self, port: int):
        for rule in self.rules:
            if getattr(rule, 'port', -1) == port:
                return rule
        return None

    def fill_missing_ssl_entries(self):
        for entry in self.rules:
            if self.get_ssl_by_host(entry.hostname) is None:
                self.ssl_entries.append(SSLEntry.by_host(entry.hostname))

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'out_file': self.out_file,
                'ssl': [entry.to_json() for entry in self.ssl_entries],
                'rules': [entry.to_json() for entry in self.rules]
            }, f, indent=4)

    def generate_nginx_config(self):
        return '\n\n'.join(map(bautify_config, [
            "### WARNING: This file is auto generated and is likely to be overwritten. Modifications can get lost. ###",
            "# HTTPS Upgrades:",
            *[entry.generate_nginx_config() for entry in self.ssl_entries if entry.exists()],
            "# Rules:",
            *[entry.generate_nginx_config(self.get_ssl_by_host(entry.hostname)) for entry in self.rules if entry.is_enabled()]
        ]))
    
    def apply_to_nginx_config(self):
        with open(self.out_file, 'w') as f:
            f.write(self.generate_nginx_config())

    def add_rule(self, rule: Rule):
        existent_rule = self.get_rule_by_host(rule.hostname)
        if existent_rule:
            self.rules.remove(existent_rule)
        self.rules.append(rule)
        existent_ssl = self.get_ssl_by_host(rule.hostname)
        if existent_ssl is None:
            self.ssl_entries.append(SSLEntry.by_host(rule.hostname))

    def remove_rule(self, hostname: str):
        rule = self.get_rule_by_host(hostname)
        if rule is None:
            raise Exception("rule doesn't exist.")
        existent_ssl = self.get_ssl_by_host(rule.hostname)
        if existent_ssl is not None:
            self.ssl_entries.remove(existent_ssl)
        self.rules.remove(rule)

