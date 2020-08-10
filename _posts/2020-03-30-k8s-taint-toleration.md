---
title: "Kubernetes taint & toleration"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Kubernetes
last_modified_at: 2020-03-30T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Kubernetes의 taint와 toleration 옵션에 대해 알아보겠습니다.  

# Taint & Toleration
- **taint** : 노드마다 설정가능. 설정한 노드에는 pod이 스케줄되지 않음
- **toleration** : taint를 무시할수있음

주로 노드를 지정된 역할만 하게할때 사용합니다.  
예를들어 gpu잇는 노드에는 다른 pod들은 올라가지않고 gpu쓰는 pod들만 올라가게 하는등의 상황에 사용할 수 있습니다.  

taint에는 사용할 수 있는 3가지 옵션이 있습니다.  
- `NoSchedule` : toleration이 없으면 pod이 스케쥴되지 않음, 기존 실행되던 pod에는 적용 안됨
- `PreferNoSchedule` : toleration이 없으면 pod을 스케줄링안하려고 하지만 필수는 아님, 클러스터내에 자원이 부족하거나 하면 taint가 걸려있는 노드에서도 pod이 스케줄링될 수 있음
- `NoExecute `: toleration이 없으면 pod이 스케줄되지 않으며 기존에 실행되던 pod도 toleration이 없으면 종료시킴.

taint 형식은 다음과 같습니다.  
~~~sh
$ kubectl taint node {nodename} {key}={value}:{option}
~~~

적용하게 되면 node describe에 Taints항목을 확인할수있다.  
~~~sh
$ kubectl taint node kube-n01 key1=value1:NoSchedule

node/kube-n01 tainted
~~~
![image](https://user-images.githubusercontent.com/15958325/77879563-a90b3900-7295-11ea-8556-f2aa83ab640e.png)  

## 실습
그럼 이제 Daemonset으로 pod을 띄워보겠습니다.  

>**DaemonSet?**  
>모든 노드에 pod을 띄우는 컨트롤러  

환경 :  
실습에 사용한 클러스터는 마스터1개 노드2개로 구성되었으며,  
taint는 1번노드(kube-n01)에 걸려있습니다.  


~~~sh
$ kubectl apply -f daemonset.yaml


$ kubectl get pod

NAME                          READY   STATUS    RESTARTS   AGE
fluentd-elasticsearch-6p6bc   1/1     Running   0          12s
~~~

pod은 하나만 뜨고, 자세히 살펴보면 2번노드(kube-n02)에 떠있는걸 확인할 수 있습니다.     
~~~sh
$ kubectl describe pod fluentd-elasticsearch-6p6bc

Name:         fluentd-elasticsearch-6p6bc
Namespace:    default
Priority:     0
Node:         kube-n02/10.73.138.219
…..
~~~

이번엔 pod에 toleration옵션을 줘서 다시 배포해보겠습니다.  

`spec.template.spec` 밑에 toleration옵션을 주도록 합니다.  
~~~sh
...
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
      - key: key1
        operator: Equal
        value: value1
        effect: NoSchedule
...
~~~


> **주의해야할 점 :**   
> **key**: 설정한 taint label의 `key`를 입력  
> **operator**: `Equal`은 key와 value effect가 모두 일치하는지 확인, `Exists`는 어떤 taint를 갖고있든지 무시  
> **value**: 설정한 taint label의 `value`  
> **effect**: 설정한 taint의 `option`


수정해서 배포 :  
~~~sh
$ kubectl apply -f daemonset.yaml

daemonset.apps/fluentd-elasticsearch configured
~~~

pod리스트를 확인해보면 두군데 전부 뜬것을 확인할 수 있습니다.  
~~~sh
$ kubectl get pod

NAME                          READY   STATUS    RESTARTS   AGE
fluentd-elasticsearch-b46tl   1/1     Running   0          14s
fluentd-elasticsearch-nqbvw   1/1     Running   0          5s
~~~

적용한 Taint를 삭제하려면 "-"를 붙여줍니다.    
~~~sh
$ kubectl taint node kube-n01 key1=value1:NoSchedule-

node/kube-n01 untainted
~~~

## 추가) Master node Scehdulable하게 바꾸기
기본적으로 Master노드에는 pod이 스케줄되지않게 taint가 걸려있습니다.  

해제방법:  
~~~sh
$ kubectl taint nodes {해제할 노드 이름} node-role.kubernetes.io/master-
~~~


----