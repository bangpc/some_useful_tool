sudo docker run --detach \     
        --hostname 192.168.0.230 \
        --publish 8929:8929 --publish 2289:22 \
        --name gitlab \        
        --restart always \     
        --volume /mnt/data2/gitlab/config:/etc/gitlab \
        --volume /mnt/data2/gitlab/logs:/var/log/gitlab \
        --volume /mnt/data2/gitlab/data:/var/opt/gitlab \
        --shm-size 256m \      
        gitlab/gitlab-ce:latest
