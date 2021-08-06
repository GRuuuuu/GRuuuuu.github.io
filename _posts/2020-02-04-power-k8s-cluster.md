---
title: "이기종 쿠버네티스 클러스터 구성 및 Pod Scheduling"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Kubernetes
  - Power
last_modified_at: 2020-02-04T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
쿠버네티스 클러스터를 필요에 따라 `x86`과 `Power`등 서로다른 인프라가 혼합된 멀티클라우드로 구성해야 될 때도 있습니다. 본 포스팅에서는 이런 구성이 가능한지 검증하고, 또 구성 과정이 x86 기반 인프라와 비교하여 무엇이 달라지는지 살펴보고자 합니다.   

이런 목적을 가지고 이기종간의 쿠버네티스 클러스터 구성과, `pod scheduling`을 통해 특정 노드에 pod을 배포하는 방법에 대해서 다루겠습니다.  

> (21.08.06)  
>`Node Affinity` 수정 (`RequiredDuringExecution` 현재 지원 x)

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

# Kubernetes Installation
가장 먼저 클러스터를 구성하려면 쿠버네티스를 설치해주어야 합니다.  

## Kubernetes on x86
이미 이전 포스팅에서 기술했으므로 다음 링크를 참고하시면 됩니다.  
-> [Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)

## Kubernetes on Power9
Power서버도 과정자체는 동일합니다.   
하나 다른 점은 쿠버네티스를 설치할 repo파일을 구성할 때, baseurl만 바꿔주시면 됩니다. 
 
~~~sh
$ cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-ppc64le
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
~~~

