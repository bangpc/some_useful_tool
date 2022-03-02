# post setup
  Step1: docker exec -it gitlab bash
  Step2: Add the following line to /etc/gitlab/gitlab.rb and run gitlab-ctl reconfigure
         external_url "ip-addr:8929"
         gitlab_rails['gitlab_shell_ssh_port'] = 2289

# Get password of root account first time installed
  Step1: docker exec -it gitlab bash
  Step2: cat /etc/gitlab/initial_root_password

