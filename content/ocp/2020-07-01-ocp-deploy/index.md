---
title: "Openshift Deployment & DeploymentConfig"
slug: ocp-deploy
tags:
  - Kubernetes
  - Openshift
date: 2020-07-01T13:00:00+09:00
---

## Overview
Openshift는 pod을 배포할 때, 크게 `Deployment`와 `DeploymentConfig` 두가지 방식으로 배포합니다.   
![image](https://user-images.githubusercontent.com/15958325/86209482-a4646280-bbad-11ea-9f5f-5d02725c2527.png)  

이번 포스팅에서는 두 배포 방식의 차이점을 알아보고, `DeploymentConfig`방식을 직접 테스트해보도록 하겠습니다.  


# Prerequisites
- Openshift v4이상 클러스터

# 1. ReplicaSet & ReplicationController
쿠버네티스의 `Deployment`와 마찬가지로 Openshift의 `Deployment`와 `DeploymentConfig`도 Pod의 복제본을 담당하는 컨트롤러를 포함하고 있습니다.  

- **Deployment** : 하나이상의 `ReplicaSet`을 포함
- **DeploymentConfig**: 하나이상의 `ReplicationController`를 포함  

쿠버네티스의 복제컨트롤러들과 동일한 역할을 합니다.  

간단히 설명을 하고 넘어가도록 하겠습니다.  

## ReplicationController
~~~yaml
# 예시파일
apiVersion: v1
kind: ReplicationController
metadata:
  name: frontend-1
spec:
  replicas: 1  
  selector:    
    name: frontend
  template:    
    metadata:
      labels:  
        name: frontend 
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
~~~

- pod의 **복제본을 설장한 수대로 유지** (`replicas`)
- selector로 관리하고자하는 pod을 선택
- **equality-based Selector** 사용
- 로드나 트래픽 기반 오토스케일링은 지원하지 않음

## ReplicaSet

~~~yaml
# 예시파일
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend-1
  labels:
    tier: frontend
spec:
  replicas: 3
  selector: 
    matchLabels: 
      tier: frontend
    matchExpressions: 
      - {key: tier, operator: In, values: [frontend]}
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
~~~

- ReplicationController와 비슷한 기능 제공
- 차이점은 **Set-based Selector**를 사용한다는 점
    (in notin exist 등)

ReplicationController는 label과 일치하는 name의 pod만 관리할 수 있다면  
ReplicaSet은 연산자를 사용해 좀더 풍부한 표현식을 사용해 pod을 관리할 수 있다는 게 차이점입니다.  

# 2. Deployment & DeploymentConfig

## Deployment
~~~
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-openshift
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-openshift
  template:
    metadata:
      labels:
        app: hello-openshift
    spec:
      containers:
      - name: hello-openshift
        image: openshift/hello-openshift:latest
        ports:
        - containerPort: 80
~~~

- 하나 이상의 `ReplicaSet`포함
- 배포 라이프사이클을 위한 기능을 지원
- **Controller Manager가 배포 프로세스를 관리**
- 배포할 노드가 죽어도 ControllerManager가 관리하기때문에 다른 마스터에서 배포 관리 가능 (**가용성 중시**) 
- 중간에 롤아웃 일시중지가능

## DeploymentConfig
~~~
apiVersion: v1
kind: DeploymentConfig
metadata:
  name: frontend
spec:
  replicas: 5
  selector:
    name: frontend
  template: { ... }
  triggers:
  - type: ConfigChange 
  - imageChangeParams:
      automatic: true
      containerNames:
      - helloworld
      from:
        kind: ImageStreamTag
        name: hello-openshift:latest
    type: ImageChange  
  strategy:
    type: Rolling 
~~~

- 하나 이상의 `ReplicationController`포함
- 배포 라이프사이클을 위한 기능을 지원
    - build이벤트에 따른 자동 배포 트리거 
    - 업데이트가 있을 시, strategy 지정 가능
    - roll-back
- Deployer pod이 배포프로세스를 관리
- 배포할 노드가 죽으면 노드가 온라인상태가 되거나 수동으로 삭제할 때까지 기다림 (일관성 중시)
- LifeCycle hook
- custom strategies

## DeploymentConfig 다뤄보기!
### DeploymentConfig 배포
web gui에서 sample app을 deploymentconfig형식으로 배포해줍시다

### DeploymentConfig 확인
~~~sh
$ oc get dc
~~~
![image](https://user-images.githubusercontent.com/15958325/86225686-8b67ab80-bbc5-11ea-8fca-81770e81b47c.png)  


### Rollout
deploymentconfig의 버전을 1증가하여 업데이트하는 명령어입니다.  
~~~sh
$ oc rollout latest dc/{dc name}
deploymentconfig.apps.openshift.io/php-app-00 rolled out
~~~
![image](https://user-images.githubusercontent.com/15958325/86225662-8276da00-bbc5-11ea-954e-4d4669ad576d.png)  

### history
현재까지 진행된 deploymentconfig의 rollout history를 확인하는 명령어입니다.
~~~sh
$ oc rollout history dc/php-app-00
~~~
![image](https://user-images.githubusercontent.com/15958325/86225808-b520d280-bbc5-11ea-8efa-347707b0611a.png)  

특정 revision의 deploymentconfig 상세정보를 확인하려면 `revision` 파라미터를 사용하면 됩니다.  
~~~sh
$ oc rollout history dc/php-app-00 --revision=1
~~~
![image](https://user-images.githubusercontent.com/15958325/86225905-d681be80-bbc5-11ea-99f9-5332c1044029.png)  

더 상세한 정보를 얻으려면 `describe` 명령어를 사용하면 됩니다.  
~~~sh
$ oc describe dc php-app-0
~~~
![image](https://user-images.githubusercontent.com/15958325/86226182-3d06dc80-bbc6-11ea-80f4-a85319fa9ff2.png)  


### deployment 재시도
DeploymentConfig의 배포가 실패했을 때 배포를 재시도하려면 `retry` 명령어를 사용합니다.  
~~~sh
$ oc rollout retry dc/php-app-00
~~~
![image](https://user-images.githubusercontent.com/15958325/86226589-d6ce8980-bbc6-11ea-8890-e4bc32f880a0.png)  

배포에 실패한 dc에만 사용할 수 있는 명령어여서 지금은 complete상태이므로 error가 발생합니다.  

추가로 retry는 단순히 실패한 배포를 다시 실행할 뿐, 새로운 revision은 생성하지 않습니다.

### deployment rolling back
이전 버전으로 롤백하려면 `undo`명령어를 사용합니다.  
~~~sh
$ $ oc rollout undo dc/php-app-00
deploymentconfig.apps.openshift.io/php-app-00 rolled back
~~~
![image](https://user-images.githubusercontent.com/15958325/86233060-d4246200-bbcf-11ea-9766-21a22df39344.png)  

undo한 것도 버전으로 기록되어서 revision이 3이 됩니다.  

특정 버전으로 롤백하려면 `--to-revision`파라미터를 추가하면 됩니다.  

### deployment log
로그를 확인하려면 `logs`명령어를 사용합니다.  
~~~sh
$ oc logs -f dc/php-app-00
~~~

![image](https://user-images.githubusercontent.com/15958325/86233589-9d028080-bbd0-11ea-9306-c2e96ad7321e.png)  


특정 버전의 log를 확이하려면 `--version` 파라미터를 추가하면 됩니다.  

### deployment scale
deploymentconfig는 pod의 개수도 관리를 하고 있습니다. replica의 개수를 조정하려면 `scale`명령어를 사용하면 됩니다.  
~~~sh
$ oc scale dc/php-app-00 --replicas=3
deploymentconfig.apps.openshift.io/php-app-00 scaled
~~~
![image](https://user-images.githubusercontent.com/15958325/86233742-db983b00-bbd0-11ea-9121-47eb88cb678d.png)  

replica를 1->3으로 올리니 두 개가 더 생성된 것을 확인 가능합니다.  

----
