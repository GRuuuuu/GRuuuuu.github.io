---
title: "Power-x86 Kubernetes Cluster"
slug: power-x86-k8s
tags:
  - Container
  - Cloud
  - Kubernetes
  - Power
date: 2020-02-10T13:00:00+09:00
---

## Overview
쿠버네티스 클러스터를 고객 요건에 따라 x86과 Power가 혼합된 멀티클라우드로 구성해야 될 때도 있습니다. 본 포스팅에서는 이런 구성이 과연 가능한지 검증하고, 또 구성 과정이 x86 기반 인프라와 비교하여 무엇이 달라지는지 살펴보고자 합니다.  

이런 목적을 가지고 이기종간의 쿠버네티스 클러스터 구성과, pod scheduling을 통해 특정 노드에 pod을 배포하는 방법에 대해서 다루겠습니다.  

>**Background++**  
>구글도 인정한 Power9의 가치 : [What's New at GCP: IBM Power Systems Service, Premium Support, Kubernetes Engine Benchmark](https://virtualizationreview.com/articles/2020/01/16/gcp-roundup.aspx)  
>
>"For organizations using a hybrid cloud strategy, especially, IBM Power Systems are an important tool," Google said. **"Because of their performance and ability to support mission critical workloads"**


# Prerequisites
해당 포스팅의 클러스터 환경은 다음과 같습니다.  

**Master**   
`os: CentOS v7.7`  
`arch: x86_64`  

**Worker1**  
`os: CentOS v7.7`  
`arch: x86_64`  

**Worker2**   
`os: RHEL v8.1`  
`arch: ppc64le`  

# Creating Cluster
이기종 간의 클러스터 구성에 있어서 기존방법과의 차이는 **없습니다**.  

>다음 링크의 **step**을 따라서 구성해주시면 됩니다.  
> [Install Kubernetes on CentOS/RHEL - Steps](https://gruuuuu.github.io/cloud/k8s-install/#3-steps)  

워커노드가 될 `Power`노드에 다른`x86`노드와 같이 `kubelet`, `kubectl`, `kubeadm등` kubernetes를 실행시키는데 필수요소들을 설치해주면 됩니다.([step-3.8](https://gruuuuu.github.io/cloud/k8s-install/#38-kubelet-kubeadm-kubectl-%EC%84%A4%EC%B9%98-mn) 참조)  

`kubeadm join~` 을 통해 아주 간단히 클러스터를 구성할 수 있습니다.([step-3.10](https://gruuuuu.github.io/cloud/k8s-install/#310-node-join-n) 참조)    
![image](https://user-images.githubusercontent.com/15958325/73814069-56794780-4825-11ea-9abd-5c39fce267ff.png)  

테스트할 앱은 오픈소스 `ngnix`에 포함되어 있는 index.html에  "TEST PAGE!" 문자열을 추가하여 아래 화면과 같이 보이도록 수정한 것입니다.  
![image](https://user-images.githubusercontent.com/15958325/73818133-094ea300-4830-11ea-8af8-3eee5bfb0a00.png)   

아래 Managing Cluster 챕터에서 이 앱을 제작하고, worker노드중 Power노드를 지정하여 배포해보겠습니다.  

# Managing Cluster
x86과 Power를 혼합해서 클러스터를 구성하였기 때문에, 해당 worker 노드에서 실행되는 pod는 개발노드와 architecture가 일치하여야 합니다.  

따라서 마스터에서 pod을 배포할 때, **타겟하는 worker 노드의 아키텍처가 무엇인지**를 지정하여  배포해야합니다.  

이번챕터에서 실습할 내용을 그림으로 나타내면 다음과 같습니다.  
![Picture1](https://user-images.githubusercontent.com/15958325/74129452-ea328580-4c22-11ea-9e24-169805bac79d.png)

1. Power 개발 서버에서 Power용 docker 이미지를 캡처한 뒤, 그 이미지를 docker에 push  
2. 클러스터의 워커노드 중, Power노드에 pod을 배포  

## 1. ppc64le용 이미지 제작 & Docker push
기존 Power 서버에서 운영되는 서비스들은 변경없이 현재의 런타임 이미지를 그대로 쿠버네티스 환경으로 이식할 가능성이 높습니다.  

이런 관점에서, 실습에서 사용할 이미지는 [Linux 서버 통째로 Dockerizing하기](https://gruuuuu.github.io/cloud/linux-dockerlizing/)에서 만든 `ppc64le`용 이미지입니다.  
(ubuntu베이스에 nginx서비스를 올린 이미지)   

링크를 따라 이미지를 빌드하고, docker 에 push해주시기 바랍니다.  

~~~sh
$ sudo docker push kongru/dockerize:base
~~~
![image](https://user-images.githubusercontent.com/15958325/73717723-ee136300-475d-11ea-9d9a-12d4e0dfbb39.png)  


## 2. Power 노드에 pod 배포
현재 클러스터의 워커노드는 x86과 Power가 혼합된 멀티 클러스터입니다.  

때문에 위에서 만든 이미지(`ppc64le`)를 배포하려면 워커노드 중 Power노드를 특정지어 배포해주어야 합니다.  

이 때 특정 노드에 pod을 배포하는 기능을 pod scheduling이라고 합니다.  

쿠버네티스의 pod scheduling에는 두가지 방법이 있는데 그 중 해당 실습에서는 `node Affinity`를 사용하여 scheduling해보겠습니다.  

### 2.1 node labeling
먼저 각 노드를 식별하기위해 label을 붙여줍니다.  
~~~sh
# kubectl label nodes <node-name> <label-key>=<label-value> 
$ kubectl label nodes kube-n01 arch=x86
$ kubectl label nodes p1220-kvm1 arch=ppc64le
~~~

label 붙은것 확인 :  
~~~sh
$ kubectl get nodes --show-labels
~~~
![image](https://user-images.githubusercontent.com/15958325/73817413-300bda00-482e-11ea-92f7-7db246c6b166.png)  

> label의 삭제는 "-"로 가능합니다.  
>~~~sh
>$ kubectl label nodes <node-name> <label-key>-
>~~~


### 2.2 node Affinity
>`nodeSelector` 대비 더 Rich한 표현식으로 노드를 선택하는 방법입니다.  
>k8s는 `Affinity`를 권장하고 있으며, `nodeSelector`는 `node affinity`로 훗날 대체될 예정이라고 합니다.  

총 4가지 옵션으로 표현식을 만들 수 있습니다.  
- `required` : 조건을 반드시 충족해야함 
- `preferred` : 조건을 충족할 수 있으면 하고 아니면 다른곳에 배포
- `IgnoredDuringExecution` : Runtime에 Node label이 바뀌어도 무시
- `RequiredDuringExecution` : Runtime에 Node label이 바뀌어서는 안되며 조건에 충족해야함

아래와 같이 총 4가지 표현식을 사용할 수 있습니다.  
`requiredDuringSchedulingIgnoredDuringExecution`  
`preferredDuringSchedulingIgnoredDuringExecution`  
`requiredDuringSchedulingRequiredDuringExecution`  
`preferredDuringSchedulingRequiredDuringExecution`  

또한 다음 operator를 사용해서 key:value간의 관계를 폭넓게 다룰 수 있습니다.  

>**사용가능한 operator의 종류** 
>- In 
>- NotIn
>- Exists
>- DoesNotExist
>- Gt
>- Lt
>
> `NotIn`과 `DoesNotExist`는 Node에 pod을 배포하지 못하게 하는 `antiAffinity`와 같은 역할을 합니다.  

위의 표현식을 참고하여 yaml파일을 작성해줍니다.  
~~~yaml
# ubuntu-nginx.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ubuntu-nginx
  labels:
    app: ubuntu-nginx
spec:
  selector:
    matchLabels:
      app: ubuntu-nginx
  template:
    metadata:
      labels:
        app: ubuntu-nginx
    spec:
      containers:
      - name: ubuntu-nginx
        image: kongru/dockerize:base
        ports:
        - containerPort: 80
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: arch
                operator: In
                values:
                - ppc64le
~~~

pod을 배포합니다.  
~~~sh
$ kubectl apply -f ubuntu-nginx.yaml
~~~
pod의 세부사항을 살펴보면 원하는 노드에 올라간 것을 확인할 수 있습니다.  
~~~sh
$ kubectl describe pod ubuntu-nginx-....
~~~
![image](https://user-images.githubusercontent.com/15958325/73821826-21c2bb80-4838-11ea-8f43-fea7eb94cd7a.png)  

제대로 pod이 작동하는지 확인해보겠습니다.  

pod의 서비스를 오픈해줍니다.  
~~~sh
$ kubectl expose pod ubuntu-nginx-....
~~~
![image](https://user-images.githubusercontent.com/15958325/73817959-95ac9600-482f-11ea-82b4-25b50afd1c70.png)   

서비스가 오픈되었으면 svc의 타입을 NodePort로 변경:   
(참고링크 : [service type 변경 방법](https://gruuuuu.github.io/cloud/k8s-install/#44-service-type-%EB%B3%80%EA%B2%BD))  
![image](https://user-images.githubusercontent.com/15958325/73817964-97765980-482f-11ea-95ac-b5c648524619.png)   

ip:port로 접근해보면 다음과 같이 페이지를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73818133-094ea300-4830-11ea-8af8-3eee5bfb0a00.png)  

>**참고 :**  
>원래 NodePort로 서비스를 오픈하게 되면 클러스터 내의 모든 ip로 접근이 가능하지만, NodeSelector로 특정 노드를 지정한 경우에는 해당 노드의 ip로만 접근이 가능합니다.  

# 한줄정리
- 이기종간의 쿠버네티스 클러스터 구성은 가능하다 (쉽다)
- `Affinity` : 배포시, 원하는 노드를 지정해주는 방식. 다양한 operator와 표현식으로 상세한 조건식 표현이 가능  
- 이기종간 클러스터 구성과 Pod Scheduling을 통해 좀 더 유연한 클러스터 운영을 기대할 수 있음

----