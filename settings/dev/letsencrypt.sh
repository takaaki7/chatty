#!/bin/bash
cd /home/ubuntu
git clone https://github.com/letsencrypt/letsencrypt.git
cd letsencrypt
#./letsencrypt-auto certonly --webroot --webroot-path /home/ubuntu/nginxroot -d dev.chatty.top
./letsencrypt-auto --standalone certonly -d dev.chatty.top
