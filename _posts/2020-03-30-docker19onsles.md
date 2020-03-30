---
title: "Docker 19.03 on SLES (ppc64le)"
categories: 
  - LINUX
tags:
  - LINUX
  - Docker
  - ppc64le
last_modified_at: 2020-03-30T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
ppc64le용 docker 19.03 설치하는 방법  

>+)  
>200330 현재는 yum repo에서 도커다운받으면 18.03이 가장 최신 버전임.  
> `docker buildx` 기능을 사용하려면 19 이상의 버전이 필요함  
> 근데 아무리찾아봐도 도커19버전을 yum으로 설치할수있는 repo를 찾을수없었고  
> rpm 소스파일만 있었기에 그 방법을 기술해둡니다...

# Prerequisites

- SLES 또는 SUSE 15

# STEP
## 1. RPM source 파일 다운로드
링크 :  [docker-19.03.1_ce-lp151.2.12.1 RPM for ppc64le](http://rpmfind.net/linux/RPM/opensuse/ports/updates/15.1/ppc64le/docker-19.03.1_ce-lp151.2.12.1.ppc64le.html)    

<img src="https://user-images.githubusercontent.com/15958325/77867687-4143f680-7273-11ea-820c-10b8da1aede7.png" width="600px">  

다운받아서 컴파일하기위해 한번 풀어준다  
~~~sh
$ rpm -Uvh https://download.opensuse.org/ports/update/leap/15.1/oss/src/docker-19.03.1_ce-lp151.2.12.1.src.rpm
~~~

## 2. 컴파일
위 과정을 거치면 빌드할 rpm이 나온다.  

`.../SPEC` 밑의 rpm을 빌드해주면되는데 os마다 `SPEC`폴더의 위치가 다른것같다.  

`find / -name SPEC`으로 찾아보자!  

~~~sh
$ cd /usr/src/packages/SPEC
~~~

컴파일은 `rpmbuild`로 한다.   
~~~sh
$ rpmbuild --bb docker…..rpm
~~~

무턱대고 `rpmbuild`를 하면 당연히 에러가 발생한다.  
`rpm`은 `yum`이나 `apt-get`과 달리 dependency가 없으면 빌드도 설치도 하지 못한다.  
그래서 수작업으로 모든 의존성파일들을 설치해주어야한다.  

다행히 모든 의존성파일들은 위의 다운로드페이지에서 찾을 수 있다.  
일단 먼저 `rpmbuild`를 한 뒤에 문제를 일으키는 dependency들만 골라서 다운받도록 하자.  

<img src="https://user-images.githubusercontent.com/15958325/77868157-178bcf00-7275-11ea-843d-f03ad8fb8b6b.png" width="600px">  

## 3. Dependency download
다른것들은 그냥 눌러서 os사양에 맞게 rpm으로 설치해주면되지만 주의해야할 점들이 있다.  

### 뒤에 특정 버전이 적혀있는 경우
꼭 해당 버전으로만 다운받아줘야한다.  

- `containerd-git = 894b81a4b802e4eb2a91d1ce216b8817763c29fb`
- `docker-libnetwork-git = fc5a7d91d54cc98f64fc28f9e288b46a0bee756c`
- `docker-runc-git = 425e105d5a03fabd737a126ad93d62a9eeede87f`
요 세개를 주의해서 다운받아준다.  

### go언어는 기본 repo에 없음  

[OpenSUSE download](https://software.opensuse.org/download.html?project=devel%3Alanguages%3Ago&package=go)페이지에서 os버전에 따라 설치를 진행해준다.  

~~~sh
# For SLE 15 run the following as root:
$ zypper addrepo https://download.opensuse.org/repositories/devel:languages:go/SLE_15/devel:languages:go.repo
$ zypper refresh
$ zypper install go
~~~

## 4. 다시 빌드
모든 의존성파일이 설치되었으면 정상적으로 `rpmbuild`가 종료될것이다.  

## 5. docker 설치

그럼 `../RPMS/ppc64le` 폴더로 이동하자  
빌드가 완료된 rpm파일이 있을것  

rpm -Uvh로 rpm설치를 진행해주면 도커설치가 완료된다!  

<img src="https://user-images.githubusercontent.com/15958325/77868466-40609400-7276-11ea-9bf7-8263fc13f3f8.png" width="600px">  



## Appendix. docker buildx
해당 커맨드는 도커 19에서도 실험적인 기능이라 사용하려면 추가로 설정을 더 해줘야한다.  

docker의 `config.json`파일에 `experimental`을 `enabled`로 설정해주면 된다.
~~~sh
vim .docker/config.json
{
        "experimental": "enabled",
        "auths": {
                "https://index.docker.io/v1/": {
                        "auth": "dddddddddddddddddddddddddd=="
                }
        },
        "HttpHeaders": {
                "User-Agent": "Docker-Client/19.03.5 (linux)"
        }
}
~~~



----