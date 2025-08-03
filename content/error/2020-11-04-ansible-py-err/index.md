---
title: "[Ansible] host x.x.x.x should use /usr/bin/python3"
slug: ansible-py-err
tags:
  - Ansible
date: 2020-11-04T13:00:00+09:00
---


## Environment
`Arch : amd64`   
`OS : Ubuntu 18.04.4 LTS`  

## Error
Ansible 실행중 다음과 같은 Warning 발생  
~~~sh
[DEPRECATION WARNING]: Distribution Ubuntu 18.04 on host 169.59.4.60 should use /usr/bin/python3, but is using /usr/bin/python for backward compatibility with prior Ansible releases. A future Ansible release
 will default to using the discovered platform python for this host. See https://docs.ansible.com/ansible/2.10/reference_appendices/interpreter_discovery.html for more information. This feature will be
removed in version 2.12. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
~~~

## Solution
타겟 서버에서 python3폴더가 아니라 python폴더를 기본 python경로로 사용하고 있기 때문.  

### 1번째시도(Default Python버전 3으로 변경)
타겟서버에 python3이 설치되어있어야 한다.  

ubuntu18.04에는 기본적으로 python3이 설치되어있지만 python의 default버전은 2.7으로 설정되어있다.  

python의 폴더 경로를 살펴보면 :  
~~~sh
$ python -V
Python 2.7.17

$ which python
/usr/bin/python

$ ls -al /usr/bin/python
lrwxrwxrwx 1 root root 24 Oct 25 13:26 /usr/bin/python -> /usr/bin/python2.7
~~~
위와 같이 default python폴더에서 2.7으로 링크가 걸려있다.  

default python을 3으로 설정하기 위해 `update-alternatives`로 버전관리를 하기로 함  

처음엔 등록된게 없어서 아무것도 안나옴:  
~~~sh
$ sudo update-alternatives --config python
update-alternatives: error: no alternatives for python
~~~
버전 등록:  
~~~
$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
~~~
default버전 변경:  
~~~sh
$ update-alternatives --config python
There are 3 choices for the alternative python (providing /usr/bin/python).

  Selection    Path                Priority   Status
------------------------------------------------------------
* 0            /usr/bin/python3     2         auto mode
  1            /usr/bin/python2.7   1         manual mode
  2            /usr/bin/python3     2         manual mode

Press <enter> to keep the current choice[*], or type selection number: 2
~~~
default python버전을 확인해보면:  
~~~sh
$ ls -al /usr/bin/python
lrwxrwxrwx 1 root root 24 Oct 25 13:26 /usr/bin/python -> /etc/alternatives/python
$ ls -al /etc/alternatives/python
lrwxrwxrwx 1 root root 16 Oct 26 03:52 /etc/alternatives/python -> /usr/bin/python3

$ python -V
Python 3.6.9
~~~
제대로 python3이 뜬다.  

이후 ansible을 다시 실행해봤지만 동일한 에러 발생..!  


### 2번째시도 (`ansible_python_interpreter` 파라미터 설정)

default python버전이 3이어도 동일한 에러가 발생하는 이유는 타겟노드의 python폴더가 python3폴더로 링크된다고해도 첫번째 call하는 폴더경로는 **/user/bin/python**이기때문!  

아예 inventory파일에서 python설정을 변경해주기로 함  

**이 방법은 타겟서버의 default python이 2이든 3이든 상관없이 그냥 python3만 설치되어있으면 가능**  

inventory파일을 생성해서 파라미터변수로 python3폴더의 경로를 지정해줌:  
~~~sh
$ vim hosts.inv

[test]
169.59.4.60

[test:vars]
ansible_python_interpreter=/usr/bin/python3
~~~

그러고나서 ansible실행해보면 warning이 싹 사라진다!  

---

