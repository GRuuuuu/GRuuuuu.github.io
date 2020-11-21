---
title: "[Ansible] Roles"
categories: 
  - Ansible
tags:
  - DevOps
  - Ansible
last_modified_at: 2020-11-21T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 포스팅에서는 Ansible의 **Roles**에 대해서 알아보겠습니다.  

# Roles?
예를들어서 프로젝트를 진행한다고 했을 때 마구잡이로 프로그래밍을 하게되면 유지보수하기도, 미래에 재사용하기도 어렵습니다.  
이런 문제들을 방지하기위해 코드의 구성을 체계화하고 모듈화를 시키는 것이 일반적입니다.   

이와 비슷하게 Ansible에서 Playbook에 대한 체계화를 시켜주는 것이 **Role**입니다.

Role은 여러 연관된 Task들을 체계화시키고 여러 playbook에 추가시켜 사용할 수 있습니다.  

## Role만들기
먼저 모든 role들은 ansible이 참조할 수 있도록 항상 "roles"폴더내에 있어야 합니다.  
~~~sh
$ mkdir roles
$ cd roles
~~~

Ansible에서 Role을 생성하는 명령어는 다음과 같습니다.  
~~~sh
$ ansible-galaxy init {이름}

- Role {이름} was created successfully
~~~

role의 이름으로 폴더가 생성되게 되고 그 안에는 다음과같은 파일들이 자동으로 생성이 됩니다.  
~~~sh
$ tree .
.
├── README.md
├── defaults
│   └── main.yml
├── files
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   └── main.yml
├── templates
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml

8 directories, 8 files
~~~
## Role의 구성요소

### defaults
각 task에서 사용할 기본값을 설정

### files
정적파일을 두는 곳입니다. task에서는 files폴더에서 필요한 파일들을 끌어다가 사용할 수 있습니다.  

### handlers
참고: [[Ansible] Handlers](https://gruuuuu.github.io/ansible/ansible-handler/#)  
task에서 사용할 handler들을 두는 폴더입니다.  

### meta
meta폴더의 main.yml은 role의 메타정보를 담고있습니다.  

자동으로 생성된 main.yml파일은 다음과 같이 생성됩니다. 제작자, 회사, 라이센스 정보 등 role에 필요한 dependency정보들이 기입되어야 합니다.  
~~~
galaxy_info:
  author: your name
  description: your role description
  company: your company (optional)

  license: license (GPL-2.0-or-later, MIT, etc)

  min_ansible_version: 2.1
  galaxy_tags: []

dependencies: []
~~~

### task
role의 핵심 폴더입니다.  
role이 실제로 동작할 내용이 담겨져 있습니다.  

### templates
python의 Jinja2템플릿 엔진에 기반한 템플릿 변수들을 담을 수 있습니다.  
.j2 확장자를 가지고 있으며 파일명은 아무거나 지정하셔도 됩니다.  

EX)  
**nginx의 default.conf파일을 수정해서 타겟서버에 nginx를 설치구성하고싶은 경우**  

1. `template/default.conf.j2` 파일을 생성한 뒤, 원하는 대로 커스텀  
2. ip나 이름과 같이 가변적인 변수들은 `{{VAR}}`와 같이 표시 (나중에 렌더링할때 vars폴더에서 변수를 참조할 것)
3. task에서 다음과 같이 렌더링
~~~
  - name: Add Default config
    template:
      src: templates/default.conf.j2
      dest: '/etc/nginx/conf.d/default.conf'
~~~

### vars
`vars/main.yml`은 role에서 사용할 변수들의 목록입니다.  

아래와 같이 구성될 수 있으며 :  
~~~
---
var1: 1
var2: /etc/hosts
var3: hihihihi
~~~

template나 task에서 `{{var1}}`이런식으로 변수를 호출해서 사용할 수 있습니다.  


## Role 사용
작성된 role은 playbook에서 다음과 같이 사용될 수 있으며:    
~~~
---
- hosts:
    - test
  roles:
    - role: {role이름}
~~~

실행될때 내부적으로 다음 위치에서 role을 찾습니다.  
`./roles`, `/home/ansible/.ansible/roles`, `/usr/share/ansible/roles`, `/etc/ansible/roles`   
해당 위치에 적절한 role이 없으면 에러가 발생합니다.   

----
