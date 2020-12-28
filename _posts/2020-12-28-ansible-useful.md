---
title: "[Ansible] 유용한 기능들 - When, Debug, Tag"
categories: 
  - Ansible
tags:
  - DevOps
  - Ansible
last_modified_at: 2020-12-28T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---
## Overview
이번 포스팅에서는 Ansible의 알고있으면 유용한 기능들을 다뤄보겠습니다.  


# 1. 조건에 따라 특정 Task를 실행하고 싶을 때 : When
Ansible은 그 구조의 특성상 하나의 task내에서 조건별로 분기를 할 수가 없습니다.  
대신 task를 여러개로 쪼개서 조건에따라 실행시키게 할 수는 있죠.   
이럴 때 사용하는 구문이 `When`입니다.  

참고: [Ansible doc/Conditionals](https://docs.ansible.com/ansible/latest/user_guide/playbooks_conditionals.html)   


### 1 ansible_facts 사용
`ansible_facts`는 Ansible에서 각 노드에 맞게 동적으로 할당되는 변수들입니다. 노드들의 시스템정보등이 들어가 있습니다.  

아래 구문을 playbook에 넣어서 실행시켜보면
~~~sh
- name: Show facts available on the system
  ansible.builtin.debug:
    var: ansible_facts
~~~
다음과 같은 결과를 얻을 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/103191810-b1be9780-4919-11eb-8af4-b62017f1d7f6.png)  

시스템의 정보에 따라 실행되는 task를 구현하고 싶을 때 사용하면 좋습니다.  
(ex. x86서버에서만 실행되게 하는 task, 특정 ip대역에서만 실행되게 하는 task 등)  

사용할때는 `ansible_facts`를 명시한 뒤 사용할 변수명을 기입합니다.  
~~~sh
tasks:
  - name: Shut down Debian flavored systems
    ansible.builtin.command: /sbin/shutdown -t now
    when: ansible_facts['os_family'] == "Debian"
~~~
이렇게하면 데비안계열 os만 shut down되는 task가 완성이 됩니다.  

> **[Tip] string to int**  
> 형변환을 하려면 bar("|")를 기준으로 {변환하고자 하는 변수}|{자료형} 명시해주시면 됩니다.  
>~~~
>tasks:
>  - ansible.builtin.shell: echo "only on Red Hat 6, derivatives, and later"
>    when: ansible_facts['os_family'] == "RedHat" and ansible_facts['lsb']['major_release'] | int >= 6
>~~~

### 2. register 변수 사용
시스템 변수는 `ansible_facts`로 하면 된다지만 커스텀 변수로 컨트롤해야하는 경우도 있습니다.  
그럴때에는 `register`구문과 `when`구문을 같이 사용하면 됩니다.  


`register`구문은 해당 task에서 출력되는 결과를 임시로 저장해두는 구문입니다.  
~~~
      - name: List contents of directory
        command: ls /
        register: contents
~~~
위와 같이 작성하면 `ls /`의 결과가 `contents`변수에 json형식으로 담기게 됩니다.  

![image](https://user-images.githubusercontent.com/15958325/103193895-23e6aa80-4921-11eb-8a7f-760eac8b1fe6.png)  
출력결과는 `stdout`과 `stdout_lines`에 있고 각 항목을 배열형식으로 다루려면 `stdout_lines`를 사용합니다.  

`/`폴더가 비어있을때 "Directory is empty"라는 메세지를 출력하게 하려면   
다음과 같이 task를 작성하시면 됩니다.  
~~~
      - name: Check contents for emptiness
        debug:
          msg: "Directory is empty"
        when: contents.stdout == ""
~~~
contents변수의 stdout이 비어있다면(when) debug구문을 실행시키는 task입니다.  



# 2. 제대로 실행되었는지 알고싶을 때 : Debug
ansible스크립트를 돌렸을 때, 잘실행되었으면 `ok`, 실패했으면 `failed`, 뭔가 변화가 생겼으면 `changed`...  
이런 몇가지 상태들로 스크립트가 정상적으로 실행되었는지 여부를 알 수가 있습니다.  

물론 실패했을 때에도 에러메세지가 출력되어서 디버그할수도 있죠.  
하지만 더 자세한 실행과정들을 알고싶을수도 있습니다.  
이럴때 사용하는 모듈이 `debug`입니다.  

`debug`의 역할은 간단합니다. `debug`모듈에 표기된 메세지나 변수를 콘솔에 출력하는 역할을 합니다.  

이를 사용하여 변수들을 msg형태로 출력시킬수도 있으며,  
~~~
- debug:
    msg: System {{ inventory_hostname }} has uuid {{ ansible_product_uuid }}
~~~

앞전 task에서 출력된 결과를 `register`에 저장하여 `debug`구문에서 출력하게 할수도 있습니다.  

아래 playbook은 /etc/security/passwd파일의 속성을 변화시키는 task입니다.  
~~~
  - name: chown&chmod root 400 /etc/security/passwd
    file:
      path: "/etc/security/passwd"
      owner: "root"
      mode: 0400
    register: command_output

  - debug:
      var: command_output
~~~
file모듈에서 실행된 task의 결과는 `register`의 `command_output` 변수에 저장되어 debug에서 출력됩니다.   
![image](https://user-images.githubusercontent.com/15958325/103194941-868d7580-4924-11eb-9e20-83d974f2103d.png)   



# 3. 특정 task만 실행하려면 : Tag
하나의 playbook파일에는 수많은 task가 포함되어있습니다.   
playbook을 짜면서 테스트를 해봐야할텐데 테스트할때마다 수많은 task를 계속 실행하기란 굉장히 번거로울겁니다.  

이럴때 사용하는 모듈이 tag입니다.  

~~~
# 4. /etc/shadow 파일 소유자 및 권한 설정
  - name: chown&chmod root 400 /etc/security/passwd
    file:
      path: "/etc/security/passwd"
      owner: "root"
      mode: 0400
    register: command_output
    tags: chmod_secpasswd
  - debug:
      var: command_output
    when: "{{var_isDebug}}"
    tags: chmod_secpasswd

# 5. /etc/hosts 파일 소유자 및 권한 설정
  - name: chown&chmod root 600 /etc/hosts
    file:
      path: "/etc/hosts"
      owner: "root"
      mode: 0600
    register: command_output
    tags: chmod_hosts
  - debug:
      var: command_output
    when: "{{var_isDebug}}"
    tags: chmod_hosts
~~~

이렇게 두개의 task가 있다고 했을때 아래task만 실행시키고 싶다면 `--tag`파라미터를 사용하시면 됩니다.  
~~~sh
$ ansible-playbook playbook.yaml -i hosts --tag chmod_hosts
~~~

playbook에 표기된 모든 tag를 확인하고싶다면 `--list-tags`파라미터를 붙이면 됩니다.   
~~~sh
$ ansible-playbook playbook.yaml -i hosts --list-tags
~~~

특정 task만 skip하고싶을땐 `--skip-tags` 파라미터를 붙여 사용하시면 됩니다.  


----