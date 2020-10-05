---
title: "Openshift4.x Baremetal 설치 - Restricted Network"
categories: 
  - OCP
tags:
  - Kubernetes
  - RHCOS
  - VMware
  - Openshift
last_modified_at: 2020-10-04T13:00:00+09:00
toc : true
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
약 5개월 전에는 베어메탈에 UPI방식으로 openshift 4.3을 설치해보는 문서를 포스팅했었습니다.  

> -> [Openshift4.3 Installation on Baremetal](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/#)

이번엔 Restricted Network, 즉 Offline에서 openshift 4.3을 설치해보는 것을 기술하겠습니다.  

기본적으로 설치과정은 동일하지만, 설치를 시작하기 이전에 준비해야할 몇가지 사항들을 주로 살펴보겠습니다.  

참고 : openshift document - [Installing a cluster on bare metal in a restricted network](https://docs.openshift.com/container-platform/4.3/installing/installing_bare_metal/installing-restricted-networks-bare-metal.html)  

## Prerequisites

제가 이번에 사용한 노드들의 스펙입니다.

Machine|os|vCPU|RAM|Storage|number  
-------|----------|----------|--------|---------|---------
Infra1|CentOS7|4|8GB|500GB|1개
Infra2|CentOS7|4|8GB|200GB|1개
Bootstrap|RHCOS|4|16GB|120GB|1개
Control plane|RHCOS|4|16GB|120GB|1개
Compute|RHCOS|2|8GB|120GB|1개  

사용한 노드들의 아키텍처는 다음과 같습니다.  
![2](https://user-images.githubusercontent.com/15958325/95017685-c8947b80-0695-11eb-86d3-a5daa04c577b.PNG)  

예전에 설치했던 [Openshift4.3 Installation on Baremetal](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/#)과 달리 사용하는 Infra 노드가 두개입니다.  

기존엔 Bastion+http+dns+lb를 한 노드에서 사용했다면, 이번에는 두 노드로 나눠서 구성을 해봤습니다.  

또 하나 추가된 점은 **Mirror Registry**입니다. 기존의 설치방식(Online)에서는 각 노드가 인터넷과 연결되어있기 때문에 Quay에서 바로 이미지를 pulling할 수 있지만,  
이번엔 Offline에서 설치를 진행할 것이기 때문에 각 클러스터 구성에 필요한 이미지 정보들을 미리 Mirror하여 로컬 레지스트리로 구성해주어야합니다.  

>+) 추가로 요번 실습에서는 퍼블릭 도메인을 사용할겁니다.  
>**사용할 도메인** -> `hololy-dev.com`  
>**사용할 클러스터이름** -> `gru`  
>미리 와일드카드 레코드를 DNS에 추가시켜주고 Target을 제가 사용할 로컬DNS노드로 향하게 해주시면 됩니다.  
>![image](https://user-images.githubusercontent.com/15958325/95009660-c82cbe00-065e-11eb-8376-0f5cd1b23ab7.png)     


## Infra2 - DNS, LoadBalancer 구성
도메인 기반으로 로컬이미지레지스트리를 구성할것이기 때문에 로컬 DNS부터 구성해주도록 하겠습니다.  
### DNS
#### 1. dns의 ip가 resolv.conf에 기입되어있는지 확인  
~~~sh
$ vim /etc/resolv.conf

nameserver {dns ip}
nameserver 8.8.8.8
~~~

#### 2. named서버를 위한 패키지 설치  
~~~
$ yum install -y bind bind-utils
~~~

#### 3. zone 추가 (/etc/named.rfc1912.zones)
~~~sh
zone "hololy-dev.com" IN {
        type master;
        file "hololy-dev.com.zone";
        allow-update { none; };
};

zone "216.95.10.in-addr.arpa" IN {
        type master;
        file "reverse.hololy-dev.com";
        allow-update { none; };
};
~~~
클러스터는 내부 ip망을 통해서 통신을 할것이기 때문에 private ip로 적어줘야 합니다.  

#### 4. 정방향 DNS설정 (/var/named/hololy-dev.com.zone)  
~~~sh
$TTL 1D
@   IN SOA  @ hololy-dev.com. (
                    20200917   ; serial
                    1D  ; refresh
                    1H  ; retry
                    1W  ; expire
                    3H )    ; minimum
    IN NS   hololy-dev.com.
    IN A    10.95.216.12
ns  IN A    10.95.216.12
www IN A    10.95.216.12

;cluster name
gru   IN CNAME    @

api-int.gru   IN A 10.95.216.12
api.gru   IN A 10.95.216.12
*.apps.gru    IN A 10.95.216.12

;ocp cluster
bootstrap.gru   IN  A   10.95.216.15
master.gru      IN  A   10.95.216.13
worker.gru      IN  A   10.95.216.14

;ocp registry (only for restrict network)
registry.gru        IN  A  10.95.216.11

;ocp internal cluster ip
etcd-0.gru      IN A    10.95.216.13

;ocp srv records
_etcd-server-ssl._tcp.gru   86400   IN   SRV    0   10  2380    etcd-0.gru
~~~
registry 레코드 추가하는 것을 잊지 않도록 합니다.  

#### 5. 역방향 DNS설정 (/var/named/reverse.hololy-dev.com)
~~~sh
$TTL 900
@ IN SOA hololy-dev.com. root.hololy-dev.com. (

    20200917;
    86400;
    3600;
    86400;
    3600;

)

    IN NS hololy-dev.com.
    IN A 10.95.216.12

12 IN PTR hololy-dev.com.

15 IN PTR bootstrap.gru.hololy-dev.com.
13 IN PTR master.gru.hololy-dev.com.

14 IN PTR worker.gru.hololy-dev.com.

12 IN PTR api.gru.hololy-dev.com.
12 IN PTR api-int.gru.hololy-dev.com.
~~~
registry는 넣으셔도 되고 안넣으셔도 됩니다.

#### 6. named설정파일 변경(/etc/named.conf)
~~~sh
options {
        listen-on port 53 { any; };
        listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
        dump-file       "/var/named/data/cache_dump.db";
        statistics-file "/var/named/data/named_stats.txt";
        memstatistics-file "/var/named/data/named_mem_stats.txt";
        recursing-file  "/var/named/data/named.recursing";
        secroots-file   "/var/named/data/named.secroots";
        allow-query     { any; };
~~~

listen-on port 53, allow-query 부분을 `localhost`에서 `any`로 바꿔줍니다

#### 7. 권한 수정
~~~sh
$ chown root.named /var/named/hololy-dev.com.zone
$ chown root.named /var/named/reverse.hololy-dev.com
~~~

#### 8. check
~~~sh
$ named-checkzone hololy-dev.com /var/named/hololy-dev.com.zone
zone hololy.local/IN: loaded serial 200522
OK

$ named-checkzone hololy-dev.com /var/named/reverse.hololy-dev.com
zone hololy.local/IN: loaded serial 200522
OK
~~~

#### 9. named 서비스 재시작  
~~~sh
$ systemctl restart named
~~~

#### 10. `nslookup`으로 확인  
~~~sh
$ nslookup
> hololy-dev.com
Server:         150.238.57.198
Address:        150.238.57.198#53

Name:   hololy-dev.com
Address: 10.95.216.11
> 10.95.216.11
11.216.95.10.in-addr.arpa       name = hololy-dev.com.
11.216.95.10.in-addr.arpa       name = api.gru.hololy-dev.com.
11.216.95.10.in-addr.arpa       name = api-int.gru.hololy-dev.com.
~~~
정방향 역방향 모두 테스트해줍니다.  


### LoadBalancer
#### 1. nginx repo 추가  
~~~sh
$ vim /etc/yum.repos.d/nginx.repo

[nginx] 
name=nginx repo 
baseurl=http://nginx.org/packages/centos/7/$basearch/ 
gpgcheck=0 
enabled=1
~~~

#### 2. nginx 설치  
~~~sh
$ sudo yum install -y nginx
$ systemctl start nginx
$ systemctl enable nginx
~~~

#### 3. lb를 위한 conf파일 생성  
~~~sh
$ mkdir /etc/nginx/tcpconf.d
$ vim /etc/nginx/tcpconf.d/lb.conf
~~~

~~~sh
stream{
    upstream ocp_k8s_api {
        #round-robin;
        server 10.95.216.15:6443; #bootstrap
        server 10.95.216.13:6443; #master1
    }
    server {
        listen 6443;
        proxy_pass ocp_k8s_api;
    }

    upstream ocp_m_config {
        #round-robin;
        server 10.95.216.15:22623; #bootstrap
        server 10.95.216.13:22623; #master1
    }
    server {
        listen 22623;
        proxy_pass ocp_m_config;
    }

    upstream ocp_http {
        #round-robin;
        server 10.95.216.13:80; #master1
        server 10.95.216.14:80; #worker1
    }
    server{
        listen 80;
        proxy_pass ocp_http;
    }

    upstream ocp_https {
        #round-robin;
        server 10.95.216.13:443; #master1
        server 10.95.216.14:443; #worker1
    }
    server{
        listen 443;
        proxy_pass ocp_https;
    }
    
    upstream ocp_registry {
        #round-robin;
        server 10.95.216.11:5000; #registry
    }
    server{
        listen 5000;
        proxy_pass ocp_registry;
    }
}
~~~
registry는 LISTEN port가 5000번이므로 참고해서 적어줍니다.  
ip는 레지스트리를 생성할 노드의 ip를 적어주시면 됩니다.  


#### 4. 기존 nginx conf파일에 tcp/udp용 로드밸런서 include  
~~~sh
$ vim /etc/nginx/nginx.conf
~~~

~~~
…
http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
    charset utf-8;
}
include /etc/nginx/tcpconf.d/*.conf;
~~~
http블럭 밖에다가 명시해주시면 됩니다.(가장 아래줄)  

#### 5. SELINUX permissive모드로 변경  
권장하는 방법은 아니지만 Nginx서비스에 필요한 포트를 semanage로 열어줘도 Permission denied 에러가 나서 실습을 진행하기 위해 permissive모드로 진행하도록 하겠습니다.  
추후 방법을 알아내면 수정하겠습니다.  
~~~sh
$ setenforce 0
~~~

#### 6. 서비스 재시작 및 확인  
~~~sh
$ systemctl restart nginx
$ systemctl status nginx
~~~

## Infra1 - Installer, MirrorRegistry, HTTP 구성

### Installer
RedHat계정이 있어야 합니다.  
#### 1. Installer Download
다음 링크로 이동 -> [https://cloud.redhat.com/openshift/install
](https://cloud.redhat.com/openshift/install)  

![image](https://user-images.githubusercontent.com/15958325/95031285-2d7cbf80-06f0-11eb-978a-51f02198fc00.png)  

UPI선택 후, Download Installer선택  
![image](https://user-images.githubusercontent.com/15958325/95031323-53a25f80-06f0-11eb-9cf8-5cafe17c2173.png)  

해당 페이지에서는 무조건 `latest`버전의 openshift installer 및 client를 받을 수 있습니다.  
원하는 버전으로 받으려면 다음 링크를 참고하세요.  
[https://mirror.openshift.com/pub/openshift-v4/clients/ocp/](https://mirror.openshift.com/pub/openshift-v4/clients/ocp/)  

이 실습에서는 4.3.8버전으로 사용할 것입니다.
![image](https://user-images.githubusercontent.com/15958325/95031417-db886980-06f0-11eb-89a8-bd8caae90da4.png)  
`openshift-client-linux`와 `openshift-install-linux`를 다운받아 줍니다.  
4.3.8태그가 붙은거나 안붙은거나 같은것이므로 둘 중 하나만 받으면 됩니다.  

### 2. 압축해제
installer 압축해제 :   
~~~sh
$ tar -xvf openshift-install-linux-4.3.8.tar.gz

$ ./openshift-install version
openshift-install 4.3.8
built from commit 7bc8168fbba1c831ac1b25c858f4f56cd7468801
release image quay.io/openshift-release-dev/ocp-release@sha256:919e2405322cf497165d58fbd064ddddcad1651c367362cfea078e4469803005
~~~

client 압축해제(`kubectl`, `oc`)  
~~~sh
$ tar -xvf openshift-client-linux-4.3.8.tar.gz
$ cp ./kubectl /usr/local/bin/kubectl
$ cp ./oc /usr/local/bin/oc
~~~
버전확인  
~~~sh
$ oc version
Client Version: 4.3.8

$ kubectl version
Client Version: version.Info{Major:"", Minor:"", GitVersion:"v0.0.0-master+$Format:%h$", GitCommit:"$Format:%H$", GitTreeState:"", BuildDate:"1970-01-01T00:00:00Z", GoVersion:"go1.12.12", Compiler:"gc", Platform:"linux/amd64"}
~~~


### MirrorRegistry
참고 : openshift document - [Creating a mirror registry for installation in a restricted network](https://docs.openshift.com/container-platform/4.3/installing/install_config/installing-restricted-networks-preparations.html)   

Offline으로 설치를 진행하기 때문에 미리 로컬에 이미지 레지스트리를 만들어 설치에 필요한 이미지를 구성해둬야 합니다.  

이미지 레지스트리는 반드시 클러스터의 모든 노드에서 접근가능해야하며, 외부 레지스트리에서 이미지를 pulling해야하기 때문에 인터넷 연결이 되어있어야 합니다.  

#### 1. SSL생성
registry와 ssl인증을 기반으로 통신을 하기 때문에 registry에 등록할 ssl certificate를 생성해주어야 합니다.  

openshift 공식 document에서는 openssl로 사설ssl를 만들어 테스트를 하도록 가이드를 하고 있지만, 이렇게되면 container pull 등에 TLS 인증 해제 설정이 필요하고, 제가 직접 해보니 잘 안됩니다...  

그래서 되도록이면 공인ssl를 발급받아서 사용하는 것을 추천드립니다.  
=> [ZeroSSL에서 무료 인증서 발급받기](https://gruuuuu.github.io/network/openssl/)   

인증서를 발급받으면 zip파일에 3가지 파일이 있을겁니다.  
![image](https://user-images.githubusercontent.com/15958325/95036640-81dd6a80-0703-11eb-9896-33b75e422d25.png)  

`certificate.crt`와 `ca_bundle.crt`를 합쳐줍니다.  
~~~sh
$ cat certificate.crt bundle.crt > domain.crt
~~~
그 다음 `domain.crt`를 열어서 파일 중간을 끊어주도록 합니다.  
~~~
...
-----end----------begin-----
...
를

...
-----end-----
-----begin-----
...
로 줄바꿈
~~~


**(optional)** 네이밍 일관성을 위해 `private.key`도 `domain.key`로 이름을 변경해주겠습니다.  
~~~sh
$ mv private.key domain.key
~~~

#### 2. registry 설정
폴더 생성:  
~~~sh
$ mkdir -p /opt/registry/{auth,certs,data}
~~~

위에서 생성한 crt와 key파일을 certs폴더에 옮겨주겠습니다.  
~~~sh
$ mv domain.crt /opt/registry/certs
$ mv domain.key /opt/registry/certs
~~~

#### 3. podman, httpd-tools 설치
centOS의 경우 epel 레포 추가 필수  
~~~sh
$ yum install -y podman httpd-tools
~~~

#### 4. 레지스트리 사용자 생성
auth 폴더로 이동 :  
~~~sh
$ cd /opt/registry/auth
~~~

사용자 생성
~~~sh
$ htpasswd -bBc /opt/registry/auth/htpasswd admin passw0rd

Adding password for user admin
~~~

>만약 docker가 켜져있다면 충돌위험이 있으니 docker는 stop해주시기 바랍니다.  
>~~~sh
>$ systemctl stop docker
>~~~

#### 5. registry 컨테이너 띄우기

podman으로 registry컨테이너를 띄워주도록 하겠습니다.  
~~~sh
$ podman run --name mirror-registry -p 5000:5000 \
  -v /opt/registry/data:/var/lib/registry:z \
  -v /opt/registry/auth:/auth:z \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -v /opt/registry/certs:/certs:z \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  -e REGISTRY_COMPATIBILITY_SCHEMA1_ENABLED=true \
  -d docker.io/library/registry:2


Trying to pull docker.io/library/registry:2...
Getting image source signatures
Copying blob 47112e65547d done
Copying blob c1cc712bcecd done
Copying blob 46bcb632e506 done
Copying blob cbdbe7a5bc2a done
Copying blob 3db6272dcbfa done
Copying config 2d4f4b5309 done
Writing manifest to image destination
Storing signatures
6daeb31e5bf53d6cfb7082817b93dcb8acaf08d3da950e13b18e1b30f25e1dc5
~~~

#### 6. 접근 테스트
제대로 registry에 접근이 가능한지 테스트해보겠습니다.  

repository 출력:  
~~~sh
$ curl -u admin:passw0rd -k https://registry.gru.hololy-dev.com:5000/v2/_catalog

{"repositories":[]}
~~~

login :  
~~~sh
$ podman login -u admin -p passw0rd registry.gru.hololy-dev.com:5000

Login Succeeded!
~~~

> **발생할 수 있는 에러**  
>~~~sh
>x509: certificate is not valid for any names, but wanted to match registry.gru.hololy-dev.com
>~~~
>사설인증서를 썼을 때 생긴 오류. 공인ssl로 바꾸니 바로 해결   

#### 7. pull secret 설정

아래 링크에서 pull-secret을 확인하실 수 있습니다.  
[https://cloud.redhat.com/openshift/install/pull-secret](https://cloud.redhat.com/openshift/install/pull-secret)   
![image](https://user-images.githubusercontent.com/15958325/95038571-6d03d580-0709-11eb-8bb0-427ae2d376f8.png)   

pull-secret을 복사해서 `pull-secret.json`파일로 생성해줍니다.
~~~sh
$ vim /opt/registry/certs/pull-secret.json
~~~

처음에 pull secret을 붙여넣기하면 json포맷의 글자들이 한줄로 나열되어있는데 이걸 보기좋게 줄 정렬을 하려면 vim의 다음 기능을 사용하시면 좋습니다.  
~~~sh
:%!python -m json.tool 
~~~

정렬을 하게되면 다음과 같이 확인할 수 있습니다.  
~~~json
{
    "auths": {
        "cloud.openshift.com": {
            "auth": "b3Blbn...",
            "email": "ddd@example.com"
        },
        "quay.io": {
            "auth": "b3Blbn...",
            "email": "ddd@example.com"
        },
        "registry.connect.redhat.com": {
            "auth": "NTMwN...",
            "email": "ddd@example.com"
        },
        "registry.redhat.io": {
            "auth": "NTMwN...",
            "email": "ddd@example.com"
        }
    }
}
~~~
계정의 auth정보가 포함되어있습니다.  

위에서 생성한 로컬 레지스트리의 시크릿파일 생성:  
~~~sh
$ echo -n 'admin:passw0rd' | base64 -w0
YWRtaW46cGFzc3cwcmQ=
~~~

그 다음 `pull-secret.json`파일에 붙여넣습니다.
~~~json
{
    "auths": {
        "cloud.openshift.com": {
            "auth": "b3Blbn...",
            "email": "ddd@example.com"
        },
        "quay.io": {
            "auth": "b3Blbn...",
            "email": "ddd@example.com"
        },
        "registry.connect.redhat.com": {
            "auth": "NTMwN...",
            "email": "ddd@example.com"
        },
        "registry.redhat.io": {
            "auth": "NTMwN...",
            "email": "ddd@example.com"
        },
        "registry.gru.hololy-dev.com:5000":{
            "auth": "YWRtaW46cGFzc3cwcmQ=",
            "email": "ddd@example.com"
        }
    }
}
~~~

#### 8. Mirroring
이제 로컬 레지스트리에 Quay에서 필요한 이미지들을 미러링하겠습니다.  

우선 설치를 편하게 하기 위해 다음 환경변수를 설정해줍니다.  

**환경변수 설정 :**
1. `OCP_RELEASE` : 설치할 OCP 버전 지정 예) 4.3.8-x86_64
2. `LOCAL_REGISTRY` : Mirror Registry URL 예) `registry.gru.hololy-dev.com:5000`
3. `LOCAL_REPOSITORY` : Registry Repository Name 
4. `PRODUCT_REPO` : 미러할 repo의 이름. production release인경우 `openshift-release-dev` 명시
5. `LOCAL_SECRET_JSON` : pull secret file path 예) /opt/registry/certs/pull-secret.json
6. `RELEASE_NAME`: 미러할 repo의 release 이름. production release인 경우 `ocp-release` 명시

원하는 release 버전은 아래 quay repo에서 검색해 태그를 확인해야 합니다.  
-> [openshift-release-dev / ocp-release](https://quay.io/repository/openshift-release-dev/ocp-release?tab=tags)  
![image](https://user-images.githubusercontent.com/15958325/95039635-498e5a00-070c-11eb-9285-3e0f7deb9d53.png)  


~~~sh
export OCP_RELEASE="4.3.8-x86_64" 
export LOCAL_REGISTRY='registry.gru.hololy-dev.com:5000' 
export LOCAL_REPOSITORY='ocp4.3.8-x86' 
export PRODUCT_REPO='openshift-release-dev' 
export LOCAL_SECRET_JSON='/opt/registry/certs/pull-secret.json' 
export RELEASE_NAME="ocp-release"
~~~

미러 시작은 다음 명령어를 통해 시작합니다.  
~~~sh
$ oc adm -a ${LOCAL_SECRET_JSON} release mirror \
   --from=quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE} \
   --to=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY} \
   --to-release-image=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE} 
~~~  

![image](https://user-images.githubusercontent.com/15958325/95039766-ad188780-070c-11eb-865e-0d059d3750e7.png)  

설치가 끝나면 `install-config.yaml`파일에 추가할 `imageContentSources`가 출력이 되는데 복사해두도록 합니다.  

repo 확인:  
~~~sh
$ curl -u admin:passw0rd -k https://registry.gru.hololy-dev.com:5000/v2/_catalog

{"repositories":["ocp4.3.8-x86"]}
~~~

MirrorRegistry구성이 완료되었습니다!  

### HTTP File Server
coreOS설치에 필요한 ignition파일이나 coreOS raw이미지파일을 공유할 파일 서버를 만들어야 합니다.  
#### 1. nginx 설치
위의 nginx 설치방법 참고  

#### 2. nginx default.conf 수정

~~~sh
$ vim /etc/nginx/conf.d/default.conf

server {
    listen       8080;
    server_name  localhost;


    location / {
        root   /usr/share/nginx/html/files;
        autoindex on;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

}
~~~

- 80포트 -> 8080포트로 변경
- `location /` 에 파일 서버로 사용할 경로 추가
- `autoindex on` 추가

#### 3. file server 실행

~~~sh
# 파일 서버로 사용할 경로 생성
$ mkdir /usr/share/nginx/html/files

# 테스트용 파일 생성
$ touch /usr/share/nginx/html/files/hi

# nginx서비스 reload
$ systemctl reload nginx
~~~

인터넷 주소창에 ip:8080으로 접근해보면 다음과 비슷한 화면이 떠야합니다.  
![image](https://user-images.githubusercontent.com/15958325/95042774-de498580-0715-11eb-8c97-70b0af07856d.png)  

>**접근이 안되는 경우**  
> -> 방화벽 stop  
>~~~
>$ systemctl stop firewalld
>~~~

## Installation
이제부터 설치를 본격적으로 진행하겠습니다.  
설치는 Infra1(bastion)서버에서 진행합니다.  

#### 1. 설치 폴더 생성
먼저 설치폴더를 만들어줍니다. 
~~~sh
$ mkdir installation_directory
$ cd installation_directory
~~~

#### 2. ssh key생성
클러스터 노드에 추가할 ssh key를 생성해주겠습니다.  
~~~sh
$ $ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:74Hc6wjgA1ErMNoixDCdKmQR821ENJcqwf4QNBKzGxA root@ocp.ibm.cloud
The key's randomart image is:
+---[RSA 2048]----+
|E@*++= ..        |
|+OO=+.o.         |
|*+=.+o.          |
|+.o*..           |
|... =   S        |
|   o o . +       |
|    o . o +      |
|     . . o o     |
|        ..+      |
+----[SHA256]-----+
~~~

#### 3. ssh config 설정
클러스터 노드에 편하게 접근하기 위해 설정해주겠습니다.  
~~~sh
$ vim ~/.ssh/config

Host boot
    HostName {bootstrap_ip}
    User core
    IdentityFile ~/.ssh/id_rsa
Host master
    HostName {master_ip}
    User core
    IdentityFile ~/.ssh/id_rsa
Host worker
    HostName {worker_ip}
    User core
    IdentityFile ~/.ssh/id_rsa
~~~
이제 설치중에 편하게 `ssh boot` 등과 같은 명령어로 노드에 접근할 수 있습니다.  

#### 4. install-config.yaml 생성
기본 틀은 다음과 같습니다.  
~~~yaml
apiVersion: v1
baseDomain: hololy-dev.com
compute:
- hyperthreading: Enabled
  name: worker
  replicas: 1
controlPlane:
  hyperthreading: Enabled
  name: master
  replicas: 1
metadata:
  name: clusterName
networking:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  networkType: OpenShiftSDN
  serviceNetwork:
  - 172.30.0.0/16
platform:
  none: {}
fips: false
pullSecret: '{"auths": ...}'
sshKey: 'ssh-ed25519 AAAA...'
additionalTrustBundle: | 
  -----BEGIN CERTIFICATE----- 
  ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ 
  -----END CERTIFICATE----- 
imageContentSources:
- mirrors: 
  - <local_registry>/<local_repository_name>/release 
  source: quay.io/openshift-release-dev/ocp-release 
- mirrors: 
  - <local_registry>/<local_repository_name>/release 
  source: registry.svc.ci.openshift.org/ocp/release
~~~

여기서 수정해 주어야 할 것들 :  
1. `baseDomain` : 자신의 도메인주소로 변경
2. `compute.replicas` : worker노드의 개수
3. `controlePlane.replicas` : master노드의 개수
4. `metadata.name` : 클러스터 이름 수정
5. `pullSecret` : [https://cloud.redhat.com/openshift/install/pull-secret](https://cloud.redhat.com/openshift/install/pull-secret) 여기서 복사  
처음 복사하면 다음과 비슷한 포맷으로 출력되는데,
    ~~~sh
    {"auths": {"cloud.openshift.com": {"auth": "b3Blbn...","email": "ddd@example.com"},"quay.io": {"auth": "b3Blbn...","email": "ddd@example.com"},"registry.connect.redhat.com": {"auth": "NTMwN...","email": "ddd@example.com"},"registry.redhat.io": {"auth": "NTMwN...","email": "ddd@example.com"}}}
    ~~~  
    여기에 위에서 생성했던 로컬registry 시크릿도 추가해줘야합니다.  
    ex)  
    ~~~sh
    {"auths": {"cloud.openshift.com": {"auth": "b3Blbn...","email": "ddd@example.com"},"quay.io": {"auth": "b3Blbn...","email": "ddd@example.com"},"registry.connect.redhat.com": {"auth": "NTMwN...","email": "ddd@example.com"},"registry.redhat.io": {"auth": "NTMwN...","email": "ddd@example.com"},"registry.gru.hololy-dev.com:5000":{"auth": "YWRtaW46cGFzc3cwcmQ=","email": "ddd@example.com"}}}
    ~~~

6. `sshKey` : 위에서 `ssh-keygen`으로 생성한 public key(~/.ssh/id_rsa.pub)
7. `additionalTrustBundle` : registry만들 때 사용한 cert파일(/opt/registry/certs/domain.crt)   
    아래 사진과 같이 추가해주시면 됩니다. 왼쪽에 노란색 펜으로 표시한 부분처럼 indent에 주의하여 붙여넣어야 합니다.  
    ![image](https://user-images.githubusercontent.com/15958325/95045080-181d8a80-071c-11eb-82f1-1b2a2067af08.png)   

8. `imageContentSources` : 로컬 MirrorRegistry 미러링끝나고 나서 출력된 imageContentSources를 그대로 붙여넣어주시면 됩니다.  

#### 5. Manifests & Ignitions
설치를 진행하면서 install-config.yaml파일은 사라지므로 백업을 떠두고 진행하도록 합니다.  
~~~sh
$ cp install-config.yaml install-config.yaml.bak
~~~

manifest파일 생성 :  
~~~sh
# install-config.yaml파일이 있는 폴더내에서 실행하면 설치 폴더의 위치를 명시해주지 않아도 됩니다.  
$ ../openshift-install create manifests

INFO Consuming Install Config from target directory
WARNING Certificate F91CF231C699768ED98F4D5EE9EA1810 from additionalTrustBundle is x509 v3 but not a certificate authority
~~~

ignition파일 생성
~~~sh
$ ../openshift-install create ignition-configs 

INFO Consuming OpenShift Install (Manifests) from target directory
INFO Consuming Worker Machines from target directory
INFO Consuming Master Machines from target directory
INFO Consuming Openshift Manifests from target directory
INFO Consuming Common Manifests from target directory
~~~

생성된 ignition파일들을 HTTP파일서버의 공유폴더로 옮깁니다.  
~~~sh
# ignition파일들을 nginx 파일 서버로 옮김
$ cp *.ign /usr/share/nginx/html/files/

# 파일 권한도 외부에서 접근 가능하게 변경
$ chmod 644 /usr/share/nginx/html/files/*.ign
~~~

#### 6. raw파일 다운로드

다음 링크에서 원하는 버전의 coreOS raw파일을 찾아서 다운로드 받습니다.  
-> [https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/](https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/)

![image](https://user-images.githubusercontent.com/15958325/95045670-78f99280-071d-11eb-9e02-929304f49f84.png)  

~~~sh
# nginx파일 서버에 raw파일 다운로드
$ cd /usr/share/nginx/html/files/
$ wget https://mirror.openshift.com/pub/openshift-v4.......raw.gz
~~~

#### 7. vm 생성 및 CoreOS설치

CoreOS 설치 초기화면 :   
![](https://user-images.githubusercontent.com/15958325/82871409-7bc4c980-9f6c-11ea-9868-bbad71b0f807.png)  

설치파라미터 (tab키누르고 입력) :   
~~~sh
coreos.inst.install_dev=sda 
coreos.inst.image_url=http://{fileserver}:8080/rhcos-4.3.8-x86_64-metal.x86_64.raw.gz
coreos.inst.ignition_url=http://{fileserver}:8080/bootstrap.ign 
ip={static ip}::{gateway}:{netmask}:{hostname}:{network interface}:none
nameserver={dns}
~~~
각 파라미터간의 구별은 enter가 아닌 공백으로 구분해야합니다.  

boot가 올라온 뒤, master와 worker도 띄우고 기다리면 설치가 완료되는 것을 확인하실 수 있습니다.  
이후의 프로세스는 [이전에 올린 포스팅](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/#)의 과정과 동일하니 참고하시면 될 것 같습니다.   

설치 중 에러에 관해서는 -> [여기](https://gruuuuu.github.io/ocp/ocp4-install-error/)


설치를 마치고 나서 Openshift GUI화면의 카탈로그를 보면 아무런 이미지를 찾아보실 수가 없을겁니다. 그냥 순전히 openshift itself 기능만 사용할 수 있는데, Restricted Network에서 카탈로그를 사용하려면 OperatorHub를 따로 구축을 해주셔야 합니다.  

다음 포스팅에서는 **OperatorHub**에 관한 내용을 다루도록 하겠습니다.  

----

