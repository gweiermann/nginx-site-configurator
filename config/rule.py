import json


class Rule:
    def from_json(data):
        from .docker_rule import DockerRule
        from .redirect_rule import RedirectRule
        from .reverse_proxy_rule import ReverseProxyRule

        types = [DockerRule, RedirectRule, ReverseProxyRule]
        for rule_type in types:
            if rule_type.is_suitable(data):
                return rule_type.from_json(data)
        raise Exception(f"Couldn't parse {json.dumps(data)}")

    def __init__(self, hostname: str, enabled: bool):
        self.hostname = hostname
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled

