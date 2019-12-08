---
title: "Upgrade GnuPG 2.2.x on CentOS/RHEL"
categories: 
  - LINUX
tags:
  - GnuPG
  - CentOS
  - RHEL
last_modified_at: 2019-11-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
**CentOS7**에서 gpg기본버전을 `gpg 2.2.x`로 업그레이드 하는 방법 입니다.  


## 2. Prerequisites
`OS : CentOS7`  
`Arch : x86`

## 3. How to Upgrade

### gpg버전확인

~~~sh
$ gpg --version
~~~  
![image](https://user-images.githubusercontent.com/15958325/69400374-cacb4100-0d34-11ea-9c5b-48c57a3245e4.png)  


### Set up Build Environment on Linux

>[Set up Build Environment on Linux](https://github.com/keepassxreboot/keepassxc/wiki/Set-up-Build-Environment-on-Linux) 참고

CentOS/RHEL은 더 최신 repository가 필요하므로 새로 repository를 추가해줍니다.

~~~sh
$ vim /etc/yum.repos.d/gpg.repo

[copr:copr.fedorainfracloud.org:bugzy:keepassxc]
name=Copr repo for keepassxc owned by bugzy
baseurl=https://copr-be.cloud.fedoraproject.org/results/bugzy/keepassxc/epel-7-$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/bugzy/keepassxc/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1

~~~  

>패키지 정보 : [bugzy/keepassxc](https://copr.fedorainfracloud.org/coprs/bugzy/keepassxc/)  


~~~sh
$ sudo yum update
~~~

각종 디펜던시 설치  

~~~sh
$ sudo yum install make autoamke gcc-c++ cmake

$ sudo yum install qt5-qtbase-devel qt5-linguist qt5-qttools qt5-qtsvg-devel libgcrypt-devel libargon2-devel qrencode-devel zlib-devel

$ sudo yum install bzip2
~~~

~~~sh
$ sudo yum update && sudo yum upgrade
~~~

### Upgrade to 2.2.x

~~~sh
$ curl -OL "https://gist.githubusercontent.com/simbo1905/ba3e8af9a45435db6093aea35c6150e8/raw/83561e214e36f6556fd6b1ec0a384cf28cb2debf/install-gnupg22.sh" && sudo -H bash ./install-gnupg22.sh
~~~

참고링크 : [simbo1905/GnuPG-2.2.md](https://gist.github.com/simbo1905/ba3e8af9a45435db6093aea35c6150e8)  

>혹시 스크립트파일이 없어지면 쓸 백업용 링크 : [GunPG-2.2.sh](https://gist.githubusercontent.com/GRuuuuu/628a9d0d3f8ffe8dba1eb97842616a54/raw/c2436297127ca91f3b2a6dae3edd50e6bc1e0e71/gistfile1.sh)  


### 확인
리부팅후, 버전확인  
~~~sh
$ gpg --version
~~~
![image](https://user-images.githubusercontent.com/15958325/69400619-a9b72000-0d35-11ea-9cb8-694bf1151b50.png)  

----
