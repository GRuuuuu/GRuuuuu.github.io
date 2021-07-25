---
title: "Openshift Ingress Certificate 구성"
categories: 
  - OCP
tags:
  - Kubernetes
  - Openshift
last_modified_at: 2021-07-25T13:00:00+09:00
toc : true
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 문서에서는 Openshift클러스터의 Ingress에 Certificate를 구성하여  
탭 상단의 "**Not Secure**" 경고를 없애보도록 하겠습니다.  

## 문제
Openshift를 처음 구성하고 나서 콘솔로 들어가보시면 아래와 같은 경고 메세지를 확인하실 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/126896505-b5141473-15d5-43b6-be8c-689ccadd5940.png)  

기본적으로 Openshift는 내부 Ingress Operator를 통해 Internal CA를 생성합니다.  
해당 CA는 `.apps.{clusterName}.{baseDomain}`의 와일드카드 Certificate로, **Self-signed Certificate**입니다.   
때문에 **신뢰할 수 없는 연결**이라고 뜨게 되죠.  

이걸 해결하려면 **`.apps` 서브 도메인에 대해 fully qualified된 certificate가 있어야 합니다.**  

> 같이 읽으면 좋은 글: [alice_k106님의 블로그/154. [Security] SSL과 인증서 구조 이해하기 : CA (Certificate Authority) 를 중심으로](https://m.blog.naver.com/alice_k106/221468341565)  

## Wildcard Certificate받기 (Let's Encrypt)
OCP Ingress의 기본 CA를 변경하기 위해 신뢰할 수 있는 기관에 인증받은 Certificate를 발급받아줘야 합니다.  

기존에 Mirror Registry를 구성할 때 [ZeroSSL에서 인증서를 발급받은 적](https://gruuuuu.github.io/network/openssl/)이 있는데, 여기는 와일드카드 도메인에 대한 인증서가 유료이므로... 이번엔 Let's Encrypt를 사용하도록 하겠습니다.  

서버 스펙: `ubuntu 20.04`  

>운영체제 별 `certbot` 설치방법 : [https://certbot.eff.org/](https://certbot.eff.org/)

### snap 설치
~~~sh
$ sudo apt install snapd
~~~

~~~sh
$ snap version
snap    2.49.2+20.04
snapd   2.49.2+20.04
series  16
ubuntu  20.04
kernel  5.4.0-72-generic
~~~

### certbot 설치
~~~sh
$ sudo snap install --classic certbot
certbot 1.17.0 from Certbot Project (certbot-eff✓) installed
~~~

### WildCard 인증서 받기
certbot으로 도메인에 대한 인증서를 받는 방법은 여러가지가 있는데, 와일드카드 도메인에 대한 인증서를 받을때에는 DNS에 TXT레코드를 추가하여 인증을 받는 방법밖에 없습니다.  

인증받을 도메인을 `-d`로 이어서 지정해주면 됩니다.  
Openshift Ingress용으로 사용할 도메인은 `.apps.{clusterName}.{baseDomain}`형태입니다.  
>EX) *.apps.test.hololy.net  
>만약 이 형식을 지키지 않으면 Ingress Controller에서 인식못함!  
>DNS와 다르게 CA는 도메인 레벨을 구별합니다.  
>-> `*.apps.test.hololy.net` != `*.test.hololy.net`

~~~sh
$ sudo certbot certonly --manual --preferred-challenges dns -d "*.apps.test.hololy.net"
~~~

그럼 다음과 같이 이메일과 서비스에 대한 동의 문구가 뜨게 됩니다. 모두 Y로 체크해주도록 합시다.  
~~~sh
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): ddd@ddd.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.2-November-15-2017.pdf. You must
agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y
Account registered.
Requesting a certificate for *.test.hololy.net
~~~

다음으로 넘어가게 되면 DNS에 TXT레코드 어떤식으로 추가해서 검증을 받을 지 나오게 됩니다.  
~~~sh
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name:

_acme-challenge.apps.test.hololy.net.

with the following value:

R1mdvZivahrxdidddClNP1KdQFEfwdddtG2XcDhtVyc

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue
~~~

DNS에 TXT레코드를 추가해주고, 엔터를 눌러 진행해줍니다. (5~15분 기다려야 함)  

성공적으로 인증이 되면 아래와 같은 메세지가 뜨면서 Certificate가 발급됩니다.  
~~~sh
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/apps.test.hololy.net/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/apps.test.hololy.net/privkey.pem
This certificate expires on 2021-10-21.
These files will be updated when the certificate renews.
~~~

폴더를 가보면 총 4개의 pem파일이 생성됩니다.  
~~~sh
$ ls
README  cert.pem  chain.pem  fullchain.pem  privkey.pem
~~~

- `privkey.pem` : 인증서를 위한 비밀키
- `fullchain.pem` : 인증서와 체인 인증서가 합쳐진 전체 파일입니다. 대부분의 서버 소프트웨어에서 사용됩니다.
- `chain.pem` : Nginx >=1.3.7에서 OCSP stapling을 위해서 사용됩니다.
- `cert.pem` : 생성된 인증서 파일입니다.

Ingress에 적용시킬 파일들은 `fullchain.pem`과 `privkey.pem`입니다.  

## openshift default ingress certificate 치환
공식문서 : [Replacing the default ingress certificate](https://docs.openshift.com/container-platform/4.7/security/certificates/replacing-default-ingress-certificate.html)  

### `fullchain.pem`을 `configmap`으로 생성  
~~~sh
$ oc create configmap custom-ca --from-file=ca-bundle.crt=/etc/letsencrypt/live/apps.test.hololy.net/fullchain.pem -n openshift-config
~~~

### cluster-wide proxy 설정 변경
새로만든 configmap을 사용하도록 변경합니다.  
~~~sh
$ oc patch proxy/cluster --type=merge --patch='{"spec":{"trustedCA":{"name":"custom-ca"}}}'
~~~

### secret 생성 (certificate chain과 private key)  
~~~sh
$ oc create secret tls secret-ca \
--cert=/etc/letsencrypt/live/apps.test.hololy.net/fullchain.pem \
--key=/etc/letsencrypt/live/apps.test.hololy.net/privkey.pem \
-n openshift-ingress
~~~

### Ingress Controller secret 변경
~~~
$ oc patch ingresscontroller.operator default \
--type=merge -p \
 '{"spec":{"defaultCertificate": {"name": "secret-ca"}}}' \
 -n openshift-ingress-operator
~~~

바꿔주고 ingress controller와 router들이 한번 재시작하고나면 정상적으로 secure연결이 활성화 된 모습을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/126899776-3f057456-00e9-41c6-9ede-cc660a32acb6.png)  

또한 브라우저 인증서 설정을 보게되면 신뢰할 수 있는 루트기관까지 제대로 연결된 모습을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/126899807-cca632b8-c362-452c-a768-6ce83e4fb2bf.png)  


----