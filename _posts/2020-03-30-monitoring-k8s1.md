---
title: "Kubernetes Monitoring - Concept, Architecture"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Kubernetes
  - Monitoring
last_modified_at: 2020-03-31T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Kubernetes의 Monitoring 개념과 아키텍처에 대해서 기술하겠습니다.  

> **참고 링크들**   
> 1. [아리수/쿠버네티스 모니터링 아키텍처(kubernetes monitoring architecture)](https://arisu1000.tistory.com/27855)  
> 2. [조대협의블로그/쿠버네티스 #13 - 모니터링 (1/2)](https://bcho.tistory.com/1269)  
> 3. [Kubernetes Community/Kubernetes monitoring architecture](https://github.com/kubernetes/community/blob/master/contributors/design-proposals/instrumentation/monitoring_architecture.md#architecture)  
> 4. [alice/167. [Kubernetes] 쿠버네티스 모니터링 : Prometheus Adapter와 Opencensus를 이용한 Custom Metrics 수집 및 HPA 적용](https://blog.naver.com/alice_k106/221521978267)


# Monitoring Concept
우선 쿠버네티스 클러스터에서 데이터를 수집할 수 있는 오브젝트는 크게 4가지 계층으로 볼 수 있습니다.  

<img src="https://user-images.githubusercontent.com/15958325/77883361-effd2c80-729d-11ea-83b1-f80866a40a3a.png" width="400px">    


1. **Host** : 노드의 cpu, 메모리, 디스크, 네트워크, 사용량과 노드 os와 커널에 대한 모니터링

2. **Container** : 노드에 기동되는  각각의 컨테이너에 대한 정보. 컨테이너의 CPU,메모리, 디스크, 네트워크 사용량을 모두 모니터링

3. **Application** : 컨테이너에서 구동되는 개별 어플리케이션에 대한 모니터링.  ex)  컨테이너에서 기동되는 node.js기반의 애플리케이션의 http 에러 빈도등

4. **Kubernetes** : 컨테이너를 컨트롤 하는 쿠버네티스 자체에 대한 모니터링 (쿠버네티스의 자원인 서비스나 POD, 계정 정보등이 이에 해당)

개념적으로는 이렇게 나눌 수 있고 쿠버네티스 공식문서에서는 이를 수집지표, 즉 **Metric**이라고 부릅니다.  

## Metrics
쿠버네티스에서는 수집지표를 두가지로 나눠서 설명하고 있습니다.  

1. **System metrics** : 노드나 컨테이너의 cpu, 메모리 사용량 같은 일반적인 시스템 관련 메트릭.  
    - `core metric` : 쿠버네티스의 내부 컴포넌트들이 사용하는 메트릭. (kubectl top에서 사용하는 메트릭 값.)  
    - `non-core metric`은 쿠버네티스가 직접 사용하지 않는 다른 시스템 메트릭을 의미
2. **Service metrics** : application을 모니터링 하는데 필요한 메트릭. 
    - 쿠버네티스 인프라컨테이너에서 나오는 메트릭은 클러스터를 관리할 때 참고해서 사용
    - 사용자 application에서 나오는 메트릭은 서비스 관련 정보를 파악할 수 있음 (ex, 웹서버의 응답속도, 500error의 빈도 등)

## Pipeline
그리고 이러한 수집지표들을 수집하는 pipeline을 두 종류로 나눠서 설명하고 있습니다.  

1. **Resource metric pipeline** : 핵심 요소들에 대한 모니터링 (kubelet, metrics-server, metricAPI등으로 구성). 
    - 스케줄러나 HPA등의 기초자료로 활용
2. **Full metric pipeline** : 클러스터의 사용자들이 필요한 모니터링을 하는데 활용.
    - 쿠버네티스가 관리하지 않고, 외부 모니터링 시스템을 연계해서 이용하는 것을 권장
    - 시스템, 서비스 메트릭 둘 다 수집 가능

> **Background++**  
> HPA(Horizontal Pod Autoscaler) : 시스템의 부하 여부에 따라 pod을 자동으로 scale out 시켜주는 컨트롤러


# Monitoring Architecture
지금부터는 위에서 언급한 두개의 파이프라인 아키텍처에대해서 알아보겠습니다.  

## 1. Resource Metric Pipeline Architecture
아래 그림은 **Resource metric pipeline**을 통해 HPA를 하는 도식도입니다.  
**HPA**는 시스템의 부하여부에 따라 pod을 scale-out시켜주는 모듈 이고, HPA를 하려면 시스템의 부하여부를 파악해야 합니다.  

시스템의 부하여부는 여러 메트릭들을 참고할 수 있겠지만 기본적으로는 시스템메트릭(cpu나 메모리사용량)을 모니터링하게됩니다.  

**쿠버네티스에서는 이러한 시스템메트릭을 기본적으로 제공**하고 있습니다.  
Kubernetes node의 `kubelet`에는 `cAdvisor`라는 모니터링 에이전트가 탑재되어있어 노드에 대한 정보와 컨테이너(pod)에 대한 지표를 수집하고 있습니다.  

그럼 해당 메트릭들을 가져오기만 하면 뚝딱 해치울수있습니다.

이 때 메트릭들을 가져오는 역할을 하는게 쿠버네티스 애드온 컴포넌트인 `Metrics-Server`입니다.  

![그림1](https://user-images.githubusercontent.com/15958325/77894469-483d2a00-72b0-11ea-8aaf-dc8a8bcb07fc.png)  

1. `cAdvisor`에서 지표수집 -> `kubelet`으로 전송
2. `Metrics-Server`에서는 해당 metric들을 사용하기 위한 커스텀 api를 `k8s Aggregator`를 통해 API server에 등록
3. 등록된 metrics api를 통해 수집된 `system metric`들이 `HPA`로 전송
4. 설정한 값에 따라 HPA에서는 controller에 명령을 내림
5. 명령을 받은 컨트롤러에서 pod을 scale-out 시킴

이 다음 포스팅에서 진행할 HPA실습을 해보시면 이해가 더 잘될거라 생각합니다.  

## 2. Full Metric Pipeline Architecture
두번째는 **Full Metric Pipeline**의 Architecture입니다.  

이 파이프라인의 가장 큰 특징은 사용자들이 필요한 리소스의 모니터링을 할 수 있다는 것입니다.  
즉, **system과 service metric모두 수집이 가능하고 사용자가 원하는대로 모니터링을 할 수 있다**는 것입니다.  

[Kubernetes Community](https://github.com/kubernetes/community/blob/master/contributors/design-proposals/instrumentation/monitoring_architecture.md#architecture)에 올라온 Full metric pipeline Architecture는 다음과 같습니다.  

![image](https://user-images.githubusercontent.com/15958325/77896505-60627880-72b3-11ea-98dd-ae6e878067ff.png)  

얼핏보면 복잡한데 파랑색에만 집중하시면 됩니다.  
1. 일단 system metric처럼 service metric은 기본제공 metric이 아니니 **metric을 수집하는 에이전트**를 둬야함
2. 수집한 metric을 모니터링시스템으로 전송
3. 전송된 metric(system+service)은 Dashboard로 확인 또는 HPA로 보내 커스텀부하측정을 가능하게 함

예전에는 `cAdvisor` + `Heapster` + `InfluxDB`의 조합이 대세였지만 Heapster가 Kubernetes에서 deprecated되면서 `Prometheus`를 많이 사용하는 추세입니다.  

해당 포스팅에서는 **Prometheus**를 기준으로 설명을 드리겠습니다.  

## Prometheus
프로메테우스는 시계열 데이터를 저장할 수 있는 다차원 데이터모델 구조를 지니고 있으며 CNCF의 두번째 졸업프로젝트입니다.  

타 모니터링 프로그램과 다른 점은 데이터를 pull 방식으로 수집한다는 것입니다.  
이 말은 모니터링 대상이 되는 자원이 지표 정보를 프로메테우스로 보내는 것이 아니라 프로메테우스가 주기적으로 모니터링 대상에서 지표를 읽어온다는 뜻입니다.  

> push 방식으로 지표를 수집하는 모니터링 툴은 ELK Stack, Telegraf, InfluxDB 등이 있습니다.  

아래 그림은 프로메테우스의 아키텍처를 그린 그림입니다.  

![그림2](https://user-images.githubusercontent.com/15958325/77894475-496e5700-72b0-11ea-9022-ff266bd588fd.png)  

1. **데이터 수집** : 크게 두가지 방식으로 나뉩니다.(pull, push)
    - **pull** : 수집하고자 하는 객체에 설치된 `exporter`를 통해 수집합니다.
    - **push** : 배치성 작업은 필요한 경우에만 떠있다가 사라지기 때문에 pull방식으로 데이터수집이 어렵습니다. 이 경우 `pushgateway`에 지표정보를 push하고 나중에 프로메테우스에서 pushgateway의 데이터를 pull받는 방식으로 수집할 수 있습니다.
2. **수집 타겟** : 서버의 개수가 정적으로 정해져있다면 모니터링 대상을 관리하는데 문제가 없지만, 클라우드환경에서는 ip가 동적으로 변하거나 대상이 늘어나거나 할 수 있기 때문에, 일일히 설정파일에 기재하는건 한계가 있습니다.  
때문에 쿠버네티스의 etcd나 dns와 같은 `Service Discovery`서비스와 연동하여 타겟 리스트를 설정 가능할 수 있습니다.
3. **데이터 저장** : 단순히 로컬 디스크에 저장해도되지만 외부 스토리지에 저장하는 것도 가능합니다.  
쿠버네티스의 `storage class`와 연결해서 쿠버네티스의 `Persistent Volume` 서비스를 이용할 수 있습니다.  
4. **알람** : 프로메테우스에 정의된 특정 규칙에 따라 알람발생조건이 되면 `Slack`, `Email` 등으로 알람내용을 전달할 수 있습니다.  
5. **데이터 시각화** : 프로메테우스에 내장된 웹 UI 또는 `Grafana`와 같은 서드파티 툴을 이용할 수 있습니다.  

다음 포스팅에서 쿠버네티스클러스터를 프로메테우스와 연동해 모니터링할 수 있는 실습을 해보겠습니다.  

----