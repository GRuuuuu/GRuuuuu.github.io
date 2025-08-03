---
title: "Ansible Basics"
slug: ansible-basic
tags:
  - DevOps
  - Ansible
date: 2020-11-13T13:00:00+09:00
series: ["Ansible"]
series_order: 1
---

## Overview
이번 포스팅에서는 Ansible이란 무엇인지, 구조와 설치방법에 대해서 기술하도록 하겠습니다.  

# Ansible?
![image](https://user-images.githubusercontent.com/15958325/99021917-0e9e0280-25a5-11eb-9491-b8103bcc49f4.png)  

**Ansible**은 여러 개의 서버를 효율적으로 관리하기 위해 고안된 환경 구성 자동화 오픈소스 도구입니다.

여러 서버를 구성할 때 사용하는 가장 기본적인 방식은 shell script를 만들어서 돌리는 방식입니다. 하지만 서버의 대수가 많아지고 동시에 환경을 구성해야하는 일이 발생한다면 기존의 shell script로는 한계가 있을겁니다.  

이를 위해 고안된 개념이 **Infrastructure as a Code**이며 환경의 배포와 구성을 규격화된 코드로 정의해 사용하는 것을 의미합니다.  

Ansible은 이러한 개념을 바탕으로 생성된 툴입니다. Python으로 개발되었고 Yaml언어를 통해 정의할 수 있습니다.  

## Architecture & Component
![2019_Email_Hero_Design_OS2 4](https://user-images.githubusercontent.com/15958325/99036234-9fd0a180-25c4-11eb-81cc-d1ef596aee3f.png)  

### Control & Managed Node
Ansible의 구조는 크게 **Control Node**와 **Managed Node**로 나뉩니다.  
여타 도구들과 다르게 에이전트 없이 SSH데몬으로 통신만 가능하다면 Ansible로 관리할 수 있습니다.  

다만 Python베이스로 ansible이 동작하기 때문에, Control과 Managed 노드 모두 Python이 설치되어 있어야 합니다.  
->[권장사양](https://docs.ansible.com/ansible/latest/dev_guide/developing_python_3.html#minimum-version-of-python-3-x-and-python-2-x)    
(2020.11.13 기준)  

|Node|python3|python2|
--|----|----------
|control|>=3.5|>=2.7|
|Managed|>=3.5|>=2.6|  


> Python2를 사용할 경우 Ansible을 동작시킬때마다 Warning이 뜨게 됩니다.  
> **해당 Warning을 지우는 방법** : [[Ansible] host x.x.x.x should use /usr/bin/python3](https://gruuuuu.github.io/error/ansible-py-err/)  

### Module
Ansible에서 미리 정의해둔 실행 단위입니다.  
다양한 역할의 모듈들이 존재하고 단일 모듈을 호출해서 사용할 수도 있으며 Playbook에서 여러 다른 모듈을 조합하여 사용할 수도 있습니다.  
-> Ansible에서 사용하는 모듈 목록 : [Collection Index](https://docs.ansible.com/ansible/latest/collections/index.html#list-of-collections)  


### Tasks
Ansible의 작업 단위입니다.  
각 Tasks는 모듈의 집합이라고 보시면 됩니다.  

### Playbook
Tasks들을 실행 순서대로 저장해놓은 작업들의 리스트입니다.  
YAML형태로 작성됩니다.  

### Inventory
관리되는 노드들의 목록이 담긴 파일입니다.  
Ansible은 Inventory파일을 참고해서 Playbook을 실행합니다.  

# Installation

1Control Node와 1Managed Node로 구성하였습니다.  

**Control Node**  
OS : Ubuntu 16.04 

**Managed Node**  
OS : Ubuntu 16.04


## 1. 필요한 패키지 설치
~~~sh
$ apt-get update
$ apt-get install apt-transport-https wget gnupg
~~~

### 1-1 apt-get으로 Ansible 설치
~~~sh
# repo추가
$ apt-add-repository ppa:ansible/ansible
$ apt-get update

$ apt-get install ansible
~~~ 

> 이 방식으로 설치하게 되면 호스트의 **기본 Python을 기반으로 Ansible이 설치**가 됨  
> Ubuntu같은 경우 초기 설치 구성 시, 기본 Python버전이 2.7인가 그렇다. 그래서 별도의 Python 버전 설정 없이 Ansible을 설치하게 되면 내부적으로 Python2를 사용하게 됨  
> 
> 아래 1-2의 pip3으로 설치를 하던지, 호스트의 기본 python버전을 3으로 올려주어야 한다.  

### 1-2 pip으로 Ansible 설치
*전제 : python3이 설치되어 있어야 함.   
~~~sh
$ apt-get install python3-pip
$ pip3 install ansible
~~~

ansible 설치 확인:  
~~~sh
$ ansible --version
ansible 2.10.2
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python3.6/dist-packages/ansible
  executable location = /usr/local/bin/ansible
  python version = 3.6.9 (default, Oct  8 2020, 12:12:24) [GCC 8.4.0]
~~~

## 2. 유저 생성
Control Node에서 Ansible 커맨드를 실행하는 유저가 동일하게 Managed Node에도 존재해야합니다.  

때문에 root로 실행할지, 특정 유저로 실행할지 선택하셔야 합니다.   

1) Managed Node의 초기 구성을 하는 대부분의 경우 -> root
2) 초기 구성 이후 운영하다 별도의 구성을 하려는 경우 -> (root가아닌)user

기본적으로 root권한으로 모든 걸 수행하는것은 바람직하지 않습니다.  

1번의 경우 root는 대부분의 초기 os구성때 생성되므로 따로 Control과 Managed Node에 유저설정을 해주지 않으셔도 됩니다.  

2번의 경우, Control Node의 유저이름이 Managed Node에도 동일하게 존재해야하므로 Control과 Managed Node에 유저생성을 해주고 몇 가지 설정을 해주셔야 합니다.  

### 2.1 user생성

해당 실습에서는 root가 아닌 사용자(이름:`ansible`)로 ansible을 테스트하도록 하겠습니다.  

Control Node와 Managed Node모두 동일한 유저 생성(ex. ansible)  
~~~sh
$ adduser ansible

Adding user `ansible' ...
Adding new group `ansible' (1001) ...
Adding new user `ansible' (1001) with group `ansible' ...
Creating home directory `/home/ansible' ...
Copying files from `/etc/skel' ...
Enter new UNIX password:
Retype new UNIX password:
passwd: password updated successfully
Changing the user information for ansible
Enter the new value, or press ENTER for the default
        Full Name []:
        Room Number []:
        Work Phone []:
        Home Phone []:
        Other []:
Is the information correct? [Y/n] y
~~~

### 2.2 sudo권한 부여
Managed Node에서 sudo권한이 필요한 작업이 있는 경우, 생성한 유저에 sudo권한을 부여해주어야 합니다.  

~~~sh
$ vim /etc/sudoers

ansible ALL=(ALL) NOPASSWD:ALL
~~~

## 3. Key 교환
Control Node에서 키를 생성한 후 Managed Node에 각 키를 복사하겠습니다.  

명령을 실행할 때의 주체는 후에 ansible명령을 내릴 사용자로 설정해주시면 됩니다.  
~~~sh
$ whoami
ansible
~~~

키 생성 후 각 노드에 복사:  
~~~sh
$ ssh-keygen
$ ssh-copy-id x.x.x.x
~~~

## 4. Hosts 파일 편집
위에서는 inventory파일이 Managed Node들의 리스트를 정리해둔 파일이라고 했지만 `/etc/ansible/hosts`파일을 편집함으로써 전역변수처럼 사용할 수도 있습니다.  

호스트파일 편집:  
~~~sh
$ vim /etc/ansible/hosts

[all]
x.x.x.x

[all:vars]
ansible_python_interpreter=/usr/bin/python3
~~~

## 5. Test!
먼저 Ansible의 Hello World급인 ping테스트부터 해보겠습니다.  
### 5.1 Ping Test
~~~sh
$ ansible -m ping all

169.59.4.60 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
~~~

`-m` : 모듈이름  
`all` : 위의 hosts파일에서 설정한 리스트의 이름  

### 5.2 Raw command Test
모듈말고 리눅스 명령어를 실행하고 싶을 때에는 raw를 사용합니다.  

~~~sh
$ ansible -m raw -a 'uptime' all

169.59.4.60 | CHANGED | rc=0 >>
 07:04:13 up 85 days, 22:42,  2 users,  load average: 0.00, 0.00, 0.00
Shared connection to 169.59.4.60 closed.
~~~

## 6. Playbook 만들어보기

이번엔 Playbook을 만들어서 수행하게 해보겠습니다.  

inventory생성:  
~~~sh
$ vim hosts.inv

[test]
169.59.4.60

[test:vars]
ansible_python_interpreter=/usr/bin/python3
~~~

playbook 작성:  
~~~sh
$ vim playbook-test.yaml

---
- hosts: test
  become: yes
  tasks:
  - name: Install packages
    apt:
      name:
      - ntpdate
      state: latest
      cache_valid_time: 3600
~~~
`hosts` : playbook이 적용될 Node리스트의 이름  
`become` : 아래의 task를 sudo권한으로 실행할거면 "yes"  
`name` : task의 이름 (해당 task가 무슨 역할을 하는지 적는다)  
`apt` : 이 자리는 task에서 실행할 모듈의 이름이 와야한다. 해당 예시에서는 `ntpdate`라는 패키지를 설치하기 위한 모듈인 `apt`가 적혀있다.  

playbook 실행:  
~~~sh
$ ansible-playbook playbook-test.yaml -i hosts.inv
~~~
![image](https://user-images.githubusercontent.com/15958325/99063092-55ace780-25e7-11eb-9837-967039949e65.png)  

----
