import re


def host_matches(specific_host: str, potentially_wildcard_host: str):
    # FIXME: there are a lot of edge cases:
    regex = potentially_wildcard_host.replace('.', r'\.').replace('*', '[^.]+')
    return bool(re.match(regex, specific_host))


def bautify_config(config: str) -> str:
    config = re.sub(r'^\s*\n', '', config)
    tabsize = len(re.match(r'^(\s*)', config).group(1))
    tabregex = re.compile(r'^\s{0,' + str(tabsize) + '}')
    config = '\n'.join(re.sub(tabregex, '', line) for line in config.split('\n'))
    return re.sub('\n{3,}', '\n', config.strip())

