---
title: "[Ansible] Handlers"
categories: 
  - Ansible
tags:
  - DevOps
  - Ansible
last_modified_at: 2020-11-19T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 포스팅에서는 Ansible의 **Handler**에 대해서 기술하겠습니다.  

# Handlers?
**Handler**는 함수와 비슷합니다.  
Task가 할 수 있는 일을 똑같이 할 수 있으며, Playbook의 Task에서 Handler를 호출하게되면 해당 Handler가 호출되어 실행되는 식으로 동작합니다.  
위에서 함수와 비슷하다고 하였는데, 우리가 코드를 짤 때 반복되는 부분을 함수로 만들어서 필요할때마다 가지고 오듯이, Handler도 비슷하게 작성해주시면 됩니다.  

아래의 playbook을 보면서 자세히 살펴보겠습니다.
~~~sh
- hosts: test
  become: yes
  tasks:
   - name: Install Nginx
     apt:
       name: nginx
       state: latest
       update_cache: true
     notify:
      - Start Nginx

  handlers:
   - name: Start Nginx
     service:
       name: nginx
       state: started
~~~

[test]태그를 가지는 서버에 해당 playbook을 적용할거고,  
`become:yes` 구문에서는 아래 tasks는 root권한으로 실행할 것을 명시해두었습니다.  

tasks 파트에서는 Nginx를 설치하는 작업이 들어가 있습니다.  
원래는 apt구문에서 설치는 끝이 날텐데 밑에 `notify`라는 구문이 또 있습니다.  

요 `notify`구문은 handler를 호출하는 구문으로써 위의 tasks를 모두 마친 뒤에 handler를 호출하라는 뜻입니다.  

handler를 호출할때에는 `name`을 기준으로 호출하게 되어있습니다.  

실제로 동작을 하게되면:  
~~~sh
$ ansible-playbook -i hosts.inv install-nginx.yaml

PLAY [test] **********************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************
ok: [169.59.4.60]

TASK [Install Nginx] *************************************************************************************************************************
changed: [169.59.4.60]

RUNNING HANDLER [Start Nginx] ****************************************************************************************************************
ok: [169.59.4.60]

PLAY RECAP ***********************************************************************************************************************************
169.59.4.60                : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

~~~

TASK에서 `Install Nginx`를 하게 되고, 타겟서버에 nginx가 설치되어있지 않으니 설치를 진행해 상태가 changed가 되었습니다.  
그리고 설치를 했으니 task를 마친 뒤, `Start Nginx` handler를 호출하여 실행하는것을 확인할 수 있습니다.  

> 타겟서버에 nginx가 설치되어 있는데 playbook을 돌릴경우:  
>![image](https://user-images.githubusercontent.com/15958325/99637690-8e860a00-2a88-11eb-8c37-38d577061a66.png)  
>이미 설치되어있기 때문에 task를 진행하지 않고 넘어갑니다. 그래서 handler도 실행되지 않음!  


----