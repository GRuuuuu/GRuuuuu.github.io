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

이번 실습의 대략적인 구조는 다음과 같습니다.  
![그림1](https://user-images.githubusercontent.com/15958325/89768739-f6968d00-db36-11ea-9a77-82866ac3b262.png)    

Sysdig Monitoring은 IBM Cloud의 클라우드 서비스(Lite버전)로 사용할 것이고, 쿠버네티스 클러스터에 sysdig agent를 deploy해서 메트릭들을 수집해보도록 하겠습니다.  

위 그림은 쿠버네티스 클러스터도 IBM Cloud안에 들어가있는데, 쿠버네티스 클러스터 자체는 어디있든 상관없는것 같습니다.  

## 1. Cluster 준비

쿠버네티스 클러스터를 준비합니다. (싱글노드도 상관없음)  

참고 : [Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)


## 2. Sysdig 서비스 생성

이 문서에서 사용할 sysdig는 IBM Cloud의 sysdig서비스를 받아서 사용할 것이므로 IBM Cloud의 계정이 필요합니다.  

계정생성 : [IBM Cloud](https://cloud.ibm.com/)  

계정을 생성했다면 리소스 검색에서 `sysdig`를 검색해서 인스턴스를 하나 생성해줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/89769789-bb955900-db38-11ea-8fe0-6a1393ab8875.png" width="700px">   

무료로 사용할 것이므로 Lite플랜을 고른 뒤 생성해주시면 됩니다.  

조금 기다리면 sysdig가 새로 생성된 것을 확인할 수 있습니다.  

이제 아래 사진에 빨간 밑줄을 친 "Edit Sources"를 눌러서 인증 정보들을 획득하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/89769946-00b98b00-db39-11ea-9193-595dc54a5ab9.png)   

**Public Endpoint**에서 a파라미터와 c파라미터의 값을 복사하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/89770093-33638380-db39-11ea-94e7-e9e331222b03.png)  

