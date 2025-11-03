#!/bin/bash

echo "Installing neccessary 
sudo apt update -yq
sudo apt install -yq git python3 python3-pip
git clone -q https://github.com/gweiermann/nginx-site-configurator ~/nginx-cli
pip3 install -q argcomplete tabulate

echo "source $(pwd)/bashrc.sh \# added by NGINX-CLI" >> ~/.bashrc