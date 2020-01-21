---
title: "Helm 3 설치 & 기본 사용방법"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Helm
last_modified_at: 2019-12-14T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 **Helm**의 사용법에 대해서 알아보겠습니다.

## 2. Prerequisites
- 쿠버네티스 클러스터가 깔려있어야 합니다.  
-> [호롤리한 하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/container/k8s-install/) 참고.

- helm을 설치할 위치에서 kubectl 명령어를 사용할 수 있어야 합니다.  

# 3. Helm이란?
Helm은 쿠버네티스의 **package managing tool**입니다.  

크게 세가지 컨셉을 가지고 있는데 :  
1. **Chart** : Helm package입니다. app을 실행시키기위한 모든 리소스가 정의되어있습니다.  
`Homebrew formula`, `Apt dpkg`, `Yum RPM`파일과 비슷하다고 생각하시면 됩니다.  
2. **Repository** : chart들이 공유되는 공간입니다. `docker hub`를 생각하시면 될 것 같습니다.  
3. **Release** : 쿠버네티스 클러스터에서 돌아가는 app들은(chart instance) 모두 고유의 release 버전을 가지고 있습니다.  

다시 정리하면,  
helm은 **chart**를 쿠버네티스에 설치하고, 설치할때마다 **release**버전이 생성되며, 새로운 chart를 찾을때에는 Helm chart **repository**에서 찾을 수 있습니다.  

>**주의!**  
>이 문서는 helm v3.0.0 이상을 다루고 있습니다.  
>2.x버전과 많은것이 변경되었기 때문에 참고해주시기 바랍니다.  

# 4. Installation
kubectl을 사용할 수 있는 노드로 이동하여 설치합니다.  
~~~sh
$ curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
$ chmod 700 get_helm.sh
$ ./get_helm.sh
~~~

버전 확인 :  
~~~sh
$ helm version
~~~
![image](https://user-images.githubusercontent.com/15958325/70848110-26aa6500-1eb0-11ea-8da2-2ccaa9dc4ba2.png)  

helm chart repository를 추가해줍니다.  
~~~sh
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/
~~~

chart list 출력 :  
~~~sh
$ helm search repo stable
~~~
![image](https://user-images.githubusercontent.com/15958325/70848132-4e013200-1eb0-11ea-930c-1346603d48b1.png)  

chart update :  
~~~sh
$ helm repo update
~~~
![image](https://user-images.githubusercontent.com/15958325/70848135-5e191180-1eb0-11ea-9119-625b7decb370.png)  
**Happy Helming!**


# 5. 실습 (Prometheus)
설치가 끝났으니 한번 차트를 클러스터에 배포해봅시다.  

모니터링 툴 중 하나인 **Prometheus**를 배포해보겠습니다.  

~~~sh
$ helm install monitor stable/prometheus
~~~
![image](https://user-images.githubusercontent.com/15958325/70848161-ab957e80-1eb0-11ea-85fb-c25b5aee1c71.png)  

그런데 pod의 상태를 확인해보면 :  
~~~sh
$ kubectl get pod
~~~
![image](https://user-images.githubusercontent.com/15958325/70848166-ccf66a80-1eb0-11ea-8ad7-777e2acfb25e.png)  
몇 개의 pod이 **Pending**상태입니다.  

이유는 k8s클러스터에 StorageClass가 정의되어있지 않기 때문입니다.  
(pvc의 요청을 받아줄 provisioner가 없기 때문)  

그래서 일단 pv옵션을 false로 변경해주어 EmptyDir을 사용하게 해야 합니다.  

Helm chart의 설정을 변경하는 방법은 크게 두가지 방법이 있습니다.   
## using yaml
문제가 되는 chart를 먼저 확인해봅시다.  
~~~sh
$ helm inspect values stable/prometheus
~~~
![image](https://user-images.githubusercontent.com/15958325/70848197-3bd3c380-1eb1-11ea-9ccb-818be92e6318.png)  

`persistentVolume.enabled`가 `True`입니다. 이렇게 표기되어있는 부분이 총 세군데가 있습니다.  

수정할 부분만 따로 파일을 만들어주면 됩니다.  

~~~sh
$ vim volumeF.yaml
~~~
~~~yaml
alertmanager:
    persistentVolume:
        enabled: false
server:  
    persistentVolume:
        enabled: false
pushgateway: 
    persistentVolume:
        enabled: false
~~~

딱 이렇게만 적고 업그레이드해줍시다.  

~~~sh
$ helm upgrade -f volumeF.yaml monitor stable/prometheus
~~~

업그레이드 하게되면 Pending이었던 pod들이 Running상태로 변하는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/70848257-e4822300-1eb1-11ea-8cb5-3f9e9ac6365b.png)  

## using Command
다른 방법으로는 커맨드라인으로 설정을 추가해주는 방법이 있습니다.  

~~~yaml
outer:
  inner: value
~~~
위와 같은 표현식을 다음과 같이 표현할 수 있습니다.  
~~~sh
$ --set outer.inner=value
~~~

그럼 위 문제와 같은 경우는 다음과 같이 표현될 수 있습니다.  
~~~sh
$ helm install monitor stable/prometheus --set alertmanager.persistentVolume.enabled=false --set server.persistentVolume.enabled=false --set pushgateway.persistentVolume.enabled=false
~~~

----
pod들이 정상적으로 Running되었으니 웹으로 접속해봅시다.  

~~~sh
$ kubectl get svc
~~~
![image](https://user-images.githubusercontent.com/15958325/70848280-66724c00-1eb2-11ea-8bee-1d95daed1d7f.png)  

`prometheus-server`를 `clusterIP`에서 `NodePort`로 변경해줍니다.(`spec.type`)
~~~sh
$ kubectl edit svc monitor-prometheus-server
~~~

![image](https://user-images.githubusercontent.com/15958325/70848299-bfda7b00-1eb2-11ea-9ed6-441b0f362dbc.png)  
다시 확인해보면 포트포워딩된 포트가 보입니다.  

ip:port로 접속해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/70848302-d1238780-1eb2-11ea-88bf-3b6aaf36526c.png)  


## 삭제
삭제할때는 간단하게 설치할때 사용했던 이름만 사용하면 됩니다.  
~~~sh
$ helm uninstall {이름}
~~~

----