`a`파라미터는 sysdig의 `access key`이고,  
`c`파라미터는 collector의 `endpoint`입니다. ([Sysdig Collector endpoints](https://cloud.ibm.com/docs/Monitoring-with-Sysdig?topic=Monitoring-with-Sysdig-endpoints#endpoints_ingestion))   

## 3. Sysdig Agent 배포
Sysdig Monitoring 서비스를 생성했으니 이제 내 클러스터의 메트릭들을 클라우드의 Sysdig서비스로 보내줄 sysdig agent를 생성하겠습니다.  

### Namespace
~~~sh
$ kubectl create namespace sysdig
namespace/sysdig created
~~~

### Service Account
~~~sh
$ kubectl create serviceaccount sysdig-agent -n sysdig
serviceaccount/sysdig-agent created
~~~

### Secret
위에서 복사해둔 a파라미터의 값을 `SYSDIG_ACCESS_KEY`자리에 넣습니다.  
~~~sh
$ kubectl create secret generic sysdig-agent --from-literal=access-key={SYSDIG_ACCESS_KEY} -n sysdig
secret/sysdig-agent created
~~~

### ClusterRole & ClusterRoleBinding

[sysdig-agent-clusterrole.yaml](https://raw.githubusercontent.com/draios/sysdig-cloud-scripts/master/agent_deploy/kubernetes/sysdig-agent-clusterrole.yaml) 다운로드  
~~~sh
$  kubectl apply -f sysdig-agent-clusterrole.yaml
~~~

ClusterRoleBinding
~~~yaml
# sysdig-agent-clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: sysdig-agent
subjects:
- kind: ServiceAccount
  name: sysdig-agent
  namespace: sysdig
roleRef:
  kind: ClusterRole
  name: sysdig-agent
  apiGroup: rbac.authorization.k8s.io
~~~

~~~sh
$ kubectl apply -f sysdig-agent-clusterrolebinding.yaml
~~~

### Configmap
~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sysdig-agent
data:
  dragent.yaml: |
    configmap: true
    ### Agent tags
    tags: env:prod

    #### Sysdig Software related config ####

    # Sysdig collector address
    collector: {COLLECTOR_ENDPOINT}

    # Collector TCP port
    collector_port: 6443

    # Whether collector accepts ssl
    ssl: true

    # collector certificate validation
    ssl_verify_certificate: true

    #######################################
    new_k8s: true
    k8s_cluster_name: {KUBE_CLUSTER_NAME}
    security:
      k8s_audit_server_url: 0.0.0.0
      k8s_audit_server_port: 7765
~~~

>`collector` : 위에서 복사한 c파라미터의 값  
>`collector_port` : 콜렉터의 port값  
>`new_k8s` : kube state metric을 수집하려면 `true`여야함  
>`k8s_cluster_name` : 클러스터의 이름  
>~~~
>$ kubectl edit configmaps -n kube-system kubeadm-config
>~~~
>![image](https://user-images.githubusercontent.com/15958325/89771721-bdace700-db3b-11ea-8d60-0d31b0823ca7.png)    


## 4. Sysdig Dashboard

~~~sh
$ kubectl get pod -n sysdig

NAME                 READY   STATUS    RESTARTS   AGE
sysdig-agent-875cn   1/1     Running   0          3d
sysdig-agent-pt4cp   1/1     Running   0          3d
~~~

정상적으로 pod들이 Running상태로 되면 IBM Cloud의 sysdig 대시보드로 이동해줍니다.  

View Sysdig 클릭  
![image](https://user-images.githubusercontent.com/15958325/89773437-dc60ad00-db3e-11ea-9b9c-5d4e77995d36.png)  

처음 접속하게 되면 초기 세팅을 하게 되어있습니다.  

<img src="https://user-images.githubusercontent.com/15958325/89773292-99063e80-db3e-11ea-8d83-f7166d372cf9.png" width="600px">  

원래대로면 Kubernetes|GKE|Openshift를 선택해야하는데, 무슨 이유인지 Kubernetes로는 선택이 안되고 Native Linux로 디텍트가 됩니다.  
아마 클라우드 쿠버네티스 서비스가 아니라서 그런가봅니다.  
Native Linux로 골라도 쿠버네티스 모니터링은 정상적으로 진행되니 Native Linux로 선택해줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/89773301-9b689880-db3e-11ea-951d-12fdbd2c8a69.png" width="600px">  

그럼 총 두 개의 Agent가 발견되었다고 뜨게됩니다. (마스터1 워커1)

<img src="https://user-images.githubusercontent.com/15958325/89773307-9dcaf280-db3e-11ea-97d6-f2a6eac5cb57.png" width="600px">  

다음 스텝으로 가게되면 대시보드화면이 뜨고, 인프라는 어떤 것을 쓰고있는지 스캔한 결과를 보여줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/89773657-51cc7d80-db3f-11ea-954a-b0a797bf31b5.png" width="600px">


왼쪽 메뉴의 Explorer를 누르면 현재 확인할 수 있는 메트릭들의 라벨들을 보실 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/89773733-76c0f080-db3f-11ea-8374-7e63123a2133.png)  

>참고로 바로 위와 같은 라벨링이 뜨지는 않고, 체감상 한 10분정도 기다리면 쿠버네티스 메트릭들을 정상적으로 볼 수 있습니다.  

## 5. Test Deployment
본격적으로 대시보드를 탐방해보기 전에, 의미있는 수치들을 확인하기 위해서 테스트용 Nginx 앱을 클러스터에 배포해보겠습니다.  

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
~~~

배포한 후 다시 대시보드로 돌아와서 Deployments 메트릭을 확인해보겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/89774096-25653100-db40-11ea-90eb-ae4dc273464a.png)  

방금 띄운 Nginx deployment를 확인할 수 있습니다.  

Overview의 Kubernetes 항목에는 총 4가지(Cluster, Node, Namespaces, Workloads)에 대한 정보를 개략적으로 확인할 수 있습니다.  
### Cluster
![image](https://user-images.githubusercontent.com/15958325/89774259-87259b00-db40-11ea-83c6-1a44fda410b9.png)  

### Node
![image](https://user-images.githubusercontent.com/15958325/89774295-99073e00-db40-11ea-8cb5-9cc76b3b4dc5.png)

### Namespaces
![image](https://user-images.githubusercontent.com/15958325/89774380-b9cf9380-db40-11ea-9b05-b57e0de58ba1.png)  

### Workloads
![image](https://user-images.githubusercontent.com/15958325/89774442-d66bcb80-db40-11ea-8bc2-7e4b2ccdefcb.png)  

### Event
왼쪽 메뉴의 Event탭에서는 클러스터에서 발생한 여러 이벤트들을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/89774465-e2578d80-db40-11ea-813f-9a4717955849.png)  


## 6. Kubernetes Event 수집
Sysdig에서는 Kubernetes의 이벤트를 수집하기위해 기본적으로 수집할 수 있는 이벤트 셋들을 지정해 뒀습니다.  
자세한 정보는 -> [참고](https://docs.sysdig.com/en/event-types.html)  

우선 기본 sysdig agent를 배포했을 때의 로그를 보면  
![image](https://user-images.githubusercontent.com/15958325/89784515-c1e4fe80-db53-11ea-869d-888868508190.png)  

`k8s events filter` 부분에 현재 수집하려는 쿠버네티스의 이벤트 종류가 나열되어 있습니다.  
그 중, pod은 `BackOff`, `ErrImageNeverPull`, `Failed` 등 과 같은 pod 에러에 관한 이벤트들만 수집할 수 있게 되어있습니다.  

그래서 대시보드의 이벤트 탭을 보면,  
![image](https://user-images.githubusercontent.com/15958325/89784719-1be5c400-db54-11ea-8ec1-66c30af43c17.png)  
replicaSet에 대한 이벤트로그밖에 없습니다.  

기본 이벤트 수집을 변경하고 싶다면, Configmap을 수정해야 합니다.  
Configmap의 마지막 줄에 가서 다음 구문을 추가해줍니다.  
~~~yaml
  events:
    kubernetes:
      pod: [Pulling, Pulled, Failed]
~~~

저는 pod에 대한 이벤트를 수정해보겠습니다.  
원래는 pod 에러에 관한 이벤트뿐이었지만, 이번엔 이미지pulling에 대한 이벤트와 Failed이벤트만 수집하도록 하겠습니다.   

~~~sh
$ kubectl apply -f sysdig-agent-configmap.yaml -n sysdig
~~~

deployment rollout:  
~~~sh
$ kubectl rollout restart ds sysdig-agent -n sysdig
~~~

다시 agent의 로그를 보면 :   
![image](https://user-images.githubusercontent.com/15958325/89785040-b80fcb00-db54-11ea-8004-26c6b33cf9df.png)  

제가 설정했던 세가지 이벤트만 수집하도록 변경되었습니다.  

다시 테스트 앱을 내렸다가 올려보면, 다음과 같이 이미지 pulling에 대한 이벤트도 수집되는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/89785243-0de47300-db55-11ea-9f81-740660966066.png)    

추가로, 이벤트 수집을 안할거면 configmap의 event파라미터를 none으로 바꿔주시면 됩니다.  
~~~yaml
  events: 
    kubernetes: none
~~~

----