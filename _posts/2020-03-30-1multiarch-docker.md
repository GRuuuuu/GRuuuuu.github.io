---
title: "Docker Multi Architecture Build"
categories: 
  - Cloud
tags:
  - amd64
  - Docker
  - ppc64le
last_modified_at: 2020-03-30T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Docker Hub에 여러 architecture로 빌드한 이미지를 push하는 방법을 알아보겠습니다.

# Prerequisites
준비물은 다음과 같습니다.
- docker 18이상
- 서로다른 architecture 이미지 두개 준비 (`x86` or `amd64` or `ppc64le` or `s390x` or etc..)

# STEP
> 참고링크 : [docker manifest](https://docs.docker.com/engine/reference/commandline/manifest/)

## 1. Experimental 기능 활성화

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

테스트

~~~sh
$ docker manifest

Usage:  docker manifest COMMAND

The **docker manifest** command has subcommands for managing image manifests and
manifest lists. A manifest list allows you to use one name to refer to the same image
built for multiple architectures.

To see help for a subcommand, use:

    docker manifest CMD --help

For full details on using docker manifest lists, see the registry v2 specification.

Commands:
  annotate    Add additional information to a local image manifest
  create      Create a local manifest list for annotating and pushing to a registry
  inspect     Display an image manifest, or manifest list
  push        Push a manifest list to a repository

Run 'docker manifest COMMAND --help' for more information on a command.
~~~

잘뜬다!   

## 2. Menifest 생성
먼저 menifest에 포함될 이미지가 로컬에 존재해야한다.  
~~~sh
$ docker images |grep kongru

kongru/php-apache                    ppc64le             aa76898b8dbf        35 minutes ago      394MB
kongru/php-apache                    amd64               39e1797ad29c        23 hours ago        355MB
kongru/php-apache                    latest              39e1797ad29c        23 hours ago        355MB
~~~

ppc64le와 amd64로 빌드된 이미지가 있음

이 두 이미지를 menifest리스트에 추가시켜주자  

~~~sh
$ docker manifest create kongru/php-apache kongru/php-apache:ppc64le kongru/php-apache:amd64

Created manifest list docker.io/kongru/php-apache:latest
~~~

첫번째 파라미터가 **push할 이미지의 이름과 태그**가 되고 두번째부터는 **menifest list에 추가될 이미지**들이다.  

정보를 확인해보면 자동으로 architecture도 추가가된다.  
~~~sh
$ docker manifest inspect kongru/php-apache

{
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
   "manifests": [
      {
         "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
         "size": 3449,
         "digest": "sha256:e16b988bece15e675c96dd793f92fadf6fea9c1751b2a7f6d78ced46f80a9e13",
         "platform": {
            "architecture": "amd64",
            "os": "linux"
         }
      },
      {
         "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
         "size": 3449,
         "digest": "sha256:9eaf3b08273faed73d76a6a77c5af76ff7927d68409c0fdd6c56306970cabb33",
         "platform": {
            "architecture": "ppc64le",
            "os": "linux"
         }
      }
   ]
}
~~~

## push image
이제 docker hub에 push해주면 끝이다
~~~sh
$ docker manifest push -p kongru/php-apache

sha256:52a16401c0a4618abb5af65066469edefc9798f6c4f940e3a9ce135db9d8d74f
~~~

그럼 이렇게 뜬다!  
![image](https://user-images.githubusercontent.com/15958325/77871710-e2d14500-727f-11ea-8318-838c238dbd9d.png)  


끝!  

----