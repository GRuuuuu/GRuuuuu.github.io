---
title: "Kubernetes Controllers : Replication, Deployment, DaemonSet"
slug: k8s-controllers
tags:
  - Kubernetes
  - Controller
date: 2019-12-09T13:00:00+09:00
---

## 1. Overview
이번 문서에서는 `Kubernetes`(k8s)의 Controller에 대해서 알아보겠습니다.  

## 2. Prerequisites

본문에서 사용한 spec :  
`OS : CentOS v7.6`  
`Arch : x86`  

k8s클러스터는 1마스터 2노드로 구성했습니다.  
`Master` : 4cpu, ram16G  
`Node` : 2cpu, ram4G  

# 3. Controller?
쿠버네티스는 크게 객체(object)와 그것을 관리하는 컨트롤러(controller)로 구성됩니다.  

객체(object)에는 `pod`, `service`, `volume` 등이 있습니다.  
컨트롤러(Controller)에는 `Replication`, `Deployment`, `StatefulSet`, `DaemonSet`, `Job` 등이 있습니다.  

컨트롤러를 통해 객체를 사용자가 미리 설정했던 상태로 유지할 수 있도록 관리할 수 있습니다.  

이번 문서에서는 쿠버네티스의 컨트롤러중 Replication, Deployment, StatefulSet에 대해서 알아보겠습니다.  

## Pod?
컨트롤러에 대해 알아보기전에 pod이 무엇인지에 대해서 짚고 넘어가겠습니다.  

