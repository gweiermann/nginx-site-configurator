# What is it?
It's a lightweight .conf generator for your nginx host configuration.
It will handle ssl, https upgrade, redirects to other domains/subdomains, reverse proxies (with websocket integration), setting up single page applications (spa), php websites (not working at the moment).

# Setup
Get the script [update_sites.py](update_sites.py) and place a file named [sites.json](sites.json) in that same directory (you can change the filename inside `update_sites.py` at `config_filename`)

The file [sites.json](sites.json) in this repository tries to show you an example how to use.
There are no more functionalites than shown in that file. If you don't want to use one thing like 'spa' you mustn't delete it. Just leave it empty :)

# 
