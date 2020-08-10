---
title: "Kubernetes Monitoring with Sysdig"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Kubernetes
  - Monitoring
last_modified_at: 2020-08-10T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
![image](https://user-images.githubusercontent.com/15958325/89750239-13ff3300-db06-11ea-816c-9b12a9a88d91.png)  

이번 포스팅에서는 sysdig 플랫폼은 무엇인지, 무료로 sysdig monitoring을 테스트할 수 있는 방법에 대해서 말씀드리겠습니다.  

> Sysdig : [sysdig.com](https://sysdig.com/)

# Sysdig?

> "Ship cloud apps faster by embedding security, compliance, and performance into your DevOps workflow"  

Sysdig를 한 문장으로 말하자면 기업용 보안 모니터링 플랫폼입니다.  

원래는 리눅스와 같은 **시스템에서 발생하는 이벤트에 대한 감시도구**입니다. 네트워크, 디스크 I/O, 에러 등 다양한 메트릭에 대한 필터링이 가능하고 시스템로그에 기록되지 않는 행위도 기록이 되기 때문에 포렌식에 많이 사용되고 있습니다.  

최근 클라우드시장이 커지면서 기존 워크플로우에 준하는 보안과 가시성이 중요해졌습니다. 이러한 흐름에 맞춰서 Sysdig에서도 Kubernetes, Openshift, Mesos와 같은 Container Orchestration툴을 위한 도커 모니터링, 관련 메트릭 수집 등의 기능을 제공하고 있습니다.    
또한, 컨테이너 이미지를 스캔하거나 비정상적인 트래픽, 또는 행위를 발견하는 등의 기능도 제공을 하고 있습니다.  

모니터링과 보안, 두가지 키워드를 통해 궁극적으로 **Secure DevOps**환경을 지향하고 있습니다.   

앞에서 언급한 바와 같이 `Sysdig Platform`에서는 크게 `Sysdig Monitoring`과 `Sysdig Secure` 두가지 application을 지원하고 있습니다.  

둘 다 매력있는 토픽이긴하지만 이번 문서에서는 **Sysdig Monitoring**에 대해서만 다루려고 합니다.  
추후에 기회가 되면 Sysdig Secure도 한번 다뤄보고 싶네요.  

## Sysdig Monitoring
Sysdig Monitoring에서는 시스템의 상태 및 성능을 모니터링하고 관리할 수 있습니다.  
Native Linux, 도커, 쿠버네티스를 포함한 컨테이너 오케스트레이션 툴 들까지 모니터링이 가능합니다.  

주요 기능으로는 :   
- **Full-Stack Monitoring** : 전체 시스템 환경을 스캔하여 응답시간, 애플리케이션 성능, 네트워크, 컨테이너 등의 메트릭을 보거나 쿼리할 수 있음  
- **Prometheus Compatibility** : sysdig는 Prometheus의 메트릭이나 라벨들을 저장하고 쿼리 가능. 따라서 유저는 Prometheus와 같은 방식으로 sysdig를 사용할 수 있음
- **Topology Maps** : 인프라 및 서비스를 토폴로지 맵으로 시각화 가능. 트래픽 흐름을 파악해 병목현상을 시각적으로 식별 가능
- **Dashboards** : sysdig API, PromQL 둘 다 사용 가능. 깔끔한 UI
- **Adaptive Alerts** : 사용자가 설정한 정책에 따라 해당 이벤트가 발생하면 알람을 보내주는 기능

## [참고] Sysdig vs Prometheus
공부를 하다보니 `sysdig`와 `prometheus`의 차이점이 궁금해졌습니다. 둘 다 모니터링 툴인데, 대체 무엇이 다른가...  
그래서 이 포스팅에도 짤막하게 정리를 해두려고 합니다.  

> 참고한 링크들:   
> - [Prometheus vs Sysdig](https://stackshare.io/stackups/prometheus-vs-sysdig)  
> - [Container Monitoring: Prometheus and Grafana Vs. Sysdig and Sysdig Monitor](https://caylent.com/container-monitoring-prometheus-vs-sysdig)  
> - [Prometheus monitoring and Sysdig Monitor: A technical comparison](https://sysdig.com/blog/prometheus-monitoring-and-sysdig-monitor-a-technical-comparison/)

**Prometheus**는 SoundCloud에서 시계열 데이터베이스 프로젝트로 시작했고, 다차원 메트릭을 위한 다양한 도구를 제공하는 오픈소스 모니터링 솔루션입니다.  
- 오픈소스(무료)
- 분산스토리지에 의존하지 않음
- Pull 기반 접근방식
- 활발한 커뮤니티

**Sysdig**도 오픈소스로 시작하긴 했지만([Sysdig-Inspect](https://github.com/draios/sysdig-inspect)) 컨테이너화 된 시스템의 모니터링, Docker와 Kubernetes환경에 초점을 맞춰 `Sysdig Monitoring`를 개발하였습니다.  
- 상용솔루션(유료)
- Docker, K8s, Mesos 등 모든 리눅스 기술에 대한 지원
- Docker 및 K8s 이벤트 로그를 포함한 모든 유형에 대한 메트릭 수집


Sysdig는 설정하는게 Prometheus보다는 훨씬 쉽고, Prometheus는 Sysdig정도의 대시보드를 꾸미려면 자체 UI로는 부족하고, Grafana와 같은 3rd party툴들을 사용해야합니다.    
또한 Sysdig는 상업용솔루션이기 때문에 비용이 발생하지만 질좋은 지원을 받을 수 있고, Prometheus는 오픈소스라서 개발자 혼자 해야하지만 커뮤니티가 잘 구성되어 있어서 유료지원에 버금가는 도움을 받을 수도 있을겁니다.  


# Sysdig Monitoring 실습!
비교는 이정도로 마치고, 지금부터는 Sysdig 실습을 진행하겠습니다.  

이번 실습에서는 직접 Sysdig Monitoring을 구축하지 않고 클라우드 서비스로 사용할 예정입니다.  

> [참고]    
>![image](https://user-images.githubusercontent.com/15958325/89763294-30629600-db2d-11ea-8a11-76f5111c60c4.png)  
> [공식홈페이지](https://sysdig.com/)로 가면 30일 무료 트라이얼이 있긴 합니다.  

![그림2](https://user-images.githubusercontent.com/15958325/89764197-f1354480-db2e-11ea-9960-b0faeb45d06c.png)  


