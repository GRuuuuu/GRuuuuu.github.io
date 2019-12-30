---
title: "envoy proxy란? (basic)"
categories: 
  - Container
tags:
  - Container
  - MSA
  - ServiceMesh
  - Envoy
  - Proxy
  - Istio
last_modified_at: 2019-12-26T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
MSA시장이 커지면서 서비스들은 네트워크를 통해 서로 통신해야했고, 이러한 서비스에서 사용하는 핵심 네트워크 프로토콜은 `HTTP`, `HTTP/2`, `gRPC`, `Kafka`, `MongoDB`등의 L7프로토콜입니다.   

L3,L4기반의 프록시들로는 다양한 요건들을 처리하기 어려워졌고, 그에 따라 **L7기능을 갖춘 프록시**의 필요성이 부각되기 시작했습니다.  

이번 포스팅에서는 추후에 기술할 `ServiceMesh Architecture`로 대표되는 `Istio`의 메인 프록시인 `Envoy Proxy`에 대해서 기술하겠습니다.  

> 참고 링크 : [Envoy doc](https://www.envoyproxy.io/docs/envoy/latest/about_docs)

# 1. What is Envoy
**Lift**사에서 제작한 프로젝트로, **Cloud Native Computing Foundation**(CNCF)의 세번째 Graduated Project입니다.  

>참고링크 : [CNCF projects](https://www.cncf.io/projects/)  
>
>![image](https://user-images.githubusercontent.com/15958325/71460574-be347f80-27ef-11ea-8c06-8ace99911ea8.png)  

대형 MSA의 단일 Application과 Service를 위해 설계된 고성능 분산 c++프록시입니다. 

다음 목적을 지니고 태어난 프로젝트이며,  
>"The network should be transparent to applications. When network and application problems do occur it should be easy to determine the source of the problem."   
>
>네트워크는 애플리케이션에 **투명**해야하며, 장애가 발생했을시 **어디에서 문제가 발생했는지 쉽게 파악**할 수 있어야 한다.  

**디자인 목표**는 다음과 같습니다.  
- 모듈화가 잘되어있으며 테스트하기 쉽게 쓰여짐  
- 플랫폼에 구애받지 않는 방식으로 기능을 제공하여 네트워크를 추상화
- L7단이기때문에 L4보다는 성능 감소가 다소 존재하지만 가능한 최고 성능을 목표로 함

>**Background++**  
>
> 출처 : [HTTP Request Latency Test Results](https://www.twilio.com/blog/2017/10/http2-issues.html)  
>
>실제로 HAproxy에 비해 다소의 성능감소가 있다고 합니다.
>![image](https://user-images.githubusercontent.com/15958325/71462720-90533900-27f7-11ea-868b-0dcfcbeb5b49.png)  


# 2. Features
Envoy proxy의 주요 기능들을 알아보겠습니다.  

### Out of process architecture
Envoy proxy는 그 자체로 메모리사용량이 적은 고성능의 서버입니다.  
모든 프로그래밍 언어, 프레임워크와 함께 실행될 수 있습니다.

이는 다양한 언어,프레임워크를 함께 사용하는 Architecture에 유용히 사용될 수 있습니다.  

### L3/L4 Architecture
Envoy의 주요 기능은 L7이지만 핵심은 L3/L4 네트워크 프록시 입니다.  
TCP프록시, HTTP프록시, TLS인증과 같은 다양한 작업을 지원합니다.  

### L7 Architecture
버퍼링, 속도제한, 라우팅/전달 등과 같은 다양한 작업을 수행할 수 있게 합니다.

### HTTP/2 , gRPC 지원
HTTP/1.1은 물론 HTTP/2도 지원합니다.  
이는 HTTP/1.1과 HTTP/2 클라이언트와 서버간 모든 조합을 연결할 수 있음을 의미합니다.  

권장하는 구조는 모든 Envoy간에 HTTP/2를 사용하는 것입니다.  

또한 gRPC를 지원하여 HTTP/2기능을 보완할 수 있습니다.  

>참고 : [나만 모르고 있던 - HTTP/2](https://www.popit.kr/%EB%82%98%EB%A7%8C-%EB%AA%A8%EB%A5%B4%EA%B3%A0-%EC%9E%88%EB%8D%98-http2/)

### Advanced Load Balancing
자동 재시도, circuit break, 외부 속도 제한 서비스를 통한 글로벌 속도제한, 이상치 탐지 등의 기능을 제공합니다.  

> **circuit break?**  
> 전기의 회로차단기에서 차용한 개념으로,   
> 평소에는 정상적으로 동작하다가 오류가 발생하면 더이상 동작하지 않게 합니다.  
> 이렇게 문제가 되는 기능 자체를 동작하지 않게하여 리소스 무한 점유를 막을 수 있습니다.  
>
>![image](https://user-images.githubusercontent.com/15958325/71466724-c4ccf200-2803-11ea-8ffb-e63b6fc703c6.png)  
>

### Etc
- health check 지원
- 프론트/엣지 프록시 지원
- 관리용으로 다양한 통계 정보 제공
- MongoDB, DynamoDB L7을 지원


# 3. 실습
그럼 Envoy proxy를 직접 실행시켜보겠습니다.  

~~~sh
$ docker pull envoyproxy/envoy-dev:f08b17516026882a0964a225c0135dc996b964af
$ docker run --rm -d -p 10000:10000 envoyproxy/envoy-dev:f08b17516026882a0964a225c0135dc996b964af
$ curl -v localhost:10000
~~~

![image](https://user-images.githubusercontent.com/15958325/71495664-6ef35b00-2892-11ea-8fd8-de526dbdd72b.png)  

envoy proxy 컨테이너를 실행시킨다음에, 웹브라우저에서 `localhost:10000`으로 접속해보면 google페이지가 뜨는것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/71495997-0c9b5a00-2894-11ea-8810-3004c8984c5e.png)  

어떻게 구글 홈페이지로 리다이렉트가 되는지 Envoy proxy의 설정파일을 보면서 알아보겠습니다.  

## Simple Configuration

>**Background++**  
>-용어정리-
>- **Downstream** : <u>Envoy에게</u> request를 보내고 response를 받는 host  
>- **Upstream** : <u>Envoy로부터</u> request를 받고 response를 보내주는 host
>- **Listener** : Downstream 호스트의 요청을 받는 부분
>- **Cluster** : upstream호스트의 그룹. 

envoy proxy 컨테이너 내부로 들어가서 config파일을 열어봅시다.  

~~~sh
$ docker exec -it f7081a24f81a /bin/bash
root@f7081a24f81a:/# 

$ cat /etc/envoy/envoy.yaml
~~~

administration server 설정
~~~yaml
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      protocol: TCP
      address: 127.0.0.1
      port_value: 9901
~~~


static_resources는 Envoy가 실행될 때 정적으로 정해지는 리소스들입니다.  
~~~yaml
static_resources:
~~~

downstream host의 요청을 처리해주는 listener의 설정 부분입니다.  
10000번 포트로 접근했을때의 처리를 담고 있습니다.  
filter_chains파트에 filter들을 연속해서 정의하는데, `http_connection_manager`를 이용하여 모든 트래픽을 `service_google`이라는 클러스터로 라우팅 하도록 설정하고있습니다.  
~~~yaml
  listeners:
  - name: listener_0
    address:
      socket_address:
        protocol: TCP
        address: 0.0.0.0
        port_value: 10000
    filter_chains:
    - filters:
      - name: envoy.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.config.filter.network.http_connection_manager.v2.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: local_service
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                route:
                  host_rewrite: www.google.com
                  cluster: service_google
          http_filters:
          - name: envoy.router
  ~~~

Envoy에서 요청하는 upstream host의 정보를 담고있습니다.  
  ~~~yaml
  clusters:
  - name: service_google
    connect_timeout: 0.25s
    type: LOGICAL_DNS
    # Comment out the following line to test on v6 networks
    dns_lookup_family: V4_ONLY
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: service_google
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: www.google.com
                port_value: 443
    transport_socket:
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.api.v2.auth.UpstreamTlsContext
        sni: www.google.com
~~~


## Using the Envoy Docker Image
한번 config파일을 수정해서 google로 연결되는게 아니라 제 블로그로 리다이렉트되도록 해보겠습니다.  

static resource들이기 때문에 방금전에 올렸던 Envoy proxy를 내리고 설정파일부터 수정해보겠습니다.  

~~~sh
$ docker kill {container id}
$ vim envoy.yaml
~~~

~~~yaml
...
  listeners:
  - name: listener_0
    address:
      socket_address:
        protocol: TCP
        address: 0.0.0.0
        port_value: 10001
...
              routes:
              - match:
                  prefix: "/about"
                route:
                  host_rewrite: gruuuuu.github.io
                  cluster: service_google
          http_filters:
          - name: envoy.router
  clusters:
...
        - endpoint:
            address:
              socket_address:
                address: gruuuuu.github.io
                port_value: 443
...
~~~

~~~sh
$ docker build -t envoy:v1 .
$ docker run -d --name envoy -p 9901:9901 -p 10001:10001 envoy:v1
~~~

![image](https://user-images.githubusercontent.com/15958325/71508264-877f6780-28ca-11ea-8941-263d25887386.png)


웹을 켜서 ip:port/path로 접속해보면 처음에는 ip가 떳다가 gruuuuu.github.io주소로 바뀌는것을 확인할 수 있습니다.(`host_rewrite`)  
![image](https://user-images.githubusercontent.com/15958325/71510705-198b6e00-28d3-11ea-9a2e-f861da5a5b07.png)  
  
  
----
