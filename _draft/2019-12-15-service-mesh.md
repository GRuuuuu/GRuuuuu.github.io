---
title: "Service Mesh Architecture & Istio"
categories: 
  - Container
tags:
  - Container
  - Cloud
  - MSA
  - ServiceMesh
  - Istio
last_modified_at: 2019-12-15T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
(사진)
이전 포스팅에서 `MicroService Architecture`의 장단점에 대해서 알아봤습니다.  
기존 `Monolitic Architecture`의 단점을 극복하고 Cloud환경에서 시스템 운영을 최적화 시키기 위해 많이 사용되고 있습니다.  

하지만 여전히 몇가지 단점이 존재하는데요. 

이번 포스팅에서는 단점을 극복하기 위한 Architecture인 `Service Mesh Architecture`에 대해서 알아보겠습니다.

# 2. Service Mesh Architecture?
## MicroService Architecture의 단점
기존 `Monolitic Architecture`의 단점을 극복하고 작은 서비스들로 하나의 서비스를 이루는 것은 각각의 서비스들을 독립적으로 관리할 수 있다는 점에서 유연하게 운용할 수 있었지만  

거대해진 MSA시스템을 보면 수십개의 MicroService가 분리되어있고 운영환경에는 수천개의 서비스 인스턴스가 동작하고 있습니다.  

(사진)

물론 관리자는 수백~수천개의 인스턴스들을 모니터링하고 로깅해야하며 관리해야하는 책임이 주어지게 됩니다.  

또한 서비스간의 통신도 매우 복잡해질수밖에 없습니다.  

이와 같은 관리 및 프로그래밍 오버헤드를 낮추기위해 나온 아키텍처가 바로 **Service Mesh**입니다.  

## Service Mesh
기존의 서비스 아키텍처에서의 호출이 직접 호출방식이었다면,   
![그림1](https://user-images.githubusercontent.com/15958325/70859721-3af76c00-1f5b-11ea-9d3f-fc868218bc3c.png)  

`Service Mesh`에서의 호출은 서비스에 딸린 **proxy**끼리 이뤄지게 됩니다.  
![그림2](https://user-images.githubusercontent.com/15958325/70859730-742fdc00-1f5b-11ea-9582-66492eef9d8a.png)  

이는 서비스의 트래픽을 네트워크단에서 통제할 수 있게 하고, 또한 Client의 요구에 따라 proxy단에서 라우팅서비스도 가능하게 할 수 있습니다.  

이런 다양한 기능을 수행하려면 기존 TCP기반의 proxy로는 한계가 있습니다.  

그래서 `Service Mesh`에서의 통신은 사이드카로 배치된 **경량화되고 L7계층기반의 proxy**를 사용하게 됩니다.  

프록시를 사용해서 트래픽을 통제할 수 있다는 것 까지는 좋은데, 서비스가 거대해짐에 따라 프록시 수도 증가하게 됩니다.  

이런 문제를 해결하기 위해서 각 프록시에 대한 설정정보를 **중앙집중화된 컨트롤러**가 통제할 수 있게 설계되었습니다.  

![그림3](https://user-images.githubusercontent.com/15958325/70860414-c3c6d580-1f64-11ea-85d9-fdf9b384a058.png)  

프록시들로 이루어져 트래픽을 설정값에 따라 컨트롤하는 부분을 `Data Plane`이라고 하고,   
프록시들에 설정값을 전달하고 관리하는 컨트롤러 역할을 `Control Plane`이라고 합니다.  

----
Service Mesh의 구현체들은 몇가지가 존재하지만 이 포스팅에서는 가장 활발히 발전하고 있는 **Istio**에 대해서 설명을 하도록 하겠습니다.  

# 3. Istio
## What is Istio?
`Data Plane`으로 Envoy proxy를 사용하며 이를 컨트롤 해주는 `Control Plane`의 오픈소스 솔루션이 **Istio**입니다.  

> **Envoy Proxy?**  
> C++로 개발된 고성능 프록시 사이드카.  
> dynamic service discovery, load balancing, TLS termination, circuit breaker..등등의 기능을 포함

`Istio`로 구성된 Service Mesh를 개략적으로 살펴보면 다음 그림과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/70860649-7c8e1400-1f67-11ea-8897-abc3f55ff788.png)  

> 참고 : [istio architecture](https://istio.io/docs/ops/deployment/architecture/)

### Pilot  
- envoy에 대한 설정관리
- service discovery 기능 제공

> **Service Discovery :**  
>
>![image](https://user-images.githubusercontent.com/15958325/70860715-7ba9b200-1f68-11ea-9fab-bbd3de995c30.png)  
> 1. 새로운 서비스가 시작되고 pilot의 `platform adapter`에게 그 사실을 알림
>2. `platform adapter`는 서비스 인스턴스를 `Abstract model`에 등록
>3. **Pilot**은 트래픽 규칙과 구성을 `Envoy Proxy`에 배포
>
>이러한 특징으로 Istio는 k8s, consul 등 여러 환경에서 **트래픽 관리를 위해 동일한 운영자 인터페이스를 유지**할 수 있습니다.  

### Mixer
- Service Mesh 전체에서 액세스 제어 및 정책 관리
- 각종 모니터링 지표의 수집
- 플랫폼 독립적, Istio가 다양한 호스트환경 & 백엔드와 인터페이스할 수 있는 이유

### Citadel
- 보안 모듈
- 서비스를 사용하기 위한 인증
- TLS(SSL)암호화, 인증서 관리

### Galley
- Istio Configuration의 유효성 검사

## Istio 기능
구성요소를 살펴보았으니 Istio의 기능에 대해서 살펴보겠습니다.  

### Traffic management
쉬운 규칙 구성과 트래픽 라우팅을 통해 서비스간의 트래픽 흐름과 API 호출을 제어 할 수 있습니다.  

### Security
기본적으로 envoy를 통해 통신하는 모든 트래픽을 자동으로 TLS암호화를 합니다.  

### Policies
서비스간 상호작용에 대해 access, role등의 정책을 설정하여 리소스가 각 서비스에게 공정하게 분배되도록 제어합니다.  

### Observability
강력한 모니터링 및 로깅 기능을 제공하여 문제를 빠르고 효율적으로 감지할 수 있게 합니다.  

## 실습
추후 작성