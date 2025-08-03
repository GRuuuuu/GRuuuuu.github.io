---
title: "Openshift ResourceQuota & LimitRange"
slug: ocp-resourcequota
tags:
  - Kubernetes
  - Openshift
date: 2020-07-01T13:00:00+09:00
---

## Overview
Openshift의 리소스를 제한시키는 기능인 ResourceQuota에 대해서 알아보겠습니다.  

# Prerequisites
- Openshift v4이상 클러스터

# 1. ResourceQuota & LimitRange
## ResourceQuota
프로젝트의 리소스를 제한시키는 기능을 제공합니다. 크게 세가지 타입의 리소스를 관리합니다.  
- **Compute Resource** (cpu, memory, ephemeral-storage 등)
- **Storage Resource** (pvc용량, pvc개수등)
- **Object counts** (pod, rc, rsourcequotas, svc, configmap 등)

> ephemeral-storage : 로컬 임시 스토리지 (emptydir)

## LimitRange
아무런 제약을 걸지 않았을 때, 기본적으로 컨테이너는 Openshift의 리소스를 무제한으로 사용할 수 있습니다.  
위의 `ResourceQuota`로 클러스터의 프로젝트 별로 리소스 사용과 생성을 제한할 수 있다면 `LimitRange`는 pod이나 컨테이너의 리소스를 제한하는 정책입니다.  

좀 더 작은 단위의 제약 조건이라고 생각하시면 됩니다.  

- pod과 컨테이너의 최소&최대 컴퓨팅 리소스 사용량 지정
- 최소&최대 pvc용량 지정
- 리소스에 대한 Request와 Limit사이의 비율을 지정

# 2. Hands-On
## ResourceQuota 적용
먼저 새로운 project를 하나 생성해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/86236149-8e1dcd00-bbd4-11ea-9db4-3d387b20c51b.png)   

