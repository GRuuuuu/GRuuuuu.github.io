---
title: "Linux 서버 통째로 Dockerizing하기"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Docker
  - Linux
last_modified_at: 2020-02-04T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 포스팅에서는 `linux`서버를 통째로 dockerizing하는 방법에 대해서 기술하겠습니다.  

>해당 문서를 참고했습니다.  
>링크 : [Dockerizing a whole physical Linux server](https://juliensalinas.com/en/dockerize-whole-linux-server/)

# Prerequisites
준비물은 다음과 같습니다.  
- (`Docker Hub`에 이미지가 있는) `Linux OS`

해당 포스팅에서는 다음 환경을 사용합니다.  
- os : `Ubuntu 18.04.2 LTS` (Bionic Beaver)
- arch : `ppc64le` (Power9)   

> system architecture가 달라도 과정은 동일합니다.  

# 실습
## 1. Test application 구동(NGINX)
먼저 dockerizing 할 서버를 먼저 꾸며줍니다.  

간단하게 nginx서버를 구동시켜보겠습니다.  

~~~sh
# nginx설치&실행
$ apt-get install nginx
$ systemctl start nginx
~~~

server ip의 80포트로 접근하면 Nginx의 초기 화면이 뜨는 것을 확인할 수 있습니다.  

여기에 추가로 nginx를 커스텀해보겠습니다.  
간단히 글자만 바꾸기 위해 html파일이 있는 root디렉토리를 찾아야 합니다.  

config파일을 열어서 확인 : (os마다 위치가 약간 다름)    
~~~sh
# 페이지 수정(root디렉토리 확인) 
$ vim /etc/nginx/sites-available/default

...
root /var/www/html;
...
~~~
root디렉토리의 위치를 찾았으면 해당 위치의 index.html파일을 열어 글자를 바꿔줍니다.  

~~~sh
$ sudo vim /var/www/html/index.nginx-debian.html
~~~

수정했으면 nginx를 재시작 :  
~~~sh
$ systemctl restart nginx
~~~

다시 서버에 접속해서 바뀐 글자를 확인해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/73708172-fa3cf780-4740-11ea-92fe-f221b19e2e9b.png)    

## 2. Docker 설치
이제 리눅스 서버의 환경 구성을 전부 마쳤습니다.  
dockerizing하기위해 docker를 설치해주겠습니다.  

~~~sh
# 설치
$ sudo apt install docker.io

# 자동부트&실행
$ sudo systemctl enable docker && sudo systemctl start docker

# 버전확인
$ docker --version
Docker version 18.09.7, build 2d0083d
~~~

그 다음 앞으로 dockerize할 이미지를 docker hub에 push하기 위해 docker login을 미리 해줍니다.  
~~~sh
$ docker login
~~~
![image](https://user-images.githubusercontent.com/15958325/73708536-02496700-4742-11ea-8215-6ec277c4a959.png)  

## 3. Dockerizing your server

### 루트폴더로 이동
~~~sh
$ cd /
~~~

### Dockerfile 생성 
~~~sh
$ sudo vim Dockerfile
~~~
~~~sh
# Dockerfile
FROM ubuntu:18.04

# Copy the whole system except what is specified in .dockerignore
COPY / /

# Reinstall nginx because of permissions issues in Docker
# 원문에서는 이 부분의 주석이 해제되어 있었는데, 
# 실제로 주석달고 해보니 별 에러가 안나길래 주석처리했습니다.
#RUN apt remove -y nginx
#RUN apt install -y nginx

# Launch all services
COPY startup.sh /
RUN chmod 777 /startup.sh
CMD ["bash","/startup.sh"]
~~~

### .dockerignore 생성

~~~sh
$ sudo vim .dockerignore
~~~
~~~sh
# .dockerignore

# Remove folders mentioned here:
# https://wiki.archlinux.org/index.php/Rsync#As_a_backup_utility
/dev 
/proc
/sys
/tmp
/run
/mnt
/media
/lost+found

# Remove database's data
/var/lib/postgresql

# Remove useless heavy files like /var/lib/scrapyd/reports.old
**/*.old
**/*.log
**/*.bak

# Remove docker
/var/lib/lxcfs
/var/lib/docker
/etc/docker
/root/.docker
/etc/init/docker.conf

# Remove the current program
/.dockerignore
/Dockerfile
~~~

### startup.sh스크립트 작성
~~~sh
$ vim startup.sh
~~~

이 단계에서 포트설정, 서비스설정 등을 해줍니다.  
이번 예제에서는 단순히 `nginx`의 서비스만 start시켜주면 됩니다.  
~~~sh
# startup.sh

# Start Nginx
service nginx start

# Little hack to keep the container running in foreground
tail -f /dev/null
~~~

### Docker build
모든 파일을 작성했으면 이제 이미지를 빌드할 차례입니다.  

서버 전체를 copy하기 때문에 용량이 크고 시간이 오래걸립니다.  

~~~sh
$ docker build -t kongru/dockerize:base .
~~~

![image](https://user-images.githubusercontent.com/15958325/73717018-f5d20800-475b-11ea-8ebd-3004b05f2132.png)  

빌드가 끝나면 이미지가 다음과 같이 생성됩니다.  
![image](https://user-images.githubusercontent.com/15958325/73717024-f8346200-475b-11ea-8cee-bc3e77a31392.png)  

### Test
nginx 80포트를 포워딩해주고, 이미지를 실행시켜봅시다.  
~~~sh
$ sudo docker run -d -p 8080:80 kongru/dockerize:base
~~~

서버의 ip:port로 접속 ->   
![image](https://user-images.githubusercontent.com/15958325/73717605-a7256d80-475d-11ea-9dba-4b59d5008f81.png)  
이미지를 말기전에 수정했었던 "TEST PAGE!"문장이 그대로 보이는 것을 확인할 수 있습니다.  
리눅스 서버를 **통째로 복사**했다는 것을 알 수 있는 부분입니다.  

### Docker Hub push (optional)
마지막으로 정상적으로 실행되는 이미지를 도커허브에 push합니다.  
~~~sh
$ sudo docker push kongru/dockerize:base
~~~
![image](https://user-images.githubusercontent.com/15958325/73717723-ee136300-475d-11ea-9d9a-12d4e0dfbb39.png)  


----