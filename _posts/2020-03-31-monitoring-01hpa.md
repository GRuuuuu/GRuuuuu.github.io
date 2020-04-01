---
title: "Kubernetes Monitoring - HPA 실습"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Kubernetes
  - Monitoring
last_modified_at: 2020-03-31T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
쿠버네티스 클러스터에서 hpa를 적용해 시스템 부하상태에 따라 pod을 autoScaling시키는 실습을 진행하겠습니다.  

참고 링크 : [Kubernetes.io/Horizontal Pod Autoscaler](https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale/)

# Prerequisites
먼저 쿠버네티스 클러스터를 생성해주세요.  

참고링크 : [호롤리한하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)  

> 본 실습에서 사용한 spec :   
>`OS : CentOS v7.6`  
>`Arch : x86` 
>
>`Kubernetes` : `v1.16.2`  
>`Master` : 4cpu, ram16G (1개)  
>`Node` : 4cpu, ram16G (2개)  

# Step
![그림1](https://user-images.githubusercontent.com/15958325/77894469-483d2a00-72b0-11ea-8aaf-dc8a8bcb07fc.png)  
## 1. Metrics-Server 배포
먼저 top명령어를 입력해봅시다.  
~~~sh
$ kubectl top node

Error from server (NotFound): the server could not find the requested resource (get services http:heapster:)
~~~
현재는 에러메세지가 뜹니다.  
이유는 노드의 system metric들을 수집하는 서비스가 없기 때문입니다.  

system metric을 수집하는 **Metrics-Server**를 배포해주도록 합시다.  

~~~sh
$ git clone https://github.com/kubernetes-sigs/metrics-server.git
$ cd metrics-server
~~~
쿠버네티스에서 공식으로 서포트하고있는 add-on 컴포넌트인 metrics-server를 클론받고, 배포하기 이전에 yaml파일을 수정해주어야합니다.  
클러스터 내에서 사용하는 인증서가 신뢰되지 않은 경우와 호스트 이름을 찾지 못하는 경우를 방지하기 위함입니다  

~~~
$ vim deploy/kubernetes/metrics-server-deployment.yaml
~~~

![image](https://user-images.githubusercontent.com/15958325/77997237-02dd3300-736a-11ea-8027-b3190b641509.png)  
위 그림과 같이 argument들을 수정해줍니다.  
~~~sh
args:
  - --kubelet-insecure-tls
  - --kubelet-preferred-address-types=InternalIP
  - --cert-dir=/tmp
  - --secure-port=4443
~~~

그리고 나서 metrics-server를 배포하면 :  
~~~sh
$ kubectl apply -f deploy/kubernetes/

clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator created
rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader created
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created
serviceaccount/metrics-server created
deployment.apps/metrics-server created
service/metrics-server created
clusterrole.rbac.authorization.k8s.io/system:metrics-server created
clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server created
~~~
중간에 metrics.k8s.io라는 API가 생성되어 Api server에 등록된 것을 확인할 수 있습니다.  

이제 top명령어를 사용할 수 있게 됩니다.  
~~~sh
$ kubectl top nodes

NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
kube-m     248m         6%     1656Mi          10%
kube-n01   112m         2%     760Mi           4%
kube-n02   112m         2%     724Mi           4%
~~~
각 노드의 cpu와 memory사용량을 확인할 수 있습니다.  

## 2. 부하테스트를 위한 이미지 작성
이제 시스템의 부하테스트를 위한 이미지를 작성해보겠습니다.  

~~~sh
$ mkdir php
cd php
~~~

스크립트 작성  :  
~~~sh
$ vim index.php

<?php
  $x = 0.0001;
  for ($i = 0; $i <= 1000000; $i++) {
    $x += sqrt($x);
  }
  echo "OK!";
?>
~~~

스크립트를 포함하는 도커 이미지 작성 :   
~~~sh
$ vim Dockerfile

FROM php:5-apache
ADD index.php /var/www/html/index.php
RUN chmod a+rx index.php
~~~

도커 이미지 빌드 :  
~~~sh
$ docker build --tag {docker id}/php-apache .

$ docker images |grep php

kongru/php-apache                    latest              39e1797ad29c        23 seconds ago      355MB
~~~

생성한 이미지를 본인의 docker hub에 push해줍니다.  
~~~sh
$ docker login
...
Login Succeeded

$ docker push kongru/php-apache
~~~

부하테스트를 위해 쿠버네티스 클러스터에 pod으로 배포해줍니다.  
~~~sh
$ vim hpa-test.yaml
~~~

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  selector:
    matchLabels:
      run: php-apache
  replicas: 1
  template:
    metadata:
      labels:
        run: php-apache
    spec:
      containers:
      - name: php-apache
        image: kongru/php-apache
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
          requests:
            cpu: 200m
---
apiVersion: v1
kind: Service
metadata:
  name: php-apache
  labels:
    run: php-apache
spec:
  ports:
  - port: 80
  selector:
    run: php-apache
~~~

yaml을 작성한 뒤에는 배포!  
~~~sh
$ kubectl apply -f hpa-test.yaml

deployment.apps/php-apache created
service/php-apache created
~~~

## 3. HPA 배포
이제 오토스케일러를 생성해주면 됩니다.  

~~~sh
$ vim autoscaler.yaml
~~~
위에서 만든 부하테스트용 pod인 php-apache의 평균 cpu사용량을 50%로 맞추기 위해 레플리카의 개수를 늘리고 줄입니다. (1개~10개)  
~~~yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
~~~

~~~sh
$ kubectl apply -f autoscaler.yaml
horizontalpodautoscaler.autoscaling/php-apache created
~~~

`hpa`커맨드를 통해 현재 hpa에 감지되는 시스템 부하정도와 관리하는 pod의 개수를 확인할 수 있습니다.  
~~~sh
$ kubectl get hpa
NAME         REFERENCE               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   0%/50%    1         10        1          18s
~~~
아직은 서버로 어떠한 요청도 하지 않았기 때문에, 현재 cpu소비량은 0%임을 알 수 있습니다. (`TARGET`은 deployment에 의해 제어되는 pod들의 평균을 뜻합니다.)  

## 부하테스트

부하가 증가함에 따라 오토스케일러가 어떻게 반응하는지 살펴보겠습니다.

창을 하나 더 띄워서 php-apache 서비스에 무한루프 쿼리를 전송합니다.  
~~~sh
$ kubectl run --generator=run-pod/v1 -it --rm load-generator --image=busybox /bin/sh

If you don't see a command prompt, try pressing enter.
/ #
/ # while true; do wget -q -O- http://php-apache.default.svc.cluster.local; done
OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!...
~~~

1~2분 지난 뒤에 `hpa`커맨드로 부하상태를 살펴보면 `TARGET`의 수치가 높아진 것을 확인할 수 있습니다.  
~~~sh
$ kubectl get hpa

NAME         REFERENCE               TARGETS    MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   248%/50%   1         10        1          9m7s
~~~

그리고 deployment 컨트롤러를 확인해보면 pod의 replica수가 5개까지 늘어난 것을 확인할 수 있습니다.  
~~~sh
$ kubectl get deploy php-apache

NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   5/5     5            5           12m
~~~

`busybox`컨테이너를 띄운 터미널에서 Ctrl+C로 부하 발생을 중단시키고, 몇 분 후에 결과를 확인합니다.  
~~~sh
$ kubectl get hpa

NAME         REFERENCE               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   0%/50%    1         10        5          11m
~~~
cpu의 사용량이 0%까지 떨어졌고, deployment의 pod replica수도 1개로 줄어든 것을 확인할 수 있습니다.  
~~~sh
$ kubectl get deploy php-apache

NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   1/1     1            1           19m
~~~

> replica autoscaling은 몇 분 정도 소요됩니다. (체감상 3~5분)  

----