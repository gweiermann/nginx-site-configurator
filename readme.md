# nginx-cli at a Glance

`nginx-cli` is a small helper that keeps an `nginx` virtual-host list in a single `sites.json` file and writes the final config for you. Run it from the project root with `python nginx-cli <command>`. Each command updates `sites.json` immediately and regenerates your nginx config when needed.

## Commands & Examples
- **`ls`** – shows every configured host and whether it already uses SSL.
  - Example: `python nginx-cli ls`
  - Add `--ssl` to see only certificate status: `python nginx-cli ls --ssl`
- **`add docker <host> <port>`** – points a domain at a Docker container that listens on a local port.
  - Example: `python nginx-cli add docker app.example.com 8080`
- **`add redirect <from> <to>`** – sends visitors from one host to another.
  - Example: `python nginx-cli add redirect old.example.com new.example.org`
- **`add reverse-proxy <host> <upstream>`** – forwards traffic to an external HTTPS URL.
  - Example: `python nginx-cli add reverse-proxy status.example.com https://statuspage.com`
- **`setup-ssl [--for DOMAIN] [--wildcard]`** – prints the `acme.sh` commands you need to issue and install missing certificates.
  - Example: `python nginx-cli setup-ssl`
- **`remove <host...>`** – deletes one or more hosts from the config.
  - Example: `python nginx-cli remove blog.example.com`
- **`disable <host>` / `enable <host>`** – toggle whether a host is served without removing it.
  - Example: `python nginx-cli disable beta.example.com`
- **`apply`** – rewrites your local nginx config file and reminds you to reload nginx.
  - Example: `python nginx-cli apply`

After changing the config, run `python nginx-cli apply` and then on your server: `sudo service nginx reload`.
