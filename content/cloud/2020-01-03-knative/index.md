---
title: "Knative란? (basic)"
slug: knative
tags:
  - Container
  - Cloud
  - MSA
  - ServiceMesh
  - Istio
date: 2020-01-10T13:00:00+09:00
---

## 1. Overview
오픈소스 서버리스 솔루션인 `Knative`에 대해서 알아보겠습니다.  

> K-native라고 읽습니다.

# 1. Serverless? (FaaS)
`Knative`가 무엇인지 알아보기 전에, **Serverless**라는 단어를 짚고 넘어갈 필요가 있습니다.  

Serverless Architecture란 단어그대로 서버가 필요없는 구조를 뜻합니다.  
하지만 실제로 서버가 존재하지 않는다는 것은 아니고, 개발자나 관리자가 **서버인프라에 대해 신경쓰지 않아도 된다는** 뜻입니다.  

이러한 구조 하에서는 **요청이 있을때만 필요한 코드를 실행**하고, 요청이 많을 경우에는 그에 비례하는 자원을 할당하여 동시에 처리하는 방법으로 **사용률과 확장성을 극대화**할 수 있습니다.  

>참고 : [호롤리한하루/Serverless Image Recognition with Cloud Functions](https://gruuuuu.github.io/simple-tutorial/visual-recog-with-cloudFn/#4-basic-concepts)  

### 장점
- 함수가 호출된 만큼만 비용이 청구, 비용절약
- 인프라 관리 필요없음

### 단점
- 각 함수에서 사용할 수 있는 **자원이 제한됨** 
    - 계속 켜둬야 하는 웹소켓같은 경우 사용불가
- 벤더에 강한 의존성을 가짐 
    - `AWS Lambda`
    - `Azure Functions`
    - `Google Cloud Functions`
    - `IBM Cloud Functions`
- 로컬 데이터 사용 불가능
    - stateless
    - 클라우드 스토리지 사용해야함

# 2. Knative
## Background
위 서버리스 솔루션들은 특정 클라우드 플랫폼에 **의존성**을 가지고 있습니다. 이를 해결하기 위해 나온 **오픈소스 서버리스 솔루션**이 `Knative`입니다.  

## 특징
- **Kubernetes** 위에서 기동
- 특정 클라우드 종속성이 없음
- `On-Premise`에서도 설치가능

>지원하는 클라우드 목록 : [knative/Installing Knative](https://knative.dev/docs/install/)


## 기능
![image](https://user-images.githubusercontent.com/15958325/71711867-42b57c80-2e46-11ea-8bb6-4aac375151fd.png)  
stateless app뿐만아니라 이벤트를 받아 처리하는 이벤트 핸들링을 위한 모델제공, 컨테이너를 빌드할 수 있는 기능을 제공합니다.  

크게 두가지 Component로 나뉘며 다음과 같습니다.  

## Serving
Knative Serving은 serverless application이나 function들을 배포하고 서빙하는 역할을 합니다.  

- Serverless 컨테이너의 빠른 배포
- 자동 scale up & down
- `Istio`기반 라우팅 & 네트워크 프로그래밍
- 배포된 코드와 config의 스냅샷기능

Serving 은 쿠버네티스 CRD (Custom Resource Definition)으로 정의된 4개의 오브젝트로 구성되어 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/71712412-742f4780-2e48-11ea-9882-4173d7ea9c59.png)  

- **Service** : `Configuration`과 `Route` 리소스의 추상화된 집합체입니다. 워크로드의 lifecycle을 관리하는 역할을 합니다.  
- **Configuration** : Serving으로 배포되는 서비스를 정의합니다. 컨테이너 경로, 환경변수 등의 설정을 정의할 수 있으며 컨테이너의 경로를 지정할 때 빌드버전도 지정할 수 있습니다.
- **Revision** : 코드와 config의 스냅샷입니다. `Configuration`을 생성할때마다 새로운 revision이 생기며 이전 revision으로 롤백하거나 각각의 버전으로 트래픽을 분할하여 서빙할 수 있습니다.  
- **Route** : `User Service`의 네트워크 엔드포인트를 제공합니다. 하나 이상의 `Revision`을 가지며 서비스로 들어오는 트래픽을 Revision으로 라우팅할 수 있습니다. 단순히 최신 버전의 Revision으로 라우팅할수도 있지만 카날리 테스트와 같이 여러 Revision으로 라우팅할수도 있습니다.  


## Eventing
또다른 Component인 Knative Eventing은 비동기 메시지 처리를 위한 모듈입니다.  

메시지 큐와 같은 이벤트 발생 자원들은 Knative에 event source에 등록되고 해당 이벤트가 발생되면 지정된 knative 서비스로 이벤트 메시지를 전송하는 루틴으로 동작하게 됩니다.  

이 때, 이벤트의 스펙은 `CNCF Serverless WG`에서 정의한 [CloudEvent](https://github.com/cloudevents/spec/blob/master/spec.md#design-goals) 스펙을 기반으로 합니다.  

`v0.5`이상부터 이벤트 broker & trigger 오브젝트를 지원해 이벤트를 보다 쉽게 필터링할 수 있게 합니다.   
![image](https://user-images.githubusercontent.com/15958325/71712448-9aed7e00-2e48-11ea-8809-db68f914d3a8.png)   
- `broker` : 이벤트 소스로부터 메시지를 받아 저장하는 버킷역할
- `trigger` : 특정 메시지 패턴만 서비스로 보낼 수 있게 하는 조건역할
- `subscriber` : 이벤트를 수신하여 처리하는 객체

>20.1.7 기록..  
>Event Channel이 이해가 안된다,,, 나중에 공부할것  
>[https://knative.dev/docs/eventing/](https://knative.dev/docs/eventing/)

### Source
Event Source는 이벤트가 발생하면 Knative서비스로 이벤트메시지를 송신하는 역할을 해줍니다.  

사용가능한 EventSource의 리스트는 아래 링크를 참고 :   
[Knative Eventing sources](https://knative.dev/docs/eventing/sources/index.html)  


- `KubernetesEventSource` : [Kubernetes이벤트](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.12/#event-v1-core)가 생성될 때 마다 이벤트메시지를 발생시킴.
- `GitHubSource` : create, delete, deploy, fork 등과 같은 [GitHub이벤트](https://developer.github.com/v3/activity/events/types/)가 생성될 때마다 이벤트메시지 발생시킴.

그 외에도 GitLab, BitBucket, Apache CouchDB등이 있습니다.  

>**Background++**
>  
>원래는 Build도 component에 있었지만, `Knative v0.8` 부터 **Deprecated**되었습니다.  
>이유는 [여기](https://github.com/knative/build/issues/614)나와있지만 간단히 기술하자면 build가 Knative의 핵심책임이 아니라는 것입니다.  
>대신 **Tekton Pipelines**라는 툴을 사용하는 것을 권장하고 있습니다.  
>궁금해서 찾아봤는데 홈페이지가 공사중이더군요.(20.1.7 기준)  
>나중에 시간날때 한번 건들여봐야겠습니다.  
>`github` : [https://github.com/tektoncd/pipeline](https://github.com/tektoncd/pipeline)  
>`Doc` : [https://tekton.dev/](https://tekton.dev/)
>![image](https://user-images.githubusercontent.com/15958325/71869137-4ef64e00-3154-11ea-9202-d18301f7b9a0.png)

## 한줄 정리

`Serverless` : Request가 있을 때만 실행되기 때문에 사용률과 확장성의 효율성이 뛰어남.  
`Knative` : opensource serveless solution  
`Serving` : 서비스를 배포하며 서비스 네트워크 설정을 알아서 해줌    
`Eventing` : Knative의 비동기 메세지 처리 모듈    

----