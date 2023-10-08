---
title: "호다닥 톺아보는 SSL/TLS (feat. Openshift)"
categories: 
  - Security
tags:
  - Kubernetes
  - Openshift
  - Security
last_modified_at: 2023-10-02T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
2년전쯤에 [X509에 관한 포스팅](https://gruuuuu.github.io/security/what-is-x509/)을 한 적이 있었는데요, 이번 포스팅은 그 후속편이라고 봐주시면 될 것 같습니다.  

>아니 근데 그게 벌써 2년전이라니... 이거 적으면서 확인했는데 너무 충격...😅  

우리가 웹사이트를 방문할 때 신뢰할 수 있는 연결을 수립하기 위해선, 보안 통신과 신뢰할 수 있는 인증서가 필요합니다.  
지난 포스팅에서는 그 중에서 인증서에 대한 내용을 다뤘었고,  
이번 포스팅에서는 통신 자체에 대해서 다뤄보려고 합니다.  

그리고 그 연결이 Kubernetes 또는 Openshift에서는 어떤식으로 동작하는지도 알아보겠습니다.  

## SSL/TLS란?

웹에서의 전송 데이터가 암호화되어있지 않다면 어떤 일이 발생할까요?  
익명의 누군가가 데이터를 가로채서 바로 내용을 확인하는 일도, 변조하는 일도 가능할 것입니다.  

인터넷 상의 통신에서 보안을 확보하려면 서로 신뢰할 수 있는 자임을 확인할 수 있어야 하며, 서로간의 통신내용이 제 3자에 의해 도청되는 것을 방지해야합니다.  
이를 위해 현재 웹 통신에서는 **신뢰할 수 있는 기관에서 발행한 인증서**와, 통신내용을 **암호화**하는 방식으로 보안 연결을 제공하고 있습니다.  

이런 통신규약들을 묶어서 정리한 프로토콜이 바로 SSL/TLS라고 보시면 됩니다.  

### SSL(Secure Sockets Layer)
1995년 Netscape의 SSL2.0이 공개되면서 웹보안의 서막을 열었지만 바로 취약점이 발견되면서 다음해 SSL3.0로 대체되었습니다.  

하지만 3.0도 여러 취약점을 가지고 있었기에, 그로부터 3년 뒤 이를 개선한 버전인 TLS 1.0이 등장하고 RFC2246 표준으로써 자리잡게 됩니다.   

어른들의 사정으로 SSL을 개발했던 Netscape가 더이상 업데이트에 참여하지 않게 되어 새로 이름을 브랜딩한게 **TLS(Transport Layer Security)**라고 보시면 됩니다.  

SSL 2.0, 3.0모두 **현재는 사용되지 않는 프로토콜**이며 여러 취약점이 존재하기 때문에 암호화 프로토콜로써의 기능을 잃은 상태입니다.   

웹에서의 암호화 프로토콜을 아직도 SSL이라고 칭하는 곳이 있기는 하지만 실제 거의 대부분의 브라우저에서 **SSL이 아닌 TLS방식을 지원**하고 있기 때문에 해당 포스팅에서는 SSL의 대한 내용은 더 깊게 안들어가려고 합니다.  

>**한줄정리**
>- 웹 통신보안을 위해 태어난 SSL
>- 보안 취약점과 어른들의 사정으로 TLS로 이름바꾸고 업데이트
>- 현재는 사용되지 않는 프로토콜 SSL

### TLS(Transport Layer Security)
SSL의 취약점을 보완해서 나온 업데이트 버전 TLS!  

그 동작과정을 살펴보도록 하겠습니다.  

#### TLS Handshake
TLS는 안전한 인터넷 통신을 위한 암호화 및 인증 프로토콜이고 **TLS Handshake**는 TLS를 사용하는 통신 프로세스입니다.  
어떻게 서버와 클라이언트가 서로를 인식하고, 검증하고, 안전하게 통신을 할 수 있는지 알아보도록 하겠습니다.  


1. `ClientHello`  
<그림>
Client가 Server에게 "HELLO"메세지를 전송하면서 Handshake 프로세스가 개시됩니다.  






https://velog.io/@osk3856/TLS-Handshake
https://www.cloudflare.com/ko-kr/learning/ssl/what-happens-in-a-tls-handshake/