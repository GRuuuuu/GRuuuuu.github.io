---
title: "호다닥 톺아보는 SSL/TLS (feat. Openshift)"
slug: tls-termination
tags:
  - Kubernetes
  - Openshift
  - Security
date: 2023-10-08T13:00:00+09:00
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

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2021-08-29-what-is-x509/14.png)  

1. `ClientHello` : Client가 Server에게 "HELLO"메세지를 전송하면서 Handshake 프로세스가 개시됩니다. 이 때 Client는 랜덤한 난수데이터와, 지원하는 암호화 방식들, TLS버전 등을 Server에 같이 보냅니다.  
2. `ServerHello` : `ClientHello`메세지에 대한 응답으로, Server의 인증서와 TLS에 사용할 암호화 종류, Server에서 생성한 랜덤한 난수데이터를 Client에 보냅니다.  
3. `Certificate` : Client는 웹브라우저에 등록된 "신뢰할 수 있는 인증서" 목록에 있는 공개키로 인증서 해시값을 비교하여 Server를 신뢰할 수 있는지 검증합니다.  
4. `ServerHelloDone`

그 다음 Client와 Server는 설정했던 암호화 방식으로 정보를 암호화해서 통신을 시작하게 되는데요,  
비대칭키 방식으로 암호화 통신을 할 수도 있겠지만, 이런 방식은 많은 컴퓨팅 파워를 소모하게 됩니다. 그래서 실제로 데이터를 주고받을 때에는 대칭키 방식으로 진행하게 됩니다.  

이 대칭키를 해킹으로 뺏겨버리면 쉽게 정보가 누출될 수 있으니 TLS Handshake에서는 키 자체를 통신망에 노출시키지 않고 Server와 Client모두 동일한 키를 가질 수 있도록 하고 있습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2021-08-29-what-is-x509/15.png)   

5. `ClientKeyExchange` : Client는 주고받은 랜덤데이터를 조합하여 PMS(Pre Master Secret)이라는 일종의 난수값을 생성해 Server가 보내준 인증서의 Server공개키로 암호화해 Server로 전송합니다.  
6. `ChangeCipherSpecFinished` : Server/Client는 PMS, Client 난수, Server 난수 세가지 값을 바탕으로 각각 같은 대칭키를 생성하고 이 키를 이용해 암호화 통신을 시작합니다.  

한 장으로 정리해보면 아래와 같은 모양이 됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-08-tls-termination/1.png)  
> 이미지 출처 : [Cloudflare/What is a TLS handshake?](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/)  


## TLS Termination
위와 같이 안전한 통신을 하기 위해선 Server와 Client에 많은 과정을 거치게 되는데, 이와 같은 과정을 Server가 직접 하게 되면 상당히 많은 부하가 걸리게 됩니다.  

예를 들어 Client가 100만명이고 이 모든 Client들에 대해 전부 TLS통신을 구축하려면 엄청난 리소스가 필요하겠죠...  

그래서 대부분의 경우 앞단에 proxy용 서버를 두거나 LoadBalancer에 **TLS관련 작업을 위임해**, Server가 그 역할에 집중할 수 있게 해줌으로써 좀 더 쾌적한 서비스를 제공할 수 있게 합니다.  

이러한 전략을 **TLS Termination** 또는 **TLS/SSL Offloading**이라고 부릅니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-08-tls-termination/2.png)   
> 이미지 출처 : [wiki/TLS termination proxy](https://en.wikipedia.org/wiki/TLS_termination_proxy)   

- 실제 TLS통신은 Proxy/LB와 Client사이, Public Network에서만 이뤄짐
- Client에게서 받은 암호화된 데이터는 LB단에서 복호화, 내부 서버끼리는 평문으로 통신
- 컴퓨팅 리소스가 많이 소모되는 암호화/복호화를 Proxy/LB단에서 처리함으로써 내부 통신을 빠르게 처리할 수 있게 됨
- 마찬가지로 Server에서 나가는 데이터도 LB단에서 암호화되어 안전하게 Client에게 전달
- 인증서를 로드밸런서에서 관리하기때문에 통합적으로 관리 가능


## TLS Termination in OpenShift
TLS Termination을 설명할 때 자주 드는 예시는 웹서버입니다.  
그러면 Kubernetes나 OpenShift같은 클러스터 환경에서는 어떨까요?  

클러스터에는 수많은 Pod들이 떠있고 각자 서비스를 노출시킬 수 있습니다. 만약 TLS Termination을 적용시키지 않고 안전한 연결을 하려면 각 Pod에 큰 부하를 주게될 것입니다.  

Kubernetes에서는 `Ingress`를 사용해서 TLS Termination을 구현할 수 있고,  
OpenShift에서는 `Route`라는 component를 제공합니다.  

>이번 문서에서는 OpenShift의 `Route`를 다룰것이나, 여기서 제공하는 정책은 Kubernetes에서도 구현이 가능하니 참고하시면 될 것 같습니다.  

### Route tls termination
OpenShift의 `Route`는 `Ingress`와 비슷하게 `Service`들의 로드밸런싱과 네트워킹을 담당하는 리소스이지만, `Ingress`와 다르게 기본적으로 TLS관련 기능들을 제공하고 있습니다.  

총 세가지 정책이 있습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-08-tls-termination/3.png)    

1. **Edge**: `Route`가 데이터를 복호화하고 복호화된 트래픽을 서비스에 전달, 클러스터 내에서는 해당 트래픽이 insecure함
2. **Re-encrypt**: `Route`가 데이터를 다시 암호화하여 서비스로 전송   
3. **Passthrough**: `Route`가 데이터를 복호화하지 않고 그대로 서비스에 전달  

위에서 언급했었던 TLS Termination의 예시가 OpenShift의 `Route`에서는 `edge`라는 이름의 정책으로 구현되어있습니다.  
이 경우 Service는 HTTP통신으로 노출되어있어야 합니다.  

`Re-encryption`의 경우 다시 한번 복호화를 해서 서비스로 넘기는만큼 Route와 Service 뒷단의 Pod에 많은 부담을 주게 됩니다. 하지만 그만큼 안전을 보장할 수 있습니다.  
Service의 인증서가 Cluster의 인증서와 상이할 경우 사용합니다.  
`edge`와 다르게 Service로 암호화된 데이터가 전달되므로 Service는 HTTPS통신이 노출되어있어야 합니다.  

`passthrough`의 경우 복호화든 암호화든 하지 않고 바로 Service로 트래픽을 넘겨버립니다.  
이 경우 Cluster 내부에서도 안전한 TLS통신을 할 수 있지만 Pod에 부담이 걸리게 되고, 인증서 관리를 Pod단에서 해주어야한다는 불편이 있습니다.  
이녀석도 Service가 HTTPS통신이 노출되어 있어야 합니다.  

----