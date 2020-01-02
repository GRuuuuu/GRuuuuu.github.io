---
title: "Service Mesh Architecture & Istio를 알아보자"
categories: 
  - Container
tags:
  - Container
  - Cloud
  - MSA
  - ServiceMesh
  - Istio
last_modified_at: 2019-12-30T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
(사진)  
[이전 포스팅](https://gruuuuu.github.io/container/architecture-microservice/)에서 `MicroService Architecture`의 장단점에 대해서 알아봤습니다.  
기존 `Monolitic Architecture`의 단점을 극복하고 Cloud환경에서 시스템 운영을 최적화 시키기 위해 많이 사용되고 있습니다.  

하지만 여전히 몇가지 단점이 존재하는데요.  

이번 포스팅에서는 단점을 극복하기 위한 Architecture중 `Service Mesh Architecture`에 대해서 알아보겠습니다.

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

프록시를 사용해서 트래픽을 통제할 수 있다는 것 까지는 좋은데, **서비스가 거대해짐에 따라 프록시 수도 증가**하게 됩니다.  

이런 문제를 해결하기 위해서 각 프록시에 대한 설정정보를 **중앙집중화된 컨트롤러**가 통제할 수 있게 설계되었습니다.  

![그림3](https://user-images.githubusercontent.com/15958325/70860414-c3c6d580-1f64-11ea-85d9-fdf9b384a058.png)  

프록시들로 이루어져 트래픽을 설정값에 따라 컨트롤하는 부분을 `Data Plane`이라고 하고,   
프록시들에 설정값을 전달하고 관리하는 컨트롤러 역할을 `Control Plane`이라고 합니다.  

----
Service Mesh의 구현체들은 몇가지가 존재하지만 이 포스팅에서는 가장 활발히 발전하고 있는 **Istio**에 대해서 설명을 하도록 하겠습니다.  

# 3. Istio
## What is Istio?
`Data Plane`의 메인 프록시로 Envoy proxy를 사용하며 이를 컨트롤 해주는 `Control Plane`의 오픈소스 솔루션이 **Istio**입니다.  

> **Envoy Proxy?**  
> C++로 개발된 고성능 프록시 사이드카.  
> dynamic service discovery, load balancing, TLS termination, circuit breaker..등등의 기능을 포함  
>
>참고1 : [호롤리한하루/Multi-Container Design Patterns 정리-sidecar pattern](https://gruuuuu.github.io/container/design-pattern/#sidecar-pattern)  
>참고2 : [호롤리한하루/envoy proxy란? (basic)](https://gruuuuu.github.io/container/envoy-proxy/)

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

# 실습 : BookInfo
4개의 `microservice`로 이루어진 간단한 application을 배포해보겠습니다.  

## 기능
책의 정보를 보여주는 페이지.  
책의 설명, 상세정보, 책의 리뷰정보를 확인할 수 있습니다.  

## 구조
`productpage` : details와 reviews 서비스를 호출  
`details` : 책의 상세정보    
`reviews` : 책의 리뷰가 담겨있고 ratings서비스를 호출  
`ratings` : 책의 별점정보  

추가로 `reviews` 서비스는 세가지 버전이 존재합니다.  
- `v1` : `ratings` 서비스를 호출하지 않음 (only 리뷰)
- `v2` : `ratings` 서비스를 호출
- `v3` : `ratings` 서비스를 호출 + 별의 색깔이 빨간색

Istio를 사용하지 않고 서비스를 배치한다면 다음과 같은 구조일 것입니다.  

![image](https://user-images.githubusercontent.com/15958325/71655230-3f07f400-2d79-11ea-866a-b497ca90c4b8.png)  

Istio를 사용한 구조는 다음과 같습니다. **application을 수정하지 않고** envoy proxy만 sidecar로 각 서비스에 삽입된 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/71655801-04538b00-2d7c-11ea-8a1c-2463f6f4e31b.png)  

## Prerequisites

먼저 쿠버네티스 클러스터를 생성해주세요.  

참고링크 : [호롤리한하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/container/k8s-install/)  

> 본 실습에서 사용한 spec :   
>`OS : CentOS v7.6`  
>`Arch : x86` 
>
>`Master` : 4cpu, ram16G (1개)  
>`Node` : 2cpu, ram4G (2개) 

## Install Istio

~~~sh
$ curl -L https://git.io/getLatestIstio | sh -
$ cd istio-1.4.2/
~~~

~~~sh
# Istio CRD 설치
$ for i in install/kubernetes/helm/istio-init/files/crd*yaml; do kubectl apply -f $i; done
~~~

Istio namespace를 생성하고 적용해줍니다.  
~~~sh
$ vim namespace.yaml
~~~
~~~yaml
apiVersion: v1
kind: Namespace
metadata:
 name: istio-system
 labels:
   istio-injection: disabled
~~~
~~~sh
$ kubectl apply -f namespace.yaml
~~~

그다음 세부사항을 설정해주고 istio를 k8s 클러스터 위에 올립니다.  
~~~sh
$ helm template \
--namespace istio-system \
--set tracing.enabled=true \
--set global.mtls.enabled=true \
--set grafana.enabled=true \
--set kiali.enabled=true \
--set servicegraph.enabled=true \
install/kubernetes/helm/istio \
> ./istioFex.yaml

$ kubectl apply -f istioFex.yaml
~~~

~~~sh
$ kubectl get pod --namespace=istio-system
~~~
![image](https://user-images.githubusercontent.com/15958325/71656378-4c73ad00-2d7e-11ea-8887-910ed7eeb8fa.png)  

pod들의 상태가 모두 Running또는 Complete라면 성공입니다.  

## Sidecar injection 기능 활성화
Istio는 Pod에 envoy proxy를 sidecar 패턴으로 삽입하여, 트래픽을 컨트롤 하는 구조입니다.  

Istio는 sidecar를 Pod 생성시 자동으로 주입 (inject)하는 기능이 있는데, 이 기능을 활성화 하기 위해서는 쿠버네티스의 해당 네임스페이스에 istio-injection=enabled 라는 라벨을 추가해야 합니다.  

application 서비스들은 `default namespace`로 올릴 예정이니 해당 namespace에 라벨을 추가해줍니다.  
~~~sh
$ kubectl label namespace default istio-injection=enabled

$ kubectl get ns --show-labels
~~~
![image](https://user-images.githubusercontent.com/15958325/71656550-e9364a80-2d7e-11ea-88e1-050715bd5ddc.png)  

## Application 배치

~~~sh
$ kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
~~~

~~~sh
$ kubectl get pod
$ kubectl get svc
~~~
![image](https://user-images.githubusercontent.com/15958325/71656597-2bf82280-2d7f-11ea-8134-86a6ed7ef51d.png)   

![image](https://user-images.githubusercontent.com/15958325/71656601-2e5a7c80-2d7f-11ea-9a09-507c345c2e79.png)  

## Istio Gateway
서비스가 전부 ClusterIP로 외부에 노출되어있지 않습니다.  

쿠버네티스의 서비스나 Ingress를 이용하지않고 `Istio Gateway`를 이용해 `Load Balancer`형태로 서비스를 노출시킬 수 있습니다.  

게이트웨이는 다음 명령어를 통해 실행시킬 수 있습니다.  
~~~sh
$ kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml
~~~

yaml파일을 자세히 보면 :   
~~~yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
# gateway를 통해 트래픽을 받을 서비스를 Virtual service 로 정의
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: bookinfo
spec:
  hosts:
  - "*"
  # bookinfo-gateway로 들어오는 트래픽은 모두 다음 라우팅 룰을 따른다.
  gateways:
  - bookinfo-gateway
  # 이 밑으로 라우팅 룰 정의
  http:
  - match:
    - uri:
        exact: /productpage
    - uri:
        prefix: /static
    - uri:
        exact: /login
    - uri:
        exact: /logout
    - uri:
        prefix: /api/v1/products
    # 위의 url들로 접근하면 productpage의 9080포트로 포워딩되어 서비스를 제공하게 된다.
    route:
    - destination:
        host: productpage
        port:
          number: 9080
~~~

~~~sh
$ kubectl get gateway
$ kubectl get svc istio-ingressgateway -n istio-system --show-labels
~~~

![image](https://user-images.githubusercontent.com/15958325/71657263-762ed300-2d82-11ea-95ab-61ce729ed9cd.png)  

![image](https://user-images.githubusercontent.com/15958325/71657264-77600000-2d82-11ea-89dc-764d548ef079.png)  

External-IP로 접근하면 페이지가 뜰 것입니다.  

그런데 제가 올린 gateway는 `<pending>`상태입니다.  
이유는 제 클러스터에서 로드밸런서를 지원하지 않기 때문입니다. (AWS나 Google은 지원한다고 하는데 테스트해보진 않음.)  

이런 경우에는 `ingressgateway`를 `NodePort`로 변경해서 접근하면 됩니다.  

~~~sh
$ kubectl edit svc istio-ingressgateway -n istio-system
~~~

![image](https://user-images.githubusercontent.com/15958325/71657426-21d82300-2d83-11ea-9664-6dc162e4b72e.png)  

ingressgateway를 외부에 노출시키는데 성공했습니다.  
이제 접근해야하는 포트가 뭔지 알아야 할 차례입니다.  
~~~sh
$ kubectl describe svc istio-ingressgateway -n istio-system
~~~
ingressgateway를 잘 살펴보면 http2에 관한 포트 정보가 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/71657550-b5115880-2d83-11ea-8092-25c9a8b26bf7.png)  

위처럼 describe를 통해 포트정보를 빼와도 되고, 다음 명령어로 포트정보만 가져와도 됩니다.  
~~~sh 
$ echo $(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
~~~

웹에서 ip:port/productpage로 이동해보면 다음과 같이 성공적으로 페이지를 보실 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/71657614-ff92d500-2d83-11ea-8eda-86276837e57d.png)  

새로고침을 눌러보면 알겠지만 v1, v2, v3페이지가 랜덤으로 나오는 것을 확인할 수 있습니다.    
라우팅 할 서비스 버전이 명시되어있지 않으면, Istio는 모든 버전을 라운드 로빈 방식으로 라우팅하기 때문입니다.   

## Apply default destination rules
Istio를 사용하여 Bookinfo 버전 라우팅을 제어하려면 subset이라고 하는 **사용가능 버전**을 정의해줘야합니다.  

~~~sh
# mutual TLS를 활성화하지 않은 경우
$ kubectl apply -f samples/bookinfo/networking/destination-rule-all.yaml

# mutual TLS를 활성화시킨경우
$ kubectl apply -f samples/bookinfo/networking/destination-rule-all-mtls.yaml
~~~

저는 후자로 했습니다.  

그럼 이제 yaml파일을 뜯어봅시다.  
~~~yaml
# destination-rule-all-mtls.yaml

# productpage에는 사용할 수 있는 버전이 v1버전뿐입니다.
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: productpage
spec:
  host: productpage
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
  subsets:
  - name: v1
    labels:
      version: v1
---
# Reviews서비스에는 세가지 버전이 있습니다.
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  - name: v3
    labels:
      version: v3
...(생략)
~~~

## Virtual service
라운드로빈형식으로 돌아가는 버전을 하나로 고정시키려면,   
Virtual Service를 만들어 라우팅 규칙을 정의해야 합니다.  

새로고침할때마다 바뀌는 버전을 v1로 고정시켜보도록 하겠습니다.  
~~~sh
$ kubectl apply -f samples/bookinfo/networking/virtual-service-all-v1.yaml
~~~

yaml파일은 다음과 같습니다. 모든 호스트페이지에 subset을 지정시켜 고정된 페이지가 나오도록 규칙을 정의해주었습니다.  

~~~yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: productpage
spec:
  hosts:
  - productpage
  http:
  - route:
    - destination:
        host: productpage
        subset: v1
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ratings
spec:
  hosts:
  - ratings
  http:
  - route:
    - destination:
        host: ratings
        subset: v1
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: details
spec:
  hosts:
  - details
  http:
  - route:
    - destination:
        host: details
        subset: v1
---
~~~

이제 아무리 새로고침을 해도 v1버전의 페이지만 뜨는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/71661001-20612780-2d90-11ea-8e90-b09f73779813.png)  

이처럼 Virtual Service를 사용하게 되면 하나 이상의 호스트 이름에 대한 트래픽 동작을 지정할 수 있습니다.  

또한 동일한 이름의 서비스의 다른버전일수도 있고, 아예 다른 서비스로 라우트시킬수도 있습니다.  

## Route based on user identity
그럼 이번엔 사용자 신원에 따라 라우트시키는 방법을 알아보겠습니다.  

~~~sh
$ kubectl apply -f samples/bookinfo/networking/virtual-service-reviews-test-v2.yaml
~~~

~~~yaml
# virtual-service-reviews-test-v2.yaml

apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
    - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
~~~
end-user가 jason인 경우, reviews페이지는 v2 버전을 띄우라는 줄을 추가하였습니다.  

한번 적용시킨뒤에 웹페이지로가서 jason으로 로그인해보면,  
![image](https://user-images.githubusercontent.com/15958325/71661317-302d3b80-2d91-11ea-95bc-3a811af2b8d2.png)  

v1만 띄웠던 reviews페이지가 v2버전으로 바뀌는 것을 확인할 수 있습니다.   
![image](https://user-images.githubusercontent.com/15958325/71661381-5521ae80-2d91-11ea-879d-9f692cd78a41.png)  



----

