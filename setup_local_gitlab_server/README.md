1. Setup docker server
   Step1: export GITLAB_HOME=/srv/gitlab
   Step2: Run 'sh $PATH/gitlab_ce.sh'
 
   Now you can visit gitlab using url http://ip-addr:8929 on computer in the same network with computer running gitlab docker instance


2. Backup gitlab
   Step 1: In new gitlab server
	   Install new gitlab by using gitlab_ce.sh (Waiting for gitlab installation)
   	   docker exec -it gitlab gitlab-ctl stop puma
	   docker exec -it gitlab gitlab-ctl stop sidekiq

   Step 2: In old gitlab server
	   docker exec -it gitlab gitlab-backup (Backup file will be stored at /srv/gitlab/data/backups)
	   Change permission of this file by using 'sudo chmod 777 ${path-to-backup-file}'
	   Copy backup file to folder '/srv/gitlab/data/backups' in new server
	   
   Step 3: In new gitlab server	
	   Copy 'db_key_base' in '/srv/gitlab/config/gitlab-secrets.json' of old gitlab server to new gitlab server
	   docker exec -it gitlab gitlab-rails runner "Project.where.not(import_url: nil).each { |p| p.import_data.destroy if p.import_data }"
	   docker container restart gitlab


