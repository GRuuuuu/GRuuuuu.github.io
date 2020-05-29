---
title: "Openshift4.3 Control plane 이란?"
categories: 
  - OCP
tags:
  - Kubernetes
  - doc
  - Openshift
last_modified_at: 2020-05-29T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Red Hat 공식 문서에 적혀있는 내용을 번역한 문서입니다.  
**영어공부겸 하는 번역이니 오역&의역이 있을수도 있습니다..**   

**원문** : [RedHat/Understanding the OpenShift Container Platform control plane](https://docs.openshift.com/container-platform/4.3/architecture/control-plane.html)    

# Understanding the OpenShift Container Platform control plane
master노드를 구성하는 `control plane`은 **Openshift Container Platform** 클러스터를 관리하는 역할을 합니다. 주로 워크로드와 워커노드(compute machine)를 관리합니다.  
또한 `Cluster Version Operator`와 `Machine Config Operator`, 그리고 각각의 Operator들로 machine 업그레이드를 담당합니다.  

## Machine roles in OpenShift Container Platform
ocp는 각 노드마다 별개의 역할을 부여할 수 있습니다. 이러한 역할들은 클러스터에서 노드가 어떤 일을 할지 결정하게 됩니다.  

크게 마스터와 워커로 나뉘며 부트스트랩(bootstrap)역할도 있긴 하지만 부트스트랩은 클러스터를 설치할 때만 사용되는 역할이기 때문에 이번 문서에서는 마스터와 워커에 대해서만 알아보겠습니다.  

### Cluster Workers
**Kubernetes**에서 워커노드는 유저의 요청에 의한 실제 워크로드를 수행하는 역할을 하였습니다.  
워커는 자신의 남은 리소스를 마스터에게 알리고 마스터의 스케줄러는 그 정보를 바탕으로 최적의 노드를 찾아 컨테이너 또는 pod을 올리게됩니다.  
또한 컨테이너 엔진인 `CRI-O`, 컨테이너 워크로드를 담당하는 `Kubelet`, 워커간 통신을 담당하는 `Service Proxy` 등 중요한 서비스들도 워커노드에서 동작합니다.  

**Openshift Container Platform**에서는 `MachineSet`이 워커를 컨트롤합니다.  
워커역할을 하는 노드들은 특정 machine pool에 의해 관리되는 워크로드들을 담당하게 됩니다.  
왜냐면 ocp는 여러 머신 타입을 지니고 있기 때문에 워커들은 "`compute machines`"라는 카테고리로 분류됩니다. 이번 버전에서 "`worker machine`"과 "`compuete machine`"은 동일한 의미로 사용되지만 (현재 compute machine의 default type은 worker machine이기 때문), 후에는 infrastructure machine과 같은 타입이 기본타입이 될 수도 있을겁니다.  


### Cluster Masters
**Kubernetes**에서 마스터노드는 쿠버네티스 클러스터를 관리하는데 필요한 서비스를 수행하는 역할을 했습니다.  

**Openshift Container Platform**에서는 마스터들은 **control plane** 역할을 합니다. 단순히 ocp클러스터를 관리하기위한 쿠버네티스 서비스만 수행하는 것이 아니라 더 많은 역할을 하게됩니다.  
워커와 같이 MachineSet으로 컨트롤되는 것 대신, 마스터는 독립적인 machine API로 정의될 수 있습니다.  

>마스터는 3개로 사용해야합니다. 이론상으로 아무 개수로 사용할 수 있지만, 마스터와 etcd의 pod들이 같은 host에서 동작하기 위해 etcd쿼럼에 의해서 그 숫자가 제한됩니다.  

**-control plane에서 동작하는 kubernetes service-**  

|Component|Description|
|---|---|
|API Server|pod의 데이터나 service, replication controller를 구성하고 검증하는 역할을 합니다. 또한 클러스터 상태에 대한 정보를 제공합니다.|
|etcd|마스터의 상태정보를 persistent하게 저장합니다.|
|Controller Manager Server|복제, 네임스페이스, 서비스어카운트 등의 변경을 감시한 다음 API를 사용해 지정된 상태를 시행하는 역할을 합니다.|

이러한 서비스들 중 몇몇은 pod으로 동작하는 대신 마스터 머신의 `systemd`서비스로 돌아갑니다. 
systemd서비스는 항상 떠있어야 하는 서비스에 적합한 형태입니다. 예를들어 다음과 같습니다.  
- `CRI-O` : 컨테이너를 실행시키고 관리하는 컨테이너 엔진입니다. ocp4.3 에서는 docker대신 crio를 사용합니다.  
- `Kubelet` : 컨테이너로 들어오는 요청을 관리하는 역할

이러한 서비스들은 다른 컨테이너의 뒤에서 동작해야하는 서비스들이기 때문에, 호스트위에서 바로 동작하는 systemd의 형태로 동작합니다.  


## Operators in OpenShift Container Platform
**Openshift Container Platform**에서 Operator는 control plane에서 서비스를 관리하고 배포하며 패키징하는 역할을 담당합니다. `kubectl` 과 `oc` 커맨드와 같은 Kubernetes API와 CLI툴을 통합해주며, health check, 업데이트 관리, application이 지정된 상태를 유지하게 해주는 역할도 합니다.  

CRI-O와 kubelet이 모든 노드에서 돌아가고 있기 때문에, 거의 모든 클러스터 기능은 operator로 사용할 수 있으며 control plane에 의해 관리됩니다.  
그런 맥락에서 ocp4.3의 컴포넌트중 가장 중요한 컴포넌트라고 할 수 있습니다.  

### PLATFORM OPERATORS IN OPENSHIFT CONTAINER PLATFORM

ocp4.3에서는 모든 클러스터 기능이 `Platform Operator`로 구분됩니다.  
**Platform Operator**는 클러스터의 특정 영역의 기능을 관리합니다.  
- 전 클러스터 application의 로깅
- control plane의 관리
- 머신 provisioning 시스템의 관리

각 operator는 간단한 API로 기능을 제공하며, 글로벌 구성파일을 수정하는 대신에 API를 수정함으로써 일반적인 작업을 자동화시켜 운영부담을 줄일 수 있습니다.  


### OPERATORS MANAGED BY OLM

**Cluster Operator Lifecycle Management**(OLM)은 application에서 사용할 수 있는 operator를 관리하는 컴포넌트입니다. (ocp를 구성하는 operator는 관리대상이 아님)   
다시말해 kubernetes-native app을 operator로써 관리하는 일종의 프레임워크가 OLM입니다.  

OLM은 `Red Hat Operator`와 `Certified Operator`로 나뉩니다.  
`Red Hat Operator`는 스케줄러나 etcd같은 클러스터 기능을 제공하고, `Certified Operator`는 community에서 빌드하고 관리하며, 전통적인 application에 API레이어를 제공해서 쿠버네티스기반으로 application을 관리할 수 있게 해주는 기능을 제공합니다.  

### ABOUT THE OPENSHIFT CONTAINER PLATFORM UPDATE SERVICE
`ocp update service`는 Openshift Container Platform과 Red Hat Enterprixe Linux CoreOS(RHOCS)에 over-the-air(OTA) 업데이트를 제공해주는 서비스입니다.  
각 operator 컴포넌트끼리 연결된 그래프와 다이어그램을 제공해서 어떤 버전으로 업그레이드를 해야 안전하게 할 수 있는지, 업데이트 할 클러스터의 예상 상태를 보여줄 수 있습니다.  

`Cluster Version Operator`(CVO)는 최신 컴포넌트의 버전과 정보를 바탕으로 update service가 적절한 업데이트를 찾았는지 체크하는 역할을 합니다. 유저가 업데이트를 진행하려고 할 때, CVO는 release된 이미지를 찾아서 클러스터를 업그레이드합니다.  

update 서비스가 호환되는 버전의 업데이트만 제공하게 하려면, 검증 파이프라인이 존재해야합니다. 각 릴리즈 버전은 클라우드 플랫폼, 시스템 아키텍처, 기타 구성요소와의 호환성을 검증하고 파이프라인이 적합하다고 판단되면 update 서비스는 사용자에게 업데이트가 이용가능하다고 알려줍니다.  

지속 업데이트 모드가 활성화되어있는 동안 두개의 컨트롤러가 동작합니다. 하나는 지속적으로 페이로드 매니페스트 파일을 업데이트하고 클러스터에 적용시키며 operator의 상태를 출력합니다. 두번째 컨트롤러는 update서비스를 통해 업데이트가 가능한 상태인지를 확인하는 역할을 합니다.  

> 클러스터를 이전버전으로 되돌리는 것은 지원하지 않습니다. 반드시 새로운 버전으로만 업그레이드해야 합니다.  

업그레이드 과정중에 `Machine Config Operator`(MCO)는 새로운 구성을 클러스터에 적용하는 역할을 합니다.  


### UNDERSTANDING THE MACHINE CONFIG OPERATOR
ocp4.3은 운영체제와 클러스터 관리를 모두 통합해서 쓸 수 있습니다. 클러스터는 RHCOS를 포함한 자체 업데이트를 관리하므로 ocp는 노드 업그레이드를 단순화시키는 라이프사이클 관리 환경을 제공합니다.  

노드 관리를 단순화하기 위해 3개의 데몬셋 및 컨트롤러를 사용합니다.  

- `machine-config-controller` : control plane에서 머신 업그레이드를 조정하는 역할을 합니다. 모든 클러스터 노드를 모니터링하고 구성 업데이트를 오케스트레이션합니다.  
- `machine-config-daemon` : 클러스터의 각 노드에서 실행되며 MachineConfig에 정의된 구성으로 머신을 업데이트 하는 역할을 합니다. 노드에 변경사항이 표시되면 pod을 drain(축출?)하고 업데이트를 적용한 후에 재부팅합니다. 이러한 변경사항은 시스템 구성 및 kubelet구성을 담은 ignition파일의 형태로 제공됩니다. 이 프로세스는 ocp및 RHCOS를 함께 관리하는데 핵심적인 요소로 사용됩니다.  
- `machine-config-server` : 마스터노드가 클러스터에 조인할때 ignition파일을 마스터에 제공합니다.  


# 마치며
왜케 내용이 어렵죠... 문서 번역하고나서 따로 내용을 정리해야겠다는 생각이 듭니다..

----
