---
title: "Content Trust in Docker(2) : DCT with Docker Hub"
categories: 
  - Container
tags:
  - Docker
  - TUF
  - Notary
  - Security
last_modified_at: 2019-10-18T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
네트워크로 연결된 시스템 사이의 데이터 송수신에서 가장 중요하게 여기는 점은 **"신뢰"**입니다.  
이전에 Docker Notary 서비스에 대한 것을 포스팅한 적이 있습니다.  

> [Content Trust in Docker(1) : Docker Notary란?](https://gruuuuu.github.io/container/docker-notary/)  

이번 포스팅은 `Notary`서비스를 기반으로 **Docker Registry**(`Docker Hub` 또는, `Docker Trusted Registry`)에서 제공하는 **Docker Content Trust**입니다.  

기본적인 이론은 **Notary**에서 설명이 되었으니 간단하게 소개한 뒤, 요번엔 실습을 해보도록 하겠습니다.  

> 해당 문서는 [Content trust in Docker](https://docs.docker.com/engine/security/trust/content_trust/)를 기반으로 쓰여졌습니다.


# Content Trust in Docker
## Docker Content Trust(DCT)?
DCT는 이름에서 느껴지듯이 Docker내 **이미지에 대한 신뢰**를 제공하는 기술입니다.  
**remote저장소**(ex. `Docker Hub`)에 데이터를 보낼 때 디지털 서명을 할 수 있는 기능을 제공해 주는데, 이는 이미지 태그를 통해 이미지의 무결성을 검증할 수 있게 해줍니다.   

> 아래 문단부터  
> image를 올리는 사람 : `publisher`  
> image를 다운로드 받는사람 : `consumer`  
> 라고 칭하겠습니다.

다시말하면, DCT를 통해 `consumer`는 해당 이미지가 `publisher`가 sign한 이미지라는 것을 신뢰할 수 있다는 것입니다.  

## Image tags and DCT
Docker에서 이미지는 다음과 같이 표현될 수 있습니다.  
~~~
[REGISTRY_HOST[:REGISTRY_PORT]/]REPOSITORY[:TAG]
~~~
`이름:태그` 의 형식으로요.  

태그는 이미지의 버전이라고 생각하시면 됩니다.  

예를들어 `nginx`를 생각해보면 :   
최신 이미지 같은 경우는 `nginx:latest`   
특정 버전을 지정해주고 싶은 경우는 `nginx:1.16.1`과 같이 원하는 이미지를 선택할 수 있습니다.  

`publisher`는 이미지의 태그 별로 서명할 수 있습니다.   
>**DCT**를 하려면 이미지에 서명하는 것이 필요충족조건이나 굳이 하고싶지 않다면 서명하지 않은 이미지도 레포에 올라갈 수 있긴 합니다.  
>
>이미지에 서명하는 것은 온전히 `publisher`의 책임입니다.

이미지 레포에는 `publisher`가 이미지를 올릴때 서명했던 key set이 존재하는데, 이것을 통해 `consumer`는 해당 이미지가 **Trust**하다고 할 수 있습니다.  

같은 버전이지만 서명한 이미지와 안된이미지는 서로 **별개**의 이미지로 취급합니다.  
예를 들면, 서명한 `nginx:latest`이미지를 hub에 push하고 서명안한 `nginx:latest`이미지를 hub에 push해도 서명된 `nginx:latest`이미지에는 아무런 영향도 끼치지 못합니다.  

또한 `consumer`는 trusted 이미지를 사용하기위해 **DCT옵션**을 활성화 시킬 수 있습니다.  
DCT옵션을 활성화 시키면 trusted 이미지만 `pull`, `run`, `build`할 수 있습니다. 또한 레포지토리상에서도 trusted이미지만 보이게 되고 서명되지 않은 untrusted이미지들은 보이지 않게 됩니다.   
쉽게 **필터 역할**을 한다고 보시면 될 것 같습니다.  


## Docker Content Trust Keys

이미지에 대한 신뢰는 서명으로써 이뤄질 수 있습니다. 당연히 서명하는 **key에 대한 관리**가 중요할 수 밖에 없습니다.  
DCT에서는 **Notary 아키텍처**를 기반으로 하고 있기 때문에 아래 링크로 설명을 대신하겠습니다.  

>[Content Trust in Docker(1) : Docker Notary란?](https://gruuuuu.github.io/container/docker-notary/)



## Signing Images with Docker Content Trust

> **Environment**  
> Arch: `amd64`  
> OS: `Ubuntu 18.04`   
> Docker: `community 18.09.7`  

DCT를 사용하기 위한 command는 `$ docker trust`입니다.  
~~~bash
root@test-cloud:~# docker trust --help

Usage:  docker trust COMMAND

Manage trust on Docker images

Management Commands:
  key         Manage keys for signing Docker images
  signer      Manage entities who can sign Docker images

Commands:
  inspect     Return low-level information about keys and signatures
  revoke      Remove trust for an image
  sign        Sign an image
~~~

### Docker login

먼저 Docker hub를 이용하려면 도커 계정에 로그인을 해줘야 합니다.  

~~~sh
root@test-cloud:~# docker login
Login with your Docker ID to push and pull images from Docker Hub. If you don't have a Docker ID, head over to https://hub.docker.com to create one.
Username: kongru
Password:
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
~~~

### Make Sample Image : NGINX
샘플로 사용할 이미지를 만들어보겠습니다.  

옛날에 테스트용으로 만들어둔 Nginx앱을 클론받은다음에  
~~~sh
root@test-cloud:~# git clone https://github.com/GRuuuuu/helloworld-s390x.git
Cloning into 'helloworld-s390x'...
remote: Enumerating objects: 32, done.
remote: Counting objects: 100% (32/32), done.
remote: Compressing objects: 100% (29/29), done.
remote: Total 32 (delta 5), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (32/32), done.
~~~

이 앱이 메인프레임위에 올라가는거라 아키텍처가 다르기때문에 Dockerfile을 약간 수정해줍시다.  

>근데 어짜피 앱실행은 안할거라 앱돌아가는거 확인안해도되면 수정안하시고 넘어가셔도 됩니다.  

~~~sh
root@test-cloud:~# cd helloworld-s390x/
root@test-cloud:~/helloworld-s390x# vim Dockerfile
~~~
~~~
FROM nginx
RUN rm /etc/nginx/conf.d/*
ADD hello.conf /etc/nginx/conf.d/
ADD index.html /usr/share/nginx/html/
~~~

그다음 빌드! 도커 허브에 넣을 이미지이니 `<Docker Hub 사용자 계정>/<이미지 이름>:<태그>` 형식으로 이름을 지어줍니다.  
~~~sh
root@test-cloud:~/helloworld-s390x# docker build --tag kongru/helloworld-dct:0.0 .
Sending build context to Docker daemon  117.8kB
Step 1/4 : FROM nginx@sha256:77ebc94e0cec30b20f9056bac1066b09fbdc049401b71850922c63fc0cc1762e
sha256:77ebc94e0cec30b20f9056bac1066b09fbdc049401b71850922c63fc0cc1762e: Pulling from library/nginx
8d691f585fa8: Pull complete
047cb16c0ff6: Pull complete
b0bbed1a78ca: Pull complete
Digest: sha256:77ebc94e0cec30b20f9056bac1066b09fbdc049401b71850922c63fc0cc1762e
Status: Downloaded newer image for nginx@sha256:77ebc94e0cec30b20f9056bac1066b09fbdc049401b71850922c63fc0cc1762e
 ---> 5a9061639d0a
Step 2/4 : RUN rm /etc/nginx/conf.d/*
 ---> Running in d0196d708e49
Removing intermediate container d0196d708e49
 ---> bae09e0f7c6c
Step 3/4 : ADD hello.conf /etc/nginx/conf.d/
 ---> 42e5196e57e2
Step 4/4 : ADD index.html /usr/share/nginx/html/
 ---> 064ee287eccc
Successfully built 064ee287eccc
Successfully tagged kongru/helloworld-dct:0.0


REPOSITORY              TAG                    IMAGE ID            CREATED             SIZE
kongru/helloworld-dct   0.0                    064ee287eccc        3 minutes ago       126MB
nginx                   latest                 5a9061639d0a        26 hours ago        126MB
~~~

이미지가 추가된 것까지 확인!  

### Sign & Push Image to Docker Hub
그럼 이제 `trusted docker image`를 Docker Hub에 push해봅시다.  

**DCT를 사용할 것이라는 환경변수를 설정**해주고, 이미지를 push합니다.  
~~~sh
root@test-cloud:~# export DOCKER_CONTENT_TRUST=1

root@test-cloud:~# docker push kongru/helloworld-dct:0.0
The push refers to repository [docker.io/kongru/helloworld-dct]
3d2dfe0a3dc1: Layer already exists
9d940173ec9a: Layer already exists
eb76042fa053: Layer already exists
cf2436e84ea8: Layer already exists
ed4a4820ee08: Layer already exists
b67d19e65ef6: Layer already exists
0.0: digest: sha256:d257671754698c8cf7d6c1de5184974cbd8b465a66767420e5b337c0ced611ea size: 1570
Signing and pushing trust metadata
Enter passphrase for root key with ID c01f036:
Enter passphrase for new repository key with ID e188c4c:
Repeat passphrase for new repository key with ID e188c4c:
Finished initializing "docker.io/kongru/helloworld-dct"
Successfully signed docker.io/kongru/helloworld-dct:0.0
~~~

> 처음 DCT를 사용하게되면 root key를 생성하게 합니다. 
>~~~
>Initializing signed repository for kongru/dct-test1910...
>You are about to create a new root signing key passphrase. This passphrase
>will be used to protect the most sensitive key in your signing system. Please
>choose a long, complex passphrase and be careful to keep the password and the
>key file itself secure and backed up. It is highly recommended that you use a
>password manager to generate the passphrase and keep it safe. There will be no
>way to recover this key. You can find the key in your config directory.
>Enter passphrase for new root key with ID c01f036:
>Repeat passphrase for new root key with ID c01f036:
>~~~
>이후로는 생성했던 root key의 비밀번호(passphrase)를 넣어주시면 됩니다.  

생성했던 `root key`의 passphrase와 생성하려고하는 `repository key` passphrase를 설정해주면 성공적으로 repository가 초기화되고, 서명한 이미지를 push하게됩니다.  

### Inspect Trusted Image
이미지의 상세 내용은 다음 명령어를 통해 확인할 수 있습니다.  

~~~sh
root@test-cloud:~/helloworld-s390x# docker trust inspect --pretty docker.io/kongru/helloworld-dct:0.0

Signatures for docker.io/kongru/helloworld-dct:0.0

SIGNED TAG          DIGEST                                                             SIGNERS
0.0                 d257671754698c8cf7d6c1de5184974cbd8b465a66767420e5b337c0ced611ea   (Repo Admin)

Administrative keys for docker.io/kongru/helloworld-dct:0.0

  Repository Key:       e188c4c4eaae260204dde3f904ee6b780f7a6173db5be3b7ad90a37979b041f2
  Root Key:     66990f2fa8a0b399c30a27b5a3b00b3d3f091a38b764406f9bd54a12802e0c39
~~~

이미지의 서명자가 해당 **repository의 관리자**라고 나오는 것을 확인할 수 있습니다.  


### Delegation Key generate
그럼 이제는 repository의 관리자가 아닌 **권한을 위임받은 누군가**가 trusted 이미지를 push할 수 있도록 해보겠습니다.  

먼저 `delegation key`를 생성합니다.  
~~~sh
root@test-cloud:~# docker trust key generate kongru2
Generating key for kongru2...
Enter passphrase for new kongru2 key with ID 85c1e62:
Repeat passphrase for new kongru2 key with ID 85c1e62:
Successfully generated and loaded private key. Corresponding public key available: /root/kongru2.pub
~~~

위임키의 이름을 넣고, 키에 대한 비밀번호를 충분히 길게 써주면 키가 생성됩니다.  

>비밀번호를 짧게쓰면 다음과 같은 에러가 발생하기 때문에, 충분히 길게 써줍시다.   
>~~~sh
>Enter passphrase for new kongru2 key with ID 457f1e4:
>Passphrase is too short. Please use a password manager to generate and store a good random passphrase.
>~~~
>

**public**키는 위 커맨드라인에 나온것처럼 `/root` 밑에 생성되고, **private** 키는 local의 Docker trust repository에 생성됩니다. (default 경로 : `~/.docker/trust`)

~~~sh
root@test-cloud:~# cat kongru2.pub
-----BEGIN PUBLIC KEY-----
role: kongru2

MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEGX/Mmd9gcO1234Q050NPp7b+vZok
HXUfslrfT0MqpilDdSUQC+fL2DcNZRLjUBa3kdJ4321Bp+/jywrkfq1l1Q==
-----END PUBLIC KEY-----


root@test-cloud:~# cat ~/.docker/trust/private/85c1e62f0b9e8d0f6cf68bb6738f7ffde660cf8e7f6ea014fafa066febf4d0cf.key
-----BEGIN ENCRYPTED PRIVATE KEY-----
role: kongru2

MIHuMEkGCSqGSIb3DQEFDTA8MBsGCSqGSIb3DQEFDDAOBAjn9D39LU9bOwICCAAw
HQYJYIZIAWUDBAEqBBCffrYU1234Pegteg22QN4iBIGgHRKA5wtOy47+lA1ewfTM
4tVssBEZC4o+kAVfj65MfZ7V3Fz6nD5fU7CVvpr1LCAHNWWulw8HNNkaHJ0s2Q3d
I0B+ldX5/Fyq03G/sVLmVf4G2WU1234aG5xpNcHfWFn2RFUc9XyYoYMB/u3N1lHQ
GnwFrSQ+QcKy2D60JMvHfvUzPDJajJCew1CNLm1234UPTfS5b8TII9KkUZVTTfBC
hA==
-----END ENCRYPTED PRIVATE KEY-----
~~~
### Add delegation key
위에서 만들었던 `delegation key`를 위에서 만들었던 저장소에 추가시켜줍니다.  
~~~sh
root@test-cloud:~# docker trust signer add --key kongru2.pub kongru2 docker.io/kongru/helloworld-dct
Adding signer "kongru2" to docker.io/kongru/helloworld-dct...
Enter passphrase for repository key with ID e188c4c:
Successfully added signer: kongru2 to docker.io/kongru/helloworld-dct
~~~
`repository key` passpharase를 입력하면 delegation key 추가 완료  

### Signing with delegation key
이제 `delegation key`에도 저장소에 접근할 **권리**가 생겼습니다.  

delegation key로 sign한 이미지를 저장소에 올려보겠습니다.  

>위에서 repo admin이 만든것과 구분하기 위해 태그를 0.1로 새로 만들었습니다.  
>~~~sh
>root@test-cloud:~/helloworld-s390x# docker images
>REPOSITORY              TAG                    IMAGE ID            CREATED             SIZE
>kongru/helloworld-dct   0.0                    064ee287eccc        About an hour ago   126MB
>kongru/helloworld-dct   0.1                    064ee287eccc        About an hour ago   126MB
>~~~

~~~sh
root@test-cloud:~/helloworld-s390x# docker trust sign docker.io/kongru/helloworld-dct:0.1
Signing and pushing trust data for local image docker.io/kongru/helloworld-dct:0.1, may overwrite remote trust data
The push refers to repository [docker.io/kongru/helloworld-dct]
3d2dfe0a3dc1: Layer already exists
9d940173ec9a: Layer already exists
eb76042fa053: Layer already exists
cf2436e84ea8: Layer already exists
ed4a4820ee08: Layer already exists
b67d19e65ef6: Layer already exists
0.1: digest: sha256:d257671754698c8cf7d6c1de5184974cbd8b465a66767420e5b337c0ced611ea size: 1570
Signing and pushing trust metadata
Enter passphrase for kongru2 key with ID 85c1e62:
Successfully signed docker.io/kongru/helloworld-dct:0.1
~~~
delegation key의 passphrase를 입력해주면 **trusted 이미지 업로드 완료**  

이미지의 inspect를 확인해보면 :   
~~~sh
root@test-cloud:~/helloworld-s390x# docker trust inspect --pretty docker.io/kongru/helloworld-dct:0.1

Signatures for docker.io/kongru/helloworld-dct:0.1

SIGNED TAG          DIGEST                                                             SIGNERS
0.1                 d257671754698c8cf7d6c1de5184974cbd8b465a66767420e5b337c0ced611ea   kongru2

List of signers and their keys for docker.io/kongru/helloworld-dct:0.1

SIGNER              KEYS
kongru2             85c1e62f0b9e

Administrative keys for docker.io/kongru/helloworld-dct:0.1

  Repository Key:       e188c4c4eaae260204dde3f904ee6b780f7a6173db5be3b7ad90a37979b041f2
  Root Key:     66990f2fa8a0b399c30a27b5a3b00b3d3f091a38b764406f9bd54a12802e0c39
~~~
delegation key가 sign한 이미지라고 뜨는것을 확인할 수 있습니다.  


### Revoke Trusted Data
Trust Data의 삭제는 **Revoke**명령어로 이뤄질 수 있습니다.  
~~~sh
root@test-cloud:~/helloworld-s390x# docker trust revoke docker.io/kongru/helloworld-dct:0.1
Enter passphrase for kongru2 key with ID 85c1e62:
Successfully deleted signature for docker.io/kongru/helloworld-dct:0.1
~~~
sign했던 signer의 passphrase를 입력하면 완료.  

Trust data가 삭제되고 inspect를 다시 해보면 :  
~~~sh
root@test-cloud:~/helloworld-s390x# docker trust inspect --pretty docker.io/kongru/helloworld-dct:0.1

No signatures for docker.io/kongru/helloworld-dct:0.1


List of signers and their keys for docker.io/kongru/helloworld-dct:0.1

SIGNER              KEYS
kongru2             85c1e62f0b9e

Administrative keys for docker.io/kongru/helloworld-dct:0.1

  Repository Key:       e188c4c4eaae260204dde3f904ee6b780f7a6173db5be3b7ad90a37979b041f2
  Root Key:     66990f2fa8a0b399c30a27b5a3b00b3d3f091a38b764406f9bd54a12802e0c39
~~~

태그정보가 뜨지 않는 것을 확인할 수 있습니다.  
(이미지를 삭제하는 것은 아님. 신임정보만 날리는 것)  

Trust정보가 사라지면 당연히 DCT환경하에서는 pull이 안되겠죠?  
~~~sh
root@test-cloud:~# export DOCKER_CONTENT_TRUST=1
root@test-cloud:~/helloworld-s390x# docker pull kongru/helloworld-dct:0.1
No valid trust data for 0.1
~~~


## 한줄정리

### For Consumer
원본 제작자로부터 모든 컨텐츠를 안전하게 수신받고 확인할 수 있게 됩니다.  

### For Publisher
이미지의 제작자로써, 해당 이미지가 변조되지 않았다는 신뢰를 유저에게 제공할 수 있습니다.  

----


$$ E = mc^2 $$