pod은 쿠버네티스가 배포, 관리할 수 있는 최소단위이며 컨테이너들의 집합입니다.  
![image](https://user-images.githubusercontent.com/15958325/70419213-5a4c5000-1aa8-11ea-93d9-5c8bfb2be63d.png)  
 

하나의 pod안에 있는 컨테이너들은 자원을 공유하게 되기 때문에, 동일한 목적을 가진 컨테이너들로 구성하는것이 좋습니다.  
위 사진을 보시면 하나의 pod안에 File puller, Web server와 같이 역할은 다르지만 동일한 목적을 가진 컨테이너끼리 뭉쳐있으며 이들은 같은 volume을 공유하고 있는 것을 확인할 수 있습니다.  

----

다시 컨트롤러에 관한 내용으로 돌아와서 살펴보도록 하겠습니다.

## Replication Controller
지정된 숫자 만큼의 pod이 항상 클러스터내에서 실행되고 있도록 관리하는 역할을 합니다.  

Controller를 사용하지 않고 pod을 직접 띄웠을때는 pod이 비정상적으로 종료되었을때 재시작이 어려운데, 

Replication Controller를 사용해서 띄운 pod이라면 노드에 장애가 생겨 pod이 내려갔을때 클러스터 내의 다른 노드에 다시 pod을 띄워주게 됩니다.  

### 실습1 : 기본동작
예제를 통해 자세히 알아보겠습니다.  

~~~sh
$ vim replicationcontroller-nginx.yaml

apiVersion: v1
kind: ReplicationController
metadata:
  name: nginx      # replication controller의 이름
spec:
  replicas: 3      # pod의 복제본은 3개(원본포함)
  selector:        # nginx라는 label을 가진 pod을 select
    app: nginx
  template:
    metadata:
      name: nginx
      labels:      # spec.selector와 spec.template.metadata.labels는 같아야함
        app: nginx
    spec:          # 컨테이너의 정보
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
~~~

만들었으면 다음명령어를 통해 클러스터에 pod을 배포해봅시다.  
~~~sh
$ kubectl apply -f replicationcontroller-nginx.yaml

replicationcontroller/nginx created
~~~

배포한 뒤, 올라가있는 pod들을 살펴봅시다.  
~~~sh
$ kubectl get pods
~~~
![image](https://user-images.githubusercontent.com/15958325/70414635-0d637c00-1a9e-11ea-9fa9-8afe846707f1.png)  

nginx의 복제본이 3개 만들어진것을 확인할 수 있습니다.  

이제 이중에서 하나골라 강제로 삭제시켜봅시다. 저는 첫번째 pod을 삭제해보겠습니다.    
~~~sh
$ kubectl delete pod nginx-cntjd

pod "nginx-cntjd" deleted
~~~

pod을 확인해보면,  
~~~sh
$ kubectl get pods
~~~
![image](https://user-images.githubusercontent.com/15958325/70415130-4a7c3e00-1a9f-11ea-83fc-6fb13ed2cba9.png)  
첫번째 pod이 사라짐과 동시에 새로운 복제본이 생긴것을 확인할 수 있습니다.  

### 실습2 : controller삭제해보기
이번에는 컨트롤러를 삭제했다가 다시 생성해보겠습니다.  

먼저 controller와 pod확인 :   
~~~sh
$ kubectl get rc,pods
~~~
![image](https://user-images.githubusercontent.com/15958325/70415750-b7440800-1aa0-11ea-956d-88e63a10ae1b.png)  


replication controller를 삭제해봅시다.  
~~~sh
# cascade=true이면 controller에 딸린 pod까지 전부 삭제됩니다.
# default는 cascade=true
$ kubectl delete rc nginx --cascade=false
~~~


controller를 삭제한 상태에서 pod을 지우게되면 :  
![image](https://user-images.githubusercontent.com/15958325/70415840-eb1f2d80-1aa0-11ea-91aa-1f7e56f89be7.png)  

pod 복제본3개가 유지되지 않는 것을 확인하실 수 있습니다.  

그럼 이번엔 replication controller를 다시 생성해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/70415889-143fbe00-1aa1-11ea-9e89-7367f3487d54.png)  
새롭게 3개의 복제본이 생기는 것이 아니라, **이미 있는 label을 체크해서 1개의 복제본만 추가**하는 모습을 확인할 수 있습니다.  

### 실습3 : label 바꿔보기
이번엔 실행중인 pod의 label을 바꿔보겠습니다.  

~~~sh
$ kubectl edit pod nginx-mf4h5
~~~
![image](https://user-images.githubusercontent.com/15958325/70416060-7ac4dc00-1aa1-11ea-9fe3-fede25e9b9fd.png)  
빨갛게 표시해둔 부분을 nginx에서 nginx-test라는 label로 변경해봅시다.  


변경 후에, pod 리스트를 출력함과 동시에 label만 필터링해서 출력해봅시다.  
~~~sh
$ kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels}{"\n"}{end}'
~~~
![image](https://user-images.githubusercontent.com/15958325/70416171-bfe90e00-1aa1-11ea-8d6a-8e86a93c9308.png)  
label을 변경했던 pod은 replication controller의 영향권내에서 벗어나게 되었습니다.  
그리고 nginx라는 label을 가진 pod이 하나 없어졌으므로 3개를 맞추기위해 새로 생성된 모습을 확인할 수 있습니다.  

이렇게 label을 활용해 실행중인 pod을 재부팅없이 실제 서비스 상태에서 떼어내 다른 용도로 활용할 수 있습니다.  

### 실습4 : rolling update
실행되고 있는 pod들을 업데이트시킬때 사용하는 방법입니다.  

~~~sh
$ kubectl rolling-update {label} --image=nginx:latest
~~~
![image](https://user-images.githubusercontent.com/15958325/70416416-69300400-1aa2-11ea-9f8c-6f23cbec7f66.png)  

새로운 버전의 pod이 뜨고, 옛날버전은 그다음에 삭제되는 것을 확인할 수 있습니다.  
즉, 1개씩 pod이 교체됩니다.  
![image](https://user-images.githubusercontent.com/15958325/70416482-8369e200-1aa2-11ea-8d2d-53db6cfd57cc.png)  

> **Replication controller**의 다음 버전인 **ReplicaSet**에서는 rolling update가 지원되지 않습니다.  
> 그래서 일반적으로는 아래에서 언급할 Deployments controller를 사용합니다.  

## Deployments Controller
`Deployments Controller`는 일반적인 상태가 없는 application을 배포할때 사용하는 컨트롤러입니다.  
처음에는 Replication Controller가 이 역할을 했지만 이제는 Deployments Controller가 기본적인 방법으로 사용되고 있습니다.  

Deployments Controller는 기존에 Replication Controller가 했던 역할인 복제 세트 관리를 보다 세밀하게 관리할 수 있으며, 배포에 관한 다양한 기능을 가지고 있습니다.  

### 실습1 : 기본동작

샘플 yaml파일을 만들어줍시다.  
~~~sh
$ vim deployments-nginx.yaml

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

생성한 yaml파일을 배포해보면, Replication Controller와 ReplicaSet을 포함해서 배포되는 것을 확인할 수 있습니다.
~~~sh
$ kubectl apply -f deployments-nginx.yaml

kubectl get deploy,rs,rc,pods
~~~
![image](https://user-images.githubusercontent.com/15958325/70417121-e90a9e00-1aa3-11ea-89b2-ed46b5edbe5e.png)  

### 실습2 : rolling-update
pod들이 생성되었으니 업데이트를 해보도록 하겠습니다.  

기본적으로는 replication controller와 유사하게 동작합니다.  

~~~sh
# 현재 pod의 이미지 정보 출력
$ kubectl get deploy -o jsonpath='{.items[0].spec.template.spec.containers[0].image}{"\n"}'

# 업데이트
$ kubectl set image deployment/nginx-deployment nginx=nginx:latest
~~~
![image](https://user-images.githubusercontent.com/15958325/70417391-7bab3d00-1aa4-11ea-888c-178afaba1bef.png)  
nginx이미지가 latest버전으로 업데이트된것을 확인할 수 있습니다.  

이전과 동일하게 새로운 pod을 먼저 만들고 다만들면 기존의 pod을 삭제하는 방식으로 진행됩니다.  
![image](https://user-images.githubusercontent.com/15958325/70417468-a5fcfa80-1aa4-11ea-8764-6dd2e4c6abe2.png)  

### 실습3 : rollout(롤백)
배포한 버전을 롤백시킬수도 있습니다.  

~~~sh
# 이미지 명 및 변경내역 확인
$ kubectl rollout history deploy nginx-deployment

# 바로 직전버전으로 롤백(undo)
$ kubectl rollout undo deploy nginx-deployment

# 특정 버전으로 롤백
$ kubectl rollout undo deploy nginx-deployment --to-revision=3 
~~~

되돌릴 수 있는 revision 개수는 `.spec.revisionHistoryLimit` 옵션을 이용해서 조정할수 있습니다.  

### 실습4 : pod개수 조정
실행하고있는 pod들의 개수를 조절할수도 있습니다.  

원래 3개의 복제본을 가지고 있었는데 5개로 늘리는 경우 :   
~~~sh
$ kubectl scale deploy nginx-deployment --replicas=5
~~~

![image](https://user-images.githubusercontent.com/15958325/70418115-1bb59600-1aa6-11ea-852c-ae7ba408bbb7.png)  

2개의 pod이 새로 추가된 모습을 확인할 수 있습니다.  


## DaemonSet Controller
다음은 클러스터 전체에 pod을 띄울 때 사용하는 controller입니다.  

클러스터 내부에 새로운 노드가 추가되었을 때, 자동으로 그 노드에 pod을 실행시켜주고  
노드가 사라지면 노드속의 pod은 그대로 사라지게 됩니다.  

보통 로그수집이나, 모니터링 등 항상 실행시켜두어야 하는 pod에 사용합니다.  

### 실습1 : 기본동작
이번에는 node가 1개인 상태에서 실습을 진행하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/70418272-7a7b0f80-1aa6-11ea-875d-ead0b93e80b7.png)  

이번엔 nginx말고 elasticsearch를 배포해보도록 하겠습니다.  
~~~sh
$ vim daemonset-elastic.yaml

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      app: fluentd-elasticsearch
  template:
    metadata:
      labels:
        app: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: k8s.gcr.io/fluentd-elasticsearch:1.20
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
~~~

실행시켜줍니다.  
~~~sh
$ kubectl apply -f daemonset-elastic.yaml

daemonset.apps/fluentd-elasticsearch created
~~~

마스터에서 pod목록을 확인해보면  
~~~sh
$ kubectl get pods -A
~~~
![image](https://user-images.githubusercontent.com/15958325/70418596-1147cc00-1aa7-11ea-96de-ba1bdf039d3a.png)  
정상적으로 실행된 것을 확인할 수 있고, 현재 두개의 pod이 올라온 것을 확인할 수 있습니다.  

실제로 각각의 pod이 어느노드에 올라가있는지 확인해봅시다.  

~~~sh
$ kubectl describe pod fluentd-elasticsearch --namespace=kube-system |grep Node:
~~~
![image](https://user-images.githubusercontent.com/15958325/70418862-9af79980-1aa7-11ea-8322-bce7949720c9.png)  

마스터와 1번노드에 올라가있는것을 확인할 수 있습니다.  

이제 2번노드를 클러스터에 추가한 뒤, 바로 확인해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/70418968-dabe8100-1aa7-11ea-9953-5bacf4511417.png)  
정상적으로 2번노드에도 배포된 것을 보실 수 있습니다.  

----