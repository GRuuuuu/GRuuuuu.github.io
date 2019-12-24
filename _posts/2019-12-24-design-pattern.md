---
title: "Multi-Container Design Patterns 정리"
categories: 
  - Container
tags:
  - Container
  - Cloud
  - Design-Pattern
  - Sidecar
  - Proxy
  - Ambassador
last_modified_at: 2019-12-24T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
지난 몇년간 컨테이너기술은 코드를 패키징하고 배포하는데 대중적인 기술이 되었습니다. 이런 특징 외에도 컨테이너를 통해 **분산 응용 프로그램을 구축**하는 방법에 대해서 주목해볼 필요가 있습니다.  
이번 글에서는 `MicroService Architecture`에서 컨테이너들을 다루는 디자인패턴 3개를 소개하겠습니다.

> 참고 : [MicroService Architecture란?](https://gruuuuu.github.io/container/architecture-microservice/)   
> 참고문헌 : [Kubernetes/The Distributed System ToolKit: Patterns for Composite Containers](https://kubernetes.io/blog/2015/06/the-distributed-system-toolkit-patterns/)

# Sidecar Pattern
먼저 대전제로 생각하고 있어야 하는 것은 다음과 같습니다.  
> **"하나의 컨테이너에는 하나의 책임만 가지고 있어야 한다."**  

예를 들어 웹서버와 로그수집기가 같이 있는 컨테이너를 생각해봅시다.  
웹서버를 수정하려고 할 때, 로그수집기와의 종속성등을 고려해야 합니다. 또한 직접적인 관련이 없더라도 에러가 발생했을 때 어디서 문제가 발생했는지 빠르게 파악하지 못할 수도 있습니다.  

때문에 **서로 다른 역할을 하는 서비스는 각각의 컨테이너로 분리**를 해주어야 합니다.  

이 때 사용하는 패턴이 **사이드카 패턴**입니다.  

<center><img src="https://user-images.githubusercontent.com/15958325/71398333-65d07700-2663-11ea-8a29-d2be848ea428.png"></center>  

pod안의 **메인 컨테이너를 확장하고 향상시키며 개선시키는 역할**을 하는 컨테이너를 `Sidecar Container`라고 하며, 해당 패턴을 `Sidecar Pattern`이라고 합니다.   

위 그림에서는 Web Server가 메인 컨테이너가 되며 같은 파일시스템을 공유하는 로그수집기가 사이드카 컨테이너가 되는 구조입니다.  

이렇게되면 웹서버를 바꾸더라도 로그수집기는 수정하지 않아도 됩니다.  
컨테이너의 재사용성이 증가하게 되는 것이죠.  

# Ambassador Pattern

<center><img src="https://user-images.githubusercontent.com/15958325/71399761-06c13100-2668-11ea-8f92-67b29984afa7.png"></center>  

Ambassador패턴은 메인컨테이너의 **네트워크 연결을 전담하는 프록시 컨테이너**를 두는 패턴입니다.  

이를 통해 메인 컨테이너는 기능 자체에 집중할 수 있고 네트워크 컨테이너에서는 네트워크 기능에 집중할 수 있게 됩니다.  

# Adapter Pattern
<center><img src="https://user-images.githubusercontent.com/15958325/71400235-6bc95680-2669-11ea-86a0-3254e3a60583.png"></center>  

Adapter패턴은 **메인컨테이너의 출력을 표준화**시킵니다.  

이를 통해서 메인컨테이너에서는 다른 컨테이너와의 연결을 신경쓰지 않을 수 있습니다.  

예를 들어, 위 그림과 같이 모니터링 pod이 존재하고 해당 팟에서 다른 pod들의 모니터링 정보를 수집하는 경우를 생각해봅시다.  

모니터링 pod에서 다른 pod들의 cpu사용량과 ram사용량 정보만 뽑아서 보고싶다고 할때, <u>메인컨테이너의 출력은 변환하지 않고 어댑터컨테이너만 수정</u>하여 일관된 정보를 모니터링 pod에게 줄 수 있습니다.  

# Differences between Sidecar and Ambassador and Adapter pattern  

> StackOverflow : [Differences between Sidecar and Ambassador and Adapter pattern](https://stackoverflow.com/questions/59451056/differences-between-sidecar-and-ambassador-and-adapter-pattern)  

세가지 패턴을 모두 익혔으면 이쯤되서 궁금증이 생길것입니다.  

> Ambassador&Adapter패턴의 프록시 컨테이너나 어댑터 컨테이너도 컨테이너인데 왜 이 패턴들은 sidecar패턴이라고 하지 않지?   

> 인터넷에서 찾아보니 envoy proxy라는 프록시는 sidecar 패턴이라고 소개되는 경우가 많은데... 프록시는 Ambassador 패턴이 아닌가..?

위 물음들은 제가 공부하면서 느꼈던 의문들입니다.  

그래서 이곳저곳 찾다가 안나오길래 스택오버플로우에 질문을 올렸었는데 답을 받아서 이 포스팅에도 정리를 하려고 합니다.  

정리하자면 Ambassador&Adapter패턴의 프록시 컨테이너나 어댑터 컨테이너 둘 다 메인컨테이너로의 **통신에 관여**합니다.  
또한 둘 다 **컨테이너**죠.  

세 패턴의 다른 점은 각 컨테이너들의 목적입니다.  

**Sidecar** : 메인컨테이너의 기능을 **확장** 또는 **향상**
**Ambassador** : 메인컨테이너의 **네트워크**기능 담당
**Adapter** : 메인컨테이너의 **출력을 변환**

다시 돌아와서 envoy프록시같은 경우, Istio위에서 네트워크기능을 담당하는 것 이상의 기능을 수행하기 때문에 Sidecar라고 불리는 것 같습니다.  

결국 하나의 컨테이너는 하나의 기능만 가져야 한다는 대전제는 동일하고,  
컨테이너가 어떤 목적을 가지고 메인컨테이너를 보조하는지에 따라 패턴이름이 나뉘는 것 같습니다.  


----