> 혹시 Power가 아닌 다른 Architecture라면 해당 링크 : [https://packages.cloud.google.com/yum/repos](https://packages.cloud.google.com/yum/repos) 를 참고해서 `baseurl`을 바꿔주시면 됩니다.  

## Creating Cluster
마스터노드(`x86`)에서 `kubeadm init~`으로 클러스터를 구성하고, `kubeadm join`을 통해 각 워커노드(`x86`,`ppc64le`)에서 클러스터에 join합니다.  

마스터에서 join된 것 확인 :   
![image](https://user-images.githubusercontent.com/15958325/73813498-83c4f600-4823-11ea-9816-106a8285b720.png)  

![image](https://user-images.githubusercontent.com/15958325/73814069-56794780-4825-11ea-9abd-5c39fce267ff.png)


# Managing Cluster
클러스터가 구성이 되었으니, 테스트용도로 pod을 배포해보아야겠죠.  

간단한 nginx앱을 두 노드 모두 배포해보겠습니다.  
~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 2
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
        image: "nginx"
        ports:
        - containerPort: 80
~~~

사실 여기서 Power노드에는 pod이 배포되지 않을것이라고 생각했습니다.  
Architecture레벨에서 달랐기 때문입니다.  

**예상한 결과 :**   
- Master는 `x86`이니 `x86`용이미지를 노드에 배포할 것.
- 고로 power노드에는 이미지가 올라가지 않을 것이다.  

**실제 결과 :**  
![image](https://user-images.githubusercontent.com/15958325/73814586-dbb12c00-4826-11ea-9740-eae0343642b8.png)   
![댕](https://user-images.githubusercontent.com/15958325/73814820-7c075080-4827-11ea-9a59-d37aa854d365.png)  

있을 수 없는 일이 일어나서 잠시 쿠버네티스가 x86용 이미지를 ppc64le용으로 자동 포팅을 한건가...? 라는 생각도 했었습니다.  

물론 그런건 없습니다.   

사실 굉장히 단순한 이유입니다.  

pod을 배포할 때의 단계는   
1. Pod Scheduling -> pod을 배포할 node를 선택
2. **(중요)** 선택된 node에서 docker pull
3. 선택된 node에서 pod Creating & Starting


순으로 pod이 배포되는데, 2번단계에서 볼 수 있듯이, 마스터에서 이미지를 pull받아 배포하는 방식이 아니라 **각 노드에서 각각 이미지를 pull받아서 pod을 생성**하는 것이기 때문에 각 architecture에 맞는 이미지를 pull받을 수 있는 것입니다.  

크게 그림으로 보면 다음과 같습니다.  
![Picture1](https://user-images.githubusercontent.com/15958325/74113653-f7328300-4be8-11ea-81f7-6f43172b40a1.png)    
  
Docker Hub를 비롯한 컨테이너 레지스트리에 배포하고자 하는 **Node의 Architecture와 일치하는 이미지**가 있다면 해당 이미지를 pull 받아 pod을 생성할 수 있습니다.  

만약 이미지를 pull받을 registry자체에 원하는 Architecture의 이미지가 없다면 에러가 나게 됩니다.   

위 테스트에서 사용했던 nginx는 Docker Hub에 다양한 Architecture에서 빌드한 이미지가 있었고,   
x86과 Power용 빌드버전이 있었기 때문에 클러스터의 두 노드에 성공적으로 배포될 수 있었던것입니다.  
![image](https://user-images.githubusercontent.com/15958325/73815357-0f8d5100-4829-11ea-8582-3ab4657e9a3e.png)  


# Pod Scheduling
위의 테스트에서는 nginx앱을 두 개의 노드에 배포해보았습니다.  

하지만 위처럼 컨테이너 레지스트리에 nginx가 여러 Architecture의 빌드이미지가 있는 경우도 있지만, **하나의 Architecture로만 빌드된 이미지를 이기종 클러스터에 배포**해야될 경우도 존재할 수 있습니다.  

이 때에는 **pod을 원하는 Node에 배포**할 수 있게 하는 기능이 필요합니다.   
쿠버네티스에서는 해당 기능을 **pod scheduling**이라고 합니다.  

꼭 이기종간의 클러스터구성에서만 유용한 것이 아니라 **다른 스펙을 가진 서버들끼리 클러스터를 구성**했을 때도 유용하게 사용될 수 있습니다.  

pod scheduling에는 `nodeSelector`와 `Affinity`로 두가지 방법이 있습니다.  

>**-중요-**  
>아래 실습에서 사용하는 이미지는 [Linux 서버 통째로 Dockerizing하기](https://gruuuuu.github.io/cloud/linux-dockerlizing/)에서 만든 `ppc64le`용 이미지입니다.  
>(ubuntu베이스에 nginx서비스를 올린 이미지)     
>
>아래 실습을 따라하실 분께서는 해당링크를 통해 이미지를 만들고 docker hub에 push해주시기 바랍니다.  


## 1. nodeSelector
첫번째는 노드에 labeling을 하여 **label을 기준으로 노드를 고르는 방법**입니다.  

먼저 각 노드의 label을 붙여줍니다.  
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

각 노드의 식별자가 생겼으니, 테스트로 `ppc64le`용 이미지를 power노드에 배포해보겠습니다.  

spec의 `nodeSelector` 옵션을 통해 `<key>:<value>`의 형식으로 원하는 노드의 label을 기재해 줍니다.  

~~~yaml
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
      nodeSelector:
        arch: ppc64le
~~~

~~~sh
$ kubectl apply -f ubuntu-nginx.yaml
~~~
![image](https://user-images.githubusercontent.com/15958325/73818026-b4ab2800-482f-11ea-8daf-b8285b88f9af.png)   
~~~sh
$ kubectl expose pod ubuntu-nginx-75575577c4-knlz5
~~~
![image](https://user-images.githubusercontent.com/15958325/73817959-95ac9600-482f-11ea-82b4-25b50afd1c70.png)   

서비스가 오픈되었으면 svc의 타입을 NodePort로 변경:   
![image](https://user-images.githubusercontent.com/15958325/73817964-97765980-482f-11ea-95ac-b5c648524619.png)   

ip:port로 접근해보면 다음과 같이 페이지를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73818133-094ea300-4830-11ea-8af8-3eee5bfb0a00.png)  

>**참고 :**  
>원래 NodePort로 서비스를 오픈하게 되면 클러스터 내의 모든 ip로 접근이 가능하지만, NodeSelector로 특정 노드를 지정한 경우에는 해당 노드의 ip로만 접근이 가능합니다.  

## 2. Node Affinity
`nodeSelector` 대비 더 Rich한 표현식으로 노드를 선택하는 방법입니다.  
k8s는 `Affinity`를 권장하고 있습니다.  
`nodeSelector`는 `node affinity`로 훗날 대체될 예정이라고 합니다.  

총 4가지 옵션으로 표현식을 만들 수 있습니다.  
- required : 조건을 반드시 충족해야함 
- preferred : 조건을 충족할 수 있으면 하고 아니면 다른곳에 배포
- IgnoredDuringExecution : Runtime에 Node label이 바뀌어도 무시
- RequiredDuringExecution : Runtime에 Node label이 바뀌어서는 안되며 조건에 충족해야함

아래와 같이 총 2가지 표현식을 사용할 수 있습니다.  
`requiredDuringSchedulingIgnoredDuringExecution`  
`preferredDuringSchedulingIgnoredDuringExecution`  

> 아래 2가지 표현식은 추후 지원 예정:  
>`requiredDuringSchedulingRequiredDuringExecution`  
>`preferredDuringSchedulingRequiredDuringExecution`  

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

표현식과 operator들로 `nodeSelect`보다 유연하게 조건식을 작성할 수 있습니다.

위와 똑같은 조건으로 yaml파일을 구성해 보겠습니다.   
위의 yaml파일에서 `nodeSelect`부분을 날리고 다음 `affinity`로 치환하시면 됩니다.   

~~~yaml
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

pod을 배포한 뒤 해당 pod의 상세내용을 살펴보면 원하는 노드에 pod이 올라간 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73821826-21c2bb80-4838-11ea-8f43-fea7eb94cd7a.png)  


# 한줄정리
- 이기종간의 쿠버네티스 클러스터 구성은 가능하다 (쉽다)
- `nodeSelect` : 배포를 원하는 노드를 지정해주는 방식
- `Affinity` : nodeSelect와 비슷한 역할이지만, 다양한 operator와 표현식으로 더 상세한 조건식 표현이 가능

끝!

----