그 다음, 관리자페이지의 Administration > Resource Quotas로 이동해 ResourceQuota를 생성  
![image](https://user-images.githubusercontent.com/15958325/86236187-a261ca00-bbd4-11ea-90c2-bde497a11c17.png)  

test resource quota를 하나 생성하겠습니다.  

~~~sh
apiVersion: v1
kind: ResourceQuota
metadata:
  name: test-quota
  namespace: resource-management-00
spec:
  hard:
    pods: '3'
    services: '5'
    requests.cpu: '1'
    requests.memory: 512Mi
    replicationcontrollers: '5'
    resourcequotas: '1'
~~~
pod은 3개까지  
services는 5개까지  
cpu와 memory는 각각 1개, 512mb까지 사용가능  
replicationcontrollers는 5개까지  
resourcequotas는 1개까지 생성가능합니다.  

>이 ResourceQuota는 프로젝트(`resource-management-00`)에만 적용되는 제한사항입니다.  

배포를 해주면 ResourceQuota의 overview에서 생성한 ResourceQuota의 세부사항을 확인할 수 있습니다.    
![image](https://user-images.githubusercontent.com/15958325/86236403-f9679f00-bbd4-11ea-9de1-5663f5abf8df.png)  
![image](https://user-images.githubusercontent.com/15958325/86236335-e05eee00-bbd4-11ea-8c7e-3071b88d406a.png)  


## ResourceQuota가 제대로 적용되었는지 확인
좌측 메뉴의 Workloads > Deployments를 선택해줍니다.  

Deployment 생성하기 버튼을 누르면 :  
![image](https://user-images.githubusercontent.com/15958325/86237025-fe791e00-bbd5-11ea-90ca-437236ba72f9.png)  

이렇게 기본 템플릿이 나옵니다.  
![image](https://user-images.githubusercontent.com/15958325/86237053-0cc73a00-bbd6-11ea-9c5a-ce3be53d8f3a.png)    

그대로 생성해주고 Workloads > ReplicaSet으로 이동해보면 제대로 복제본들이 뜨지 않은 것을 확인할 수 있습니다.   
![image](https://user-images.githubusercontent.com/15958325/86237115-27011800-bbd6-11ea-883a-1b2dba6bee87.png)    

Event탭으로 이동하면 상세 사항을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/86237166-3aac7e80-bbd6-11ea-9abb-87cb32ecdeb2.png)  
에러의내용은 앞에서 생성했던 ResourceQuotas 규칙에 부합하지 않는 생성이기 때문에 pod을 생성하지 않았다는 내용입니다.  

## LimitRange 생성
컨테이너는 기본적으론 Openshift클러스터의 리소스를 무제한으로 사용하기 때문에 ResourceQuota를 쓰기 위해선 개별 pod에 대한 리소스 제약이 필요합니다.  

개별 pod 또는 컨테이너에 거는 리소스제약이 `LimitRange`입니다.  

현재 사용하고 있는 프로젝트인 `limits-00`에서 생성되는 모든 pod은 다음과 같은 리소스 제약을 갖게 설정하는 구문입니다.  
~~~yaml
kind: LimitRange
apiVersion: v1
metadata:
  name: limits-00
spec:
  limits:
  - type: Pod
    max:
      cpu: 1
      memory: 1.5Gi
    min:
      cpu: 100m
      memory: 50Mi
  - type: Container
    max:
      cpu: 500m
      memory: 750Mi
    min:
      cpu: 100m
      memory: 50Mi
    default:
      cpu: 200m
      memory: 100Mi
~~~

다음 명령어로 `LimitRange`를 클러스터에 배포해줍니다.  
~~~sh
$ oc create -f limitlange.yaml -n resource-management-00

limitrange/limits-00 created
~~~

GUI에서 확인하려면 Administration > LimitRanges로 들어가서   
![image](https://user-images.githubusercontent.com/15958325/86728386-606ad500-c067-11ea-96a2-a0566488ab10.png)  

생성했던 LimitRange를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/86728463-724c7800-c067-11ea-88db-0563ab6465be.png)  
![image](https://user-images.githubusercontent.com/15958325/86728590-898b6580-c067-11ea-8193-54ba06a1aeb1.png)  


LimitRange를 배포한 후에, 위에서 오류가 났었던 ReplicaSet의 로그를 다시 살펴보면 정상적으로 배포가 진행되었다는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/86728637-94de9100-c067-11ea-9aee-29e3b7d37b0a.png)  


## ResourceQuota가 제대로 적용되었는지 확인2
### pod4개 띄워보기
맨처음에 배포한 ResourceQuota에서 pod의 개수를 3으로 제한을 걸어뒀습니다.  

한번 Workload > Deployments로 이동해서 pod의 개수를 3에서 4로 늘려봅시다.  

![image](https://user-images.githubusercontent.com/15958325/86729311-4978b280-c068-11ea-9efe-fcfea6f81260.png)   

Workload > ReplicaSet의 Event탭을 살펴보면 pod의 개수가 3으로 제약이 걸려있기 때문에 pod을 더 늘릴 수 없다고 에러가 발생한 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/86729509-82b12280-c068-11ea-8a90-edff68902275.png)  

### Deployment의 resource 변경하기
현재 배포된 pod의 리소스를 확인해보겠습니다.  

Workload > Deployments로 이동해서 pod의 개수를 1개로 scale-down시켜주고,  
![image](https://user-images.githubusercontent.com/15958325/86731622-aecda300-c06a-11ea-8f42-2d87cd52f074.png)  

Pods탭으로 이동 :   
![image](https://user-images.githubusercontent.com/15958325/86731655-b55c1a80-c06a-11ea-9dd5-97bc8d50714e.png)  

YAML을 보면 현재 해당 pod의 resource는 LimitRange에서 설정한 default값을 따르고 있는 것을 확인 가능합니다.  
![image](https://user-images.githubusercontent.com/15958325/86731663-b725de00-c06a-11ea-819f-516732ceb7ff.png)  

현재 해당 pod은 deployment 컨트롤러의 관리를 받고 있기 때문에 deployment의 설정을 바꿔서 산하 pod들의 리소스들을 수정시켜보겠습니다.  

Workload > Deployments > YAML 탭으로 이동해서 30번 줄 resources를 변경해주면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/86736600-9eb7c280-c06e-11ea-92c9-2e0f26e93446.png)     

~~~
resources:
  limits:
    cpu: 500m
  requests:
    cpu: 500m
~~~

이렇게 바꿔주면 앞으로 이 deployment에서 관리하는 pod들은 위와같은 리소스제약을 가지게 됩니다.  

Deployment를 save해서 재배포해주고 Workload > Deployments > Pods > pod 선택 후 YAML탭을 살펴보면,  
![image](https://user-images.githubusercontent.com/15958325/86737706-754b6680-c06f-11ea-9545-9384a953adb9.png)  
deployment에서 설정한 대로 리소스가 정의된 것을 확인할 수 있습니다.  

테스트로 pod을 3개로 다시 scale-up해주면 pod이 2개밖에 안뜨는 것을 확인할 수 있고  
![image](https://user-images.githubusercontent.com/15958325/86737934-9f9d2400-c06f-11ea-9dfd-dd95149bb61d.png)  

로그를 보면 cpu리소스의 limit을 넘어가는 request이기 때문에 pod이 생성되지 않았다는 메세지를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/86737982-a7f55f00-c06f-11ea-8749-9d47cbe185bf.png)  

Administration > ResourceQuotas 로 이동해보면 현재 설정한 ResourceQuota중에 얼마나 사용하고 있는지 확인할 수 있습니다.   
![image](https://user-images.githubusercontent.com/15958325/86738084-be031f80-c06f-11ea-910f-a9421a8bf0ce.png)   



끝

----
