# nginx-cli at a Glance

`nginx-cli` keeps your nginx virtual-host configuration in a single `sites.json` file and writes out the final config for you. Commands are available through the standalone binary `nginx-cli`, so no Python environment is required once it is installed.

## Installation

1. **Download and install (one-liner)** – replace the owner/branch if you forked the project:

   ```bash
   wget -O nginx-cli https://github.com/gweiermann/nginx-site-configurator/releases/latest/download/nginx-cli && chmod +x nginx-cli && ./nginx-cli --install
   ```

The installer copies the binary to `~/.local/bin/nginx-cli`, ensures it is executable, appends a managed alias block, and (if available) configures argcomplete-based tab completion in `~/.bashrc`. It also attempts to install `argcomplete` for the current user, but only prints a warning if that fails.

Open a new shell or run `source ~/.bashrc` to activate the alias and completions.

## Uninstall

Run the executable with the `--uninstall` flag:

```bash
nginx-cli --uninstall
```

This removes the alias/completion blocks from `~/.bashrc`, deletes `~/.local/bin/nginx-cli`, and removes the copy you invoked (if it exists outside `~/.local/bin`).

## Autocomplete

The CLI uses `argcomplete` so tab completion is context aware and dynamic:

- Commands and options are suggested as you type.
- Hostname arguments (e.g. for `remove`, `disable`, `enable`, and `setup-ssl --for`) are populated from the current contents of `sites.json`.

If completions stop working, ensure `argcomplete` is installed (`python3 -m pip install --user argcomplete`) and re-run `source ~/.bashrc`.

## Commands & Examples

- **`nginx-cli ls`** – show every configured host and whether it already uses SSL.
  - Add `--ssl` to see only certificate status: `nginx-cli ls --ssl`
- **`nginx-cli add docker <host> <port>`** – point a domain at a Docker container that listens on a local port.
- **`nginx-cli add redirect <from> <to>`** – send visitors from one host to another.
- **`nginx-cli add reverse-proxy <host> <upstream>`** – forward traffic to an external HTTPS URL.
- **`nginx-cli setup-ssl [--for DOMAIN] [--wildcard]`** – print the `acme.sh` commands needed for missing certificates.
- **`nginx-cli remove <host...>`** – delete one or more hosts from the config.
- **`nginx-cli disable <host>` / `nginx-cli enable <host>`** – toggle whether a host is served without removing it.
- **`nginx-cli apply`** – rewrite your nginx config file and remind you to reload nginx.

After changing the config, run `nginx-cli apply` and then on your server: `sudo service nginx reload`.
