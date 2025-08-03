---
title: "호다닥 공부해보는 x509와 친구들(2) - Let's Encrypt"
slug: letsencrypt
tags:
  - Security
  - Auth
date: 2021-09-09T13:00:00+09:00
---

## Overview
지난 포스팅에서 x509란 무엇인지, PKI와 CA 그리고 인증서에 대해서 알아보았습니다.  
지난포스팅 -> [호다닥 공부해보는 x509와 친구들](https://gruuuuu.github.io/security/what-is-x509/)  

이번 포스팅에서는 실제로 인증서를 발급해보고, 웹서버에 적용시켜 신뢰할 수 있는 사이트를 만들어보도록 하겠습니다.  

## Let's Encrypt?
신뢰할 수 있는 인증서를 발급해줄 수 있는 CA는 여러군데 있지만 무료로 인증서를 발급해주는 CA는 흔치 않습니다.  

Let's Encrypt는 인증서 수동생성, 유효성 확인, 디지털 서명, 설치 및 갱신의 복잡한 프로세스를 **자동화**시켜, **무료**로 SSL인증서를 발급해주는 CA(Certificate Authorities)입니다.  

인증서의 무료 보급을 통해 모든 인터넷 웹서버들에 대해 암호화된 연결을 생성하는 것을 목표로 2016년 출범하였습니다.  

무료지만 타 인증서들과 동일한 신뢰도를 가지며 SSL암호화 기술방식과 동작도 **정확히 동일**합니다.  
다른 점은 사이트의 인증에 문제가 생겨 최종 웹사이트 방문자가 피해를 입었을 경우의 배상여부만 차이가 있습니다.  

하지만 자동화 과정때문에 엄격한 심사가 이루어지기 힘들다는 점이 있어, Let's Encrypt로는 **Domain Validated certificate**만 발급받을 수 있습니다. (OV, EV 발급 불가능)  

> **Background++**  
>SSL인증서 심사 수준에 따른 레벨:  
> 1. **DV(Domain Validation)** : 도메인 유효성 검사  
>   도메인 소유권 심사를 통해 발급되는 가장 쉽고 빠른 인증서, 회사에 대한 정보 확인 불가능  
>   ![image](https://user-images.githubusercontent.com/15958325/132977035-c1c52e54-b9b9-4a06-b76b-6da08fe3f6af.png)  
>
>2. **OV(Organization Validation)** : 조직 유효성 검사  
>   비즈니스 적법성 검증과 도메인 소유권 심사를 통해 발급, 검증된 회사 정보는 인증서에 표기됨  
>   ![image](https://user-images.githubusercontent.com/15958325/132977148-d9354649-a62e-4a2f-a8e8-5d942c1ca465.png)  
>3. **EV(Extended Validation)** : 확장 유효성 검사
>   DV,OV보다 까다로운 검증을 통해 기업의 실존성을 인증. EV인증서를 소유한 사이트는 브라우저에서 도메인 소유 회사의 이름이 표시되어 안전한 사이트임을 확인할 수 있음  
>   ![image](https://user-images.githubusercontent.com/15958325/132977226-e8f795c2-fde5-401d-8e5e-45b058135630.png)  
>   ![image](https://user-images.githubusercontent.com/15958325/132977236-9c9864c3-f62e-4e85-9839-da32ac2d21a3.png)  

정리하자면,  
1. 인증절차가 단순하고
2. 대기시간 없이 바로 발급
3. 유효기간 90일이 있지만, 자동갱신 설정가능
4. 무료
라는 장점들로 인해 Let's Encrypt는 많은 사랑을 받고 있습니다.  

## Let's Encrypt로 인증서 발급받기!

Let's Encrypt의 인증서는 [ACME(Automatic Certificate Management Environment)](https://en.wikipedia.org/wiki/Automated_Certificate_Management_Environment) 프로토콜을 준수하는 프로그램을 이용해 발급을 받을 수 있는데, Let’s Encyrpt는 `Certbot` 사용을 권장하고 있습니다. 

![image](https://user-images.githubusercontent.com/15958325/132977507-22f124fc-f178-4c1a-a1c7-b02f97a0da2f.png)  

시스템 관리자는 Certbot을 통해 인증서를 직접 요청할 수 있습니다.  

Certbot Instructions -> [https://certbot.eff.org/instructions](https://certbot.eff.org/instructions)  
위 페이지를 통해서 여러 설치방법들을 볼 수 있습니다.  

이 포스팅에서는 그 중 일부 방법만 테스트해보도록 하겠습니다.  

## 0. 테스트용 nginx서버 올리기

![image](https://user-images.githubusercontent.com/15958325/132977803-b1f7700a-f017-4072-94c6-d1a5f698ceaf.png)  

도메인에 레코드를 등록해 웹서버의 ip를 가리키도록 설정해주도록 하겠습니다.  

![image](https://user-images.githubusercontent.com/15958325/132977919-d4664a2d-0624-4ffa-b73a-7214097a4cb3.png)  

![image](https://user-images.githubusercontent.com/15958325/132977999-22524cef-8018-4793-96e6-d40fd98a6744.png)  

준비 끝!  

# 인증서 발급받기

방법은 여러개가 있지만 이 포스팅에서는 4가지 방법을 소개하도록 하겠습니다.  
1. Webroot로 발급받기
2. Standalone으로 발급받기
3. nginx를 통해 발급받기
4. DNS레코드를 통해 발급받기

## 1. Webroot로 발급받기
웹서버를 중단하지 않고도 인증서를 발급받을 수 있는 방법입니다.  
사이트 디렉토리 내에 인증서 유효성을 확인할 수 있는 파일을 업로드하여 인증서를 발급받을 수 있습니다.  
외부에서 사이트에 접속하여 검증하게 됩니다.  

### snap 설치
~~~
$ sudo snap install core; sudo snap refresh core
~~~
> 기존에 `apt`나 `dnf` 또는 `yum`으로 `certbot`을 설치한 적이 있다면 삭제 후 `snap`으로 재설치할것

### certbot 설치
~~~
$ sudo snap install --classic certbot
~~~

링크:  
~~~
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot
~~~

### well-known 폴더 생성
~~~
$ mkdir -p /etc/letsencrypt/.well-known/acme-challange
~~~

### nginx conf 수정

~~~
$ vim /etc/nginx/snippets/letsencrypt.conf

location /.well-known/acme-challenge/ {
  root /etc/letsencrypt;
}
~~~

nginx default.conf를 열어서  
~~~
$ vim /etc/nginx/sites-enabled/default
~~~

위에서 생성했던 conf파일을 80번에 추가해줍니다.  

~~~conf
#EXAMPLE (ADD include /etc/nginx/snippets/letsencrypt.conf;)
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        include /etc/nginx/snippets/letsencrypt.conf;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
        }
~~~
nginx 재시작:  
~~~
$ systemctl restart nginx
~~~

### certbot 실행
~~~
$ certbot certonly --webroot --webroot-path=/etc/letsencrypt -d nginx.hololy.net
~~~

~~~
$ certbot certonly --webroot --webroot-path=/etc/letsencrypt  -d nginx.hololy.net

Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for nginx.hololy.net

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/nginx.hololy.net/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/nginx.hololy.net/privkey.pem
This certificate expires on 2021-12-11.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
~~~

~~~sh
$ ls /etc/letsencrypt/live/nginx.hololy.net
README  cert.pem  chain.pem  fullchain.pem  privkey.pem
~~~

이렇게 인증서가 생성됩니다.  

## 2. Standalone으로 발급받기
이 방식은 웹서버를 중단하고, 로컬 certbot이 서버자체에서 인증을 진행합니다.  
발급받는동안 서버를 중단해야한다는 단점이 있지만 훨씬 간편합니다.  

### certbot 설치
상동

### nginx 서비스 중지
~~~
$ systemctl stop nginx
~~~

### certbot 실행
~~~
$ certbot certonly --standalone -d nginx.hololy.net
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for nginx.hololy.net

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/nginx.hololy.net/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/nginx.hololy.net/privkey.pem
This certificate expires on 2021-12-11.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
~~~

~~~sh
$ ls /etc/letsencrypt/live/nginx.hololy.net
README  cert.pem  chain.pem  fullchain.pem  privkey.pem
~~~

## 3. Nginx를 통해 발급받기 
웹서버에서 직접 SSL인증을 실시하고 웹서버에 맞는 SSL세팅값을 부여해주는 방식입니다.  
2번 standalone방식과 비슷하지만 발급이나 갱신을 위해 웹서버를 중단시킬 필요가 없습니다.  

### certbot 설치
상동

### certbot 실행
nginx옵션을 붙여 실행시켜줍니다.  

~~~
$ certbot --nginx -d nginx.hololy.net

Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for nginx.hololy.net

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/nginx.hololy.net/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/nginx.hololy.net/privkey.pem
This certificate expires on 2021-12-11.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for nginx.hololy.net to /etc/nginx/sites-enabled/default
Congratulations! You have successfully enabled HTTPS on https://nginx.hololy.net

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
~~~
다른 옵션과 다르게 인증서 및 키생성과 더불어 certificate 세팅에 대한 것들이 `/etc/nginx/sites-enabled/default`에 추가된 것을 확인할 수 있습니다.  

~~~
...
    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/nginx.hololy.net-0002/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/nginx.hololy.net-0002/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = nginx.hololy.net) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
        listen 80 ;
        listen [::]:80 ;
    server_name nginx.hololy.net;
    return 404; # managed by Certbot
}
~~~
포트와 certificate위치, key위치그리고 ssl설정들이 추가되었습니다.  

재시작 없이 바로 페이지 새로고침을 해보면 아래 사진과 같이 https연결로 리다이렉트되는것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/132989660-02dccbe8-fd70-4095-b448-f52e8761ecdf.png)  


> `/etc/nginx/sites-enabled/default`에 자동으로 ssl설정을 적용시키고 싶지 않은 경우:  
>~~~
>$ certbot certonly --nginx
>~~~

## 4. DNS레코드를 통해 발급받기
마지막 방법은 번거롭긴하지만 wildcard 도메인에 대한 인증서를 받을 수 있는 유일한 방법입니다.  
- wildcard 인증서 발급 가능
- certbot사용자가 DNS를 관리/수정할 수 있어야함
- 갱신시마다 DNS에서 TXT값을 변경해야해서 자동갱신설정이 어려움

이전에 관련 내용을 적어둔게 있어서 링크로 대체하겠습니다.  
->[Wildcard Certificate받기](https://gruuuuu.github.io/ocp/ocp-ingress-ca/#wildcard-certificate%EB%B0%9B%EA%B8%B0-lets-encrypt)  


## 인증서 자동갱신하기
->[Renewing certificates](https://certbot.eff.org/docs/using.html?highlight=hooks#renewing-certificates)  

인증서 갱신이 가능한지 확인:  
~~~
$ certbot renew --dry-run
~~~

갱신:  
~~~
$ certbot renew
~~~

갱신할때 hook을 둬서 갱신전에 서비스를 멈췄다가 갱신 후, 서비스 재시작을 할 수도 있습니다.  
~~~
$ certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start"
~~~


## 사용이 끝난 인증서 삭제하기
사용이 끝난 인증서를 삭제하려면 `certbot delete` 명령어를 통해 골라서 삭제하면 됩니다.  
~~~
$ certbot delete

Saving debug log to /var/log/letsencrypt/letsencrypt.log

Which certificate(s) would you like to delete?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1: apps.gru.hololy.net
2: gru.hololy.net
3: nginx.hololy.net-0001
4: nginx.hololy.net-0002
5: nginx.hololy.net
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Select the appropriate numbers separated by commas and/or spaces, or leave input
blank to select all options shown (Enter 'c' to cancel):
~~~


----