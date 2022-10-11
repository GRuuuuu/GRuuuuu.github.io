---
title: "default-scheduler  0/1 nodes are available: 1 node(s) didn't match pod anti-affinity rules."
categories: 
  - ERROR
tags:
  - Kubernetes
  - Infra
last_modified_at: 2022-10-11T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Environment
Openshift Cluster Single Node
~~~
$ oc get node
NAME           STATUS   ROLES           AGE    VERSION
10.178.105.3   Ready    master,worker   501d   v1.23.5+8471591
~~~

## ERROR
Operator에 하드코딩된 `replicas` 때문에 강제로 deployment의 `replicas`를 조정할 수 없는 경우에,  
Openshift Update와 같은 작업을 진행할 때 조건이 충족 안되서 다음 스텝으로 못넘어가는 문제  

~~~
default-scheduler  0/1 nodes are available: 1 node(s) didn't match pod anti-affinity rules.
~~~

## 원인
예시로 `openshift-console` project의 console pod는 replica가 2개임  
하지만 노드가 하나뿐이라 하나만 동작하고 나머지 하나는 Pending상태이다.  
Update시 Cluster Operator가 이를 비정상적인 상태로 파악해 다음 update step으로 넘어가지 않을 수 있음  
~~~
$ oc get pod
NAME                         READY   STATUS    RESTARTS   AGE
console-5fc44795b4-8krdn     0/1     Pending   0          78m
console-5fc44795b4-cg8rh     1/1     Running   0          107m
downloads-6c87f4dc86-fhbvp   0/1     Pending   0          78m
downloads-6c87f4dc86-fq2g9   1/1     Running   0          112m
~~~

`replicas`수를 조정해야하는데, deployment에서 조정해도 `console-operator`의 관리를 받기 때문에 다시 원복되는 현상이 반복됨.  

pod가 Pending되는 근본적인 원인은 아래 `podAntiAffinity`때문이고  
~~~yaml
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: component
            operator: In
            values:
            - ui
        topologyKey: kubernetes.io/hostname
~~~
`component: ui`라는 label을 가진 pod가 동일한 노드에 있으면 해당 노드에 뜨지 못하게 만듬.  


## Workaround
Operator를 속여서 label을 떼버렸다가 다시 붙여서 정상적인 상태로 보이게 해야함.  

### 1. Running pod의 label 제거
~~~
$ oc label pod console-5fc44795b4-cg8rh component-
pod/console-5fc44795b4-cg8rh unlabeled
~~~
제거하면 operator의 관리에서 벗어나기때문에 새로운 pod가 하나 더 생김
~~~
$ oc get pod
NAME                         READY   STATUS    RESTARTS   AGE
console-5fc44795b4-5pk82     0/1     Pending   0          58s
console-5fc44795b4-8krdn     0/1     Pending   0          86m
console-5fc44795b4-cg8rh     1/1     Running   0          115m
~~~

### 2. Pending pod중 하나의 label 제거
~~~
$ oc label pod console-5fc44795b4-8krdn component-
pod/console-5fc44795b4-8krdn unlabeled
~~~

이렇게 하면 operator의 관리 하의 Pending pod2개와 label이 제거되서 Running상태의 관리 밖의 pod 2개가 생김  
~~~
$ oc get pod
NAME                         READY   STATUS    RESTARTS   AGE
console-5fc44795b4-5pk82     0/1     Pending   0          2m15s
console-5fc44795b4-8krdn     1/1     Running   0          87m
console-5fc44795b4-cg8rh     1/1     Running   0          117m
console-5fc44795b4-ltrt9     0/1     Pending   0          30s
~~~

### 3. Running pod에 re-labeling
~~~
$ oc label pod console-5fc44795b4-8krdn component=ui
pod/console-5fc44795b4-8krdn labeled

$ oc label pod console-5fc44795b4-cg8rh component=ui
pod/console-5fc44795b4-cg8rh labeled
~~~

다시 라벨링을 했기 때문에 operator의 관리 하에 들어가게되고,  
~~~
$ oc get pod
NAME                         READY   STATUS    RESTARTS   AGE
console-5fc44795b4-8krdn     1/1     Running   0          89m
console-5fc44795b4-cg8rh     1/1     Running   0          118m
~~~
Running 상태의 pod2개만 남게된다.  

### 4. Operator상태 확인

~~~
$ oc get co
NAME                                       VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE   MESSAGE
console                                    4.10.32   True        False         False      95s
...
~~~
정상!   

----