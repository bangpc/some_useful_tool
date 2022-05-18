sudo docker run --detach \
  --publish 8929:8929 --publish 80:80 --publish 2289:22 \
  --hostname 192.168.0.231 \
  --name gitlab \
  --volume /srv/gitlab/config:/etc/gitlab \
  --volume /srv/gitlab/logs:/var/log/gitlab \
  --volume /srv/gitlab/data:/var/opt/gitlab \
  --restart always \
  --shm-size 256m \
  --env GITLAB_OMNIBUS_CONFIG="external_url 'http://192.168.0.231:8929'; 
                               gitlab_rails['gitlab_shell_ssh_port'] = 2289; 
                               gitlab_rails['initial_root_password'] = 'llq123a@';" \
  gitlab/gitlab-ce:14.8.1-ce.0


# gitlab_rails['backup_keep_time'] = 3600
