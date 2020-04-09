---
title: "Nginx File listing"
categories: 
  - LINUX
tags:
  - LINUX
  - HTTP
  - NGINX
last_modified_at: 2020-04-09T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---
## Overview
간단하게 nginx로 파일 호스팅하는 방법을 알아보겠습니다.

# Prerequisites
- 호스팅할 리눅스서버
- (해당 포스팅에서는 CentOS 7을 사용)

# Step
## 1. Nginx 설치
CentOS에서는 기본적으로 Nginx repo를 지원하고 있지 않기 때문에 repo추가를 해줍니다.  

~~~sh
$ vi /etc/yum.repos.d/nginx.repo

[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1
~~~

그 다음 설치 진행 & 서비스 시작
~~~sh
$ yum install -y nginx

$ systemctl start nginx
$ systemctl enable nginx
~~~

## 2. Nginx config

config파일의 위치는 운영체제마다 약간씩 다르지만 CentOS는 `/etc/nginx` 밑에 있습니다.

저는 편의를 위해 루트디렉토리에 바로 파일리스팅을 적용했지만 `location /files` 와 같이 적용시킬 수 있습니다.  

- `root` : file listing할 디렉토리. 주의할점은 nginx의 루트디렉토리 밑이어야 한다.  
- `autoindex` : file listing을 해주는 옵션

~~~sh
$ vim /etc/nginx/conf.d/default.conf

server {
    listen       80;
    server_name  localhost;

    #charset koi8-r;
    #access_log  /var/log/nginx/host.access.log  main;

    location / {
        root   /usr/share/nginx/html/files;
        autoindex on;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
~~~

설정을 저장하고 서비스 재시작을 해줍니다. 
~~~sh
$ systemctl restart nginx
~~~

## 3. HTTP
웹으로 가서 ip를 입력하면 다음과 같이 root에서 설정해줬던 `/usr/share/nginx/html/files`폴더의 파일들이 리스팅되어서 보이는 것을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/78849457-80323300-7a4f-11ea-8819-fe6e6e917f0d.png)  

끝!

----
