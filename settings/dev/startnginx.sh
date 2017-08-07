#!/bin/bash
mkdir -p /home/ubuntu/nginxdata/root
mkdir -p /home/ubuntu/nginxdata/certs
#copy these for permission issue
sudo cp /etc/letsencrypt/live/dev.chatty.top/* /home/ubuntu/nginxdata/certs
echo "hello" > /home/ubuntu/nginxdata/root/index.html
#docker stop nginx | xargs docker rm
docker run --name nginx -d -p 80:80 -p443:443 -p 8081:8081 -v /etc/letsencrypt/live/dev.chatty.top/:/etc/letsencrypt/live/dev.chatty.top/ \
                                                    -v /home/ubuntu/nginxdata:/data \
                                                    -v /home/ubuntu/Chatty/settings/dev/nginx.conf:/etc/nginx/conf.d/devnginx.conf \
                                                    -v /dev/null:/etc/nginx/conf.d/default.conf nginx:1.10.3-alpine
