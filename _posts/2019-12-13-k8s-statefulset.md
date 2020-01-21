---
title: "Kubernetes Controllers : StatefulSet"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Controller
last_modified_at: 2019-12-14T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 `Kubernetes`(k8s)의 Controller중, StatefulSet에 대해서 알아보겠습니다.   

## 2. Prerequisites

본문에서 사용한 spec :  
`OS : CentOS v7.6`  
`Arch : x86`  

k8s클러스터는 1마스터 2노드로 구성했습니다.  
`Master` : 4cpu, ram16G  
`Node` : 2cpu, ram4G  

# 3. StatefulSet
이전 포스팅에서 k8s의 여러 컨트롤러에 대해 알아봤었습니다. 이 컨트롤러들은 주로 상태가 없는(`stateless`) pod을 관리하는 용도로 사용됩니다.  
> 참고 : [호롤리한 하루/Kubernetes Controllers : Replication, Deployment, DaemonSet](https://gruuuuu.github.io/cloud/k8s-controllers/)


오늘 소개할 **StatefulSet Controller**는 이름에서 느껴지듯이 상태를 가지고 있는 pod들을 관리하는 용도로 사용됩니다.  

pod에 순서를 지정해서 지정한 순서대로 실행되게 할 수도 있으며, 볼륨을 지정해줘서 pod을 내렸다가 올려도 데이터가 유지되게 할 수 있습니다.  

## 실습

> **Static Provisioning**의 경우 :  
>미리 1G짜리 pv를 두개 만들어줍니다.  
>~~~yaml
>kind: PersistentVolume
>metadata:
>  name: pv
>spec:
>  capacity:
>    storage: 1Gi
>  accessModes:
>    - ReadWriteMany
>  nfs:
>    server: x.x.x.x
>    path: /.../mount/dir
>~~~
>![image](https://user-images.githubusercontent.com/15958325/70845527-1f289300-1e93-11ea-89dd-73b201a27779.png)  
>
>**Dynamic Provisioning**의 경우 :  
>[호롤리한 하루/Kubernetes Volumes : Static & Dynamic Provisioning](https://gruuuuu.github.io/cloud/k8s-volume/#%EC%8B%A4%EC%8A%B5--dynamic-provisioning-with-nfs)을 참고하여 storage class, provisioner까지 만든 후 부터 아래 실습을 진행해주세요.  

StatefulSet Controller를 생성해줍니다.  
~~~sh
$ vim statefulset-nginx.yaml
~~~

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  type: NodePort
  ports:
  - port: 80
    name: web
  clusterIP: 10.96.10.10
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 2
  selector:
    matchLabels:
      app: nginx          # ==spec.template.metadata.labels
  template:
    metadata:
      labels:
        app: nginx         # ==spec.selector.matchLabels
    spec:
      containers:
      - name: nginx
        image: k8s.gcr.io/nginx-slim:0.8
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: web-pvc
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: web-pvc
    spec:
      storageClassName: nfs-storageclass    # Static Provisioning의 경우에는 주석처리!
      accessModes: [ "ReadWriteMany" ]      # pv의 accessmode와 일치할것
      resources:
        requests:
          storage: 1Gi
~~~

배포!  
~~~sh
$ kubectl apply -f statefulset-nginx.yaml
~~~
![image](https://user-images.githubusercontent.com/15958325/70845644-8dba2080-1e94-11ea-8174-3b303f79d2ca.png)  

~~~sh
$ kubectl get pod
~~~
![image](https://user-images.githubusercontent.com/15958325/70845651-a0ccf080-1e94-11ea-9444-c7692b802763.png)  
pod이 생성될 때 0번부터 순차적으로 생성됩니다.  

볼륨이 제대로 바운드되었는지 확인 :  
~~~sh
$ kubectl get pv,pvc
~~~
![image](https://user-images.githubusercontent.com/15958325/70845684-e7224f80-1e94-11ea-90ca-f992d96ede0c.png)  

----
그럼 이번엔 서비스에 접속해봅시다.  
~~~sh
$ kubectl get svc
~~~
![image](https://user-images.githubusercontent.com/15958325/70845697-0620e180-1e95-11ea-9680-48969675d826.png)

ip:port로 접속!  
![image](https://user-images.githubusercontent.com/15958325/70845721-4718f600-1e95-11ea-8a87-784ba406881d.png)  
했는데 403에러가 발생합니다.  

이유는 바로 
~~~sh
$ for i in 0 1; do kubectl exec web-$i -- ls -a /usr/share/nginx/html; done
~~~
![image](https://user-images.githubusercontent.com/15958325/70845736-6ca5ff80-1e95-11ea-9582-5761663fcdc1.png)  

루트 html폴더가 비어있기 때문입니다.  

----
각 pod에 html파일을 하나씩 구성해줍시다.  

pod들의 `hostname`이 다르다는것을 이용해 0번노드로 접속하면 0번노드의 hostname이 뜨는 페이지가, 1번 노드로 접속하면 1번노드의 hostname이 뜨도록 페이지를 구성해보겠습니다.  

~~~sh
$ for i in 0 1; do kubectl exec web-$i -- sh -c 'hostname'; done
   web-0
   web-1

$ for i in 0 1; do kubectl exec web-$i -- sh -c 'echo $(hostname) > /usr/share/nginx/html/index.html'; done
~~~

이제 각 pod이 어떤 노드에 올라갔는지 확인해봅시다.  
~~~sh
$ kubectl describe pod web
~~~
![image](https://user-images.githubusercontent.com/15958325/70845973-11294100-1e98-11ea-8844-8f8149851a4b.png)  
![image](https://user-images.githubusercontent.com/15958325/70845976-138b9b00-1e98-11ea-8d13-d39c19347e17.png)  

**Node2:port :**  
![image](https://user-images.githubusercontent.com/15958325/70846007-6e24f700-1e98-11ea-9aeb-a80eda5fc82a.png)

**Node1:port :**   
![image](https://user-images.githubusercontent.com/15958325/70846017-8bf25c00-1e98-11ea-96df-8e235b56d799.png)

403에러가 나지 않고, 각 pod의 hostname이 출력되는 것을 확인할 수 있습니다.  

----
이번엔 pod을 삭제해보고 다시 올라왔을 때, 그대로 hostname이 출력되는지(volume이 제대로 바인딩되었는지)확인해봅시다.  

~~~sh 
$ kubectl delete pod -l app=nginx
~~~
![image](https://user-images.githubusercontent.com/15958325/70846069-f3a8a700-1e98-11ea-833d-69a78786b526.png)  

replication 옵션이라 조금만 기다리면 새로운 pod이 생성될 것입니다.  
![image](https://user-images.githubusercontent.com/15958325/70846076-07540d80-1e99-11ea-94ed-1065312d2ff9.png)  

다 running상태가 되면 웹으로 접속해봐서 hostname이 그대로 나오는지 확인해보시면 됩니다.  

## 나올수있는 에러
**웹으로 접속해봤는데 전부 같은 hostname이 나오는 경우 :**  

`Dynamic Provisioning`이 아니라 `Static Provisioning`을 사용할 때 할수있는 실수입니다.  

Static Provisioning은 provisioning을 수동으로 해줘야하기때문에 파일시스템의 마운트포인트를 다르게 해서 pv를 생성해줘야합니다.  

동일한 마운트 포인트를 사용할 경우, **같은 볼륨을 공유하는것**과 마찬가지입니다. 때문에 file이 **overwriting**되어서 같은 hostname이 보여지는 것입니다.  

**-->**  
수동으로 nfs에 폴더 두개를 만들어주고  
![image](https://user-images.githubusercontent.com/15958325/70846232-99a8e100-1e9a-11ea-9b7e-3d4fbeb4ccaf.png)  

pv생성할때 각각의 폴더로 마운트하게 설정을 해줍니다.  

**pv.yaml :**  
![image](https://user-images.githubusercontent.com/15958325/70846236-b9400980-1e9a-11ea-8e9b-512cd2b3ad39.png)  

**pv2.yaml :**  
![image](https://user-images.githubusercontent.com/15958325/70846243-cf4dca00-1e9a-11ea-8edd-1be30ad42de0.png)   

그럼 file overwriting같은 문제가 발생하지 않게됩니다.  

----