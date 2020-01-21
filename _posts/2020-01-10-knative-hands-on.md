---
title: "Knative를 다뤄보자! (Serving, Eventing 실습)"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - MSA
  - ServiceMesh
  - Istio
  - Knative
last_modified_at: 2020-01-10T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Knative의 Serving기능과 Eventing기능을 실습을 통해 더 자세히 알아보겠습니다.  

본 포스트는 **Knative v0.11**을 기준으로 제작되었습니다.

> 참고 : [호롤리한하루/Knative란? (basic)](https://gruuuuu.github.io/cloud/knative/#)  

# Prerequisites
먼저 쿠버네티스 클러스터를 생성해주세요.  

> Kubernetes v1.14 이상이어야 합니다.  

참고링크 : [호롤리한하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)  

> 본 실습에서 사용한 spec :   
>`OS : CentOS v7.6`  
>`Arch : x86` 
>
>`Kubernetes` : `v1.16.2`  
>`Master` : 4cpu, ram16G (1개)  
>`Node` : 4cpu, ram16G (2개) 

Knative는 Istio위에 올라가기 때문에 Istio의 구성이 필수적입니다.  

> 참고 링크 : [호롤리한하루/Service Mesh Architecture & Istio를 알아보자](https://gruuuuu.github.io/cloud/service-mesh-istio/#install-istio)

`Istio` 패키지를 다운받습니다.  
~~~sh
$ curl -L https://git.io/getLatestIstio | sh -
$ cd istio-1.4.2/
~~~

그다음 Istio의 CRD(Custom Resource Definitions)를 적용시킵니다.  
~~~sh
$ for i in install/kubernetes/helm/istio-init/files/crd*yaml; do kubectl apply -f $i; done
~~~

Istio namespace생성  
~~~yaml
apiVersion: v1
kind: Namespace
metadata:
 name: istio-system
 labels:
   istio-injection: disabled
~~~

~~~sh
$ kubectl apply -f namespace.yaml
~~~

이제부터 추가로 생성하는 pod들에 대해 자동으로 envoy proxy를 삽입하기위해 sidecar injection을 활성화 해주고 istio를 배포합니다.     
~~~sh
# A template with sidecar injection enabled.
$ helm template --namespace=istio-system \
  --set sidecarInjectorWebhook.enabled=true \
  --set sidecarInjectorWebhook.enableNamespacesByDefault=true \
  --set global.proxy.autoInject=disabled \
  --set global.disablePolicyChecks=true \
  --set prometheus.enabled=false \
  `# Disable mixer prometheus adapter to remove istio default metrics.` \
  --set mixer.adapters.prometheus.enabled=false \
  `# Disable mixer policy check, since in our template we set no policy.` \
  --set global.disablePolicyChecks=true \
  --set gateways.istio-ingressgateway.autoscaleMin=1 \
  --set gateways.istio-ingressgateway.autoscaleMax=2 \
  --set gateways.istio-ingressgateway.resources.requests.cpu=500m \
  --set gateways.istio-ingressgateway.resources.requests.memory=256Mi \
  `# More pilot replicas for better scale` \
  --set pilot.autoscaleMin=2 \
  `# Set pilot trace sampling to 100%` \
  --set pilot.traceSampling=100 \
  install/kubernetes/helm/istio \
  > ./istio.yaml


$ kubectl apply -f istio.yaml
~~~

~~~sh
$ kubectl get pod --namespace=istio-system
~~~

![image](https://user-images.githubusercontent.com/15958325/72043566-dc70a400-32f4-11ea-877a-da8fa6877542.png)  

전부 Running 또는 Compleeted가 뜨면 성공입니다.  

>이제 마지막 체크만 하면 됩니다.  
>`istio-ingressgateway`의 `External-IP`가 정상적으로 출력되면 Knative 설치로 넘어가시면 됩니다.   
>
>`<pending>`인 경우 :   
>![image](https://user-images.githubusercontent.com/15958325/72128719-2326d280-33b7-11ea-969e-89e45387e2ed.png)   
>
>~~~sh
>$ kubectl edit svc istio-ingressgateway -n istio-system
>~~~
>type을 `LoadBalancer`에서 `NodePort`로 변경

# 3. Knative 설치
> 참고 : [Installing Knative](https://knative.dev/docs/install/)  

먼저 Knative의 CRD를 생성해줍니다.  
자잘한 에러 방지를 위해 `-l knative.dev/crd-install=true` 플래그를 추가해서 돌려줍니다.  

~~~sh
$ kubectl apply --selector knative.dev/crd-install=true \
--filename https://github.com/knative/serving/releases/download/v0.11.0/serving.yaml \
--filename https://github.com/knative/eventing/releases/download/v0.11.0/release.yaml \
--filename https://github.com/knative/serving/releases/download/v0.11.0/monitoring.yaml
~~~

>그럼에도 불구하고 아래와 같은 에러메시지가 뜬다면 :  
>~~~
>error: unable to recognize "https://github.com/knative/serving/releases/download/v0.11.0/serving.yaml": no matches for kind "Image" in version "caching.internal.knative.dev/v1alpha1"
>~~~
>
>위 명령어를 한번더 치면 됩니다.

Knative와 각종 의존성파일들을 설치완료 하기위해 `--selector` 플래그를 제거하고 다시 명령어를 입력해줍니다.  
~~~sh
$ kubectl apply --filename https://github.com/knative/serving/releases/download/v0.11.0/serving.yaml \
--filename https://github.com/knative/eventing/releases/download/v0.11.0/release.yaml \
--filename https://github.com/knative/serving/releases/download/v0.11.0/monitoring.yaml
~~~

pod들이 제대로 Running상태에 있는지 확인 :  
~~~sh
$ kubectl get pods --namespace knative-serving
$ kubectl get pods --namespace knative-eventing
$ kubectl get pods --namespace knative-monitoring
~~~

![image](https://user-images.githubusercontent.com/15958325/72126951-57979000-33b1-11ea-949a-1cdbd350075f.png)  

>몇몇 pod들이 `pending`상태라면 **메모리부족**일 가능성이 있습니다.  
> `insufficient cpu`에러가 떠서 클라우드의 리소스를 늘려줬더니 성공적으로 Running이 떴습니다.  



# 실습 - Serving
> 참고 : [Knative/Getting Started with App Deployment](https://knative.dev/docs/serving/getting-started-knative-app/)  

샘플 Application을 `Knative`의 **Serving**을 이용해 배포해보겠습니다.  

해당 샘플 app은 config파일에서 env변수를 읽고 "Hello World : ${TARGET}!"을 인쇄하는 기능을 가진 아주 간단한 appd입니다.   

먼저 다음과 같이 serving.yaml파일을 작성해줍니다.  
~~~yaml
apiVersion: serving.knative.dev/v1 # Current version of Knative
kind: Service
metadata:
  name: helloworld-go # The name of the app
  namespace: default # The namespace the app will use
spec:
  template:
    spec:
      containers:
        - image: gcr.io/knative-samples/helloworld-go # The URL to the image of the app
          env:
            - name: TARGET # The environment variable printed out by the sample app
              value: "Go Sample v1"
~~~

다른 쿠버네티스 yaml파일과 같이 `kubectl apply -f {filename}`을 써서 배포합니다.  

~~~sh
$ kubectl apply -f serving.yaml
~~~

서비스를 생성했습니다! 이제 Knative 내부에서는 다음 step을 진행할 것입니다.  
1. 사용자 app의 새로운 revision을 생성
2. app의 route, ingress, service, loadbalancer를 생성
3. 트래픽에 따라 pod을 올리거나 내림 (scale up-down)

이것만 봐서는 쉽게 이해가 안될것입니다.  
1번은 당연한거니 넘어가고, 2번부터 찬찬히 살펴보겠습니다.  

## 2. app의 route, ingress, service, loadbalancer를 생성
쿠버네티스에서 pod을 생성할 때를 떠올려봅시다.  
기본적으로 사용자는 pod만 생성해서는 app에 접근할 수 없습니다. 그래서 **별도로** `service`를 생성해주던지 `loadbalancer`를 설정해주거나 `ingress`를 만들었었고, 네트워크 설정이 필수 불가결 했습니다.  

반면에 Knative위에서의 배포는 서비스 컨테이너 이름과 컨테이너만 정의해주면 바로 배포가 됩니다. 서비스를 하는데 필요한 복잡한 설정을 추상화 시켜서 개발자가 필요한 최소한의 설정만으로 서비스를 제공할 수 있게 됩니다.   

그럼 Knative에서 어떤식으로 pod에 접근할 수 있는지 살펴보겠습니다.  

> 참고 : [호롤리한하루/Service Mesh Architecture & Istio를 알아보자](https://gruuuuu.github.io/cloud/service-mesh-istio/)

지금 Knative는 Istio를 기반으로 올라가있으며 그를 통해 배포한 pod은 **자동으로 Istio의 gateway를 통해 서비스**되고 있습니다.  

또한 Istio의 Service Mesh Architecture상, Istio의 gateway가 모든 knative서비스를 라우팅하기 때문에(단일 ip) 원하는 서비스를 구분할 수 있어야 합니다.  

방법은 두가지입니다.     
- Hostname
- URI (ex. [uri 라우팅 예제/Istio-Bookinfo](https://gruuuuu.github.io/cloud/service-mesh-istio/#istio-gateway))  

해당 예제에서 사용한 방법은 Hostname으로 식별하는 방법입니다.  

![image](https://user-images.githubusercontent.com/15958325/72135636-545cce00-33ca-11ea-8629-04dcfdf73beb.png)  
> 출처 : [조대협의 블로그/Serveless를 위한 오픈소스 KNative](https://bcho.tistory.com/1322)  

위 그림과 같이 **Knative서비스들은 Istio-gateway에 연결**되어 서비스됩니다.  

각 서비스에 접근하기 위해서는 각 서비스들의 **식별자**(`Hostname`또는 `URI`)와 **Istio-gateway의 ip정보**만 있으면 됩니다.   

그럼 지금부터 위에서 띄웠던 `helloworld-go` 서비스에 접근해보겠습니다.  

서비스의 Hostname을 알아내봅시다.  
~~~sh
$ kubectl get ksvc
~~~
![image](https://user-images.githubusercontent.com/15958325/72130635-79970f80-33bd-11ea-83e3-e64cf0f05dad.png)    

URL은 `http://{RouteName}.{k8s-namespace}.{Domain}`구성으로 되어있고, Domain같은 경우는 default가 `example.com`입니다.  

helloworld-go의 RouteName은 `helloworld-go`이고, 쿠버네티스 namespace는 `default`를 사용하였기 때문에, `helloworld-go.default.example.com` 이 전체 서비스 호스트명이 됩니다.  

그 다음, 두번째로 알아야하는 Istio-gateway의 ip정보 입니다.  
~~~sh
$ kubectl get svc istio-ingressgateway -n istio-system
~~~
![image](https://user-images.githubusercontent.com/15958325/72136539-59228180-33cc-11ea-9eb5-06acd621acfe.png)

local에서 접근하는 경우 :   
~~~sh
$ curl -H "Host: helloworld-go.default.example.com" http://10.96.93.83
~~~

외부에서 접근하는 경우 :   
~~~sh
$ curl -H "Host: helloworld-go.default.example.com" http://{istio-gateway ip}:31380
~~~

>- NodePort로 Istio-gateway를 설정해줬을 경우는 **노드의 ip**가 필요하며 LoadBalancer로 설정해줬을 경우엔 **External-IP**사용
>- 포트가 31380인 이유는 내부 80포트의 포트포워딩이 31380으로 되었기 때문. Istio-gateway의 포트정보를 확인해햐함.  

이렇게 간단하게 Istio-gateway의 기능을 사용하여 pod을 서비스할 수 있습니다.  

## 3.트래픽에 따라 pod을 올리거나 내림 (scale up-down)
여기까지 실습을 진행해보셨다면 하나 이상한 점을 발견하셨을 겁니다.  

~~~sh
$ kubectl get pod
~~~
위 명령어를 쳤을 때 helloworld-go pod이 뜨는 사람도 있을거고 pod이 없다고 뜨는 사람도 있을 것입니다.  

helloworld-go pod이 뜨는 분은 한 1분만 아무것도 하지 말고 기다렸다가 다시 명령어를 쳐보세요.  

분명히 서비스를 배포했는데....없어..!   
![image](https://user-images.githubusercontent.com/15958325/72137632-8112e480-33ce-11ea-9d7b-127953961409.png)  

일단 위에서의 curl명령어를 통해 서비스를 호출해봅시다.  
근데 신기하게 서비스는 정상적으로 호출됩니다.  

다시 pod을 검색해보면 없어졌던 helloworld-go가 생긴 것을 확인하실 수 있을겁니다.  
![image](https://user-images.githubusercontent.com/15958325/72137535-52950980-33ce-11ea-9801-3619d4d9ce83.png)  

Knative는 트래픽이 발생하지 않는 pod은 없애버렸다가 트래픽이 발생하는 순간 pod을 새로 띄웁니다.   

Knative는 Serverless솔루션이라는 것이 실감되는 부분입니다.  
이렇게 자주사용하는 pod은 scale up하여 신속한 처리를 가능하게 하고 자주 사용하지 않는 pod은 scale down (to Zero) 클러스터의 운용을 유연하게 할 수 있게 합니다.  

>살펴본 결과 60초정도 아무 트래픽이 없으면 pod을 꺼버리던데 이걸 더 늘릴수 있는건지는 나중에 알아봐야겠습니다.  

# 실습 - Eventing
> 참고 : [Knative/Getting Started with Eventing](https://knative.dev/docs/eventing/getting-started/#installing-knative-eventing)  

## Before you begin

실습을 시작하기 전에 다음 항목을 체크해주세요.  

- `Kubernetes` v1.14이상
- `curl` v7.65이상
- `Knative Eventing` component가 모두 존재

해당 포스팅을 통해 Knative v0.11로 설치했다면 문제없이 넘어가셔도 됩니다.  

~~~sh
$ kubectl get pods --namespace knative-eventing
~~~

결과가 아래와 같이 나오면 됩니다.  
~~~sh
NAME                                  READY   STATUS    RESTARTS   AGE
eventing-controller-d67878576-b9gxh   1/1     Running   0          3h50m
eventing-webhook-5b45945585-zh865     1/1     Running   0          3h50m
imc-controller-67b4c9787b-8xj82       1/1     Running   0          3h50m
imc-dispatcher-7b57bc9796-6fhx5       1/1     Running   0          3h50m
sources-controller-685db898c-85cdk    1/1     Running   0          3h50m
~~~

만약 아니라면 [Installing Knative Eventing](https://knative.dev/docs/eventing/getting-started/#installing-knative-eventing)를 참조  

## Creating and configuring an Eventing namespace

첫 번째로 이번 실습에서 사용할 namespace를 만들어줍니다.  

~~~sh
$ kubectl create namespace event-example
~~~

그다음 Knative의 eventing resource를 사용할 수 있게 다음과 같이 라벨링해줍니다.  
~~~sh
$ kubectl label namespace event-example knative-eventing-injection=enabled
~~~

확인 :   
~~~sh
$ kubectl get ns --show-labels
~~~

![image](https://user-images.githubusercontent.com/15958325/72216701-07aef980-3568-11ea-8639-fabe3de557e7.png)  


## Validating that the Broker is running
`Broker`는 Event Producer가 만든 모든 이벤트가 적절한 Event Consumer한테 보내질 수 있도록 하는 역할을 합니다.  
이벤트 처리를 위한 namespace를 생성할 때 만들어집니다.  

`event-example` namespace에 대한 이벤트 Broker가 만들어진 것을 확인해볼 수 있습니다.  
~~~sh
$ kubectl --namespace event-example get Broker default

NAME      READY   REASON   URL                                                     AGE
default   True             http://default-broker.event-example.svc.cluster.local   2m12s
~~~

`READY`가 `True`이면 브로커가 받은 이벤트들을 정상적으로 관리할 수 있다는 의미입니다.   

## Creating event consumers
Event Consumer는 Event Producer가 발생시키는 이벤트들을 받는 역할을 합니다.  

이 실습에서는 두개의 Event Consumer를 만들어 줄겁니다. (`hello-display`, `goodbye-display`)  

~~~yaml
# hello-display.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-display
spec:
  replicas: 1
  selector:
    matchLabels: &labels
      app: hello-display
  template:
    metadata:
      labels: *labels
    spec:
      containers:
        - name: event-display
          # Source code: https://github.com/knative/eventing-contrib/blob/release-0.6/cmd/event_display/main.go
          image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display@sha256:37ace92b63fc516ad4c8331b6b3b2d84e4ab2d8ba898e387c0b6f68f0e3081c4

---

# Service pointing at the previous Deployment. This will be the target for event
# consumption.
kind: Service
 apiVersion: v1
 metadata:
   name: hello-display
 spec:
   selector:
     app: hello-display
   ports:
   - protocol: TCP
     port: 80
     targetPort: 8080
~~~

~~~yaml
# goodbye-display.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goodbye-display
spec:
  replicas: 1
  selector:
    matchLabels: &labels
      app: goodbye-display
  template:
    metadata:
      labels: *labels
    spec:
      containers:
        - name: event-display
          # Source code: https://github.com/knative/eventing-contrib/blob/release-0.6/cmd/event_display/main.go
          image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display@sha256:37ace92b63fc516ad4c8331b6b3b2d84e4ab2d8ba898e387c0b6f68f0e3081c4

---

# Service pointing at the previous Deployment. This will be the target for event
# consumption.
kind: Service
apiVersion: v1
metadata:
  name: goodbye-display
spec:
  selector:
    app: goodbye-display
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
~~~

그 다음, 배포해줍니다.  
~~~sh
$ kubectl apply -f hello-display.yaml -n event-example
$ kubectl apply -f goodbye-display.yaml -n event-example
~~~

제대로 배포되었는지 확인 :   
~~~sh
$ kubectl get deploy -n event-example
~~~
![image](https://user-images.githubusercontent.com/15958325/72217284-983d0800-356f-11ea-9760-0e4a0be378c3.png)  

## Creating Triggers
`Trigger`는 Event Consumer에게 원하는 이벤트를 보낼 수 있게 하는 조건입니다. `Broker`는 Trigger를 통해 Event Consumer에게 이벤트를 보내게 됩니다.  

Event Consumer가 2개이니 트리거도 2개를 만들어줍시다.  
~~~yaml
# hello-trigger.yaml
apiVersion: eventing.knative.dev/v1alpha1
kind: Trigger
metadata:
  name: hello-display
spec:
  filter: # 조건
    attributes:
      type: greeting   # type이 greeting인 event에만 반응
  subscriber:  # 조건을 통과한 event는 subscriber로 이동
    ref:
     apiVersion: v1
     kind: Service
     name: hello-display  # hello-display라는 이름의 서비스로
~~~

~~~yaml
# goodbye-trigger.yaml
apiVersion: eventing.knative.dev/v1alpha1
kind: Trigger
metadata:
  name: goodbye-display
spec:
  filter:
    attributes:
      source: sendoff  # source가 sendoff인 event에만 반응
  subscriber:
    ref:
     apiVersion: v1
     kind: Service
     name: goodbye-display
~~~

배포해줍니다.  
~~~sh
$ kubectl apply -f hello-trigger.yaml -n event-example
$ kubectl apply -f goodbye-trigger.yaml -n event-example
~~~

확인 :  
~~~sh
$ kubectl get triggers -n event-example
~~~
![image](https://user-images.githubusercontent.com/15958325/72217406-7e4ff500-3570-11ea-9770-18173db16fc8.png)  

## Creating event producers
event consumer, Broker, Trigger까지 만들었으니 이제는 이벤트를 생성하는 producer를 만들어보겠습니다.  

대부분의 이벤트는 시스템적으로 생성되지만 이번 실습에서는 curl을 통해 manual하게 이벤트를 생성하겠습니다.  

curl request를 Broker에게 보내는 pod을 만들어줍니다.  
~~~yaml
# producer.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: curl
  name: curl
spec:
  containers:
    # This could be any image that we can SSH into and has curl.
  - image: radial/busyboxplus:curl
    imagePullPolicy: IfNotPresent
    name: curl
    resources: {}
    stdin: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    tty: true
~~~

~~~sh
$ kubectl apply -f producer.yaml -n event-example
~~~

## Sending Events to the Broker
모든 준비가 완료되었습니다.  

이제 Broker에게 총 세가지 이벤트를 보내보겠습니다.  

일단 producer인 pod안으로 ssh접속 :   
~~~sh
$ kubectl attach curl -it -n event-example
~~~  
![image](https://user-images.githubusercontent.com/15958325/72217470-83617400-3571-11ea-86cb-53e88874378e.png)  

첫번째 (type : greeting) :     
~~~sh
$ curl -v "http://default-broker.event-example.svc.cluster.local" \
  -X POST \
  -H "Ce-Id: say-hello" \
  -H "Ce-Specversion: 0.3" \
  -H "Ce-Type: greeting" \
  -H "Ce-Source: not-sendoff" \
  -H "Content-Type: application/json" \
  -d '{"msg":"Hello Knative!"}'
~~~

>제대로 이벤트가 보내졌으면 이런 메세지가 날라옵니다.  
>~~~sh
>< HTTP/1.1 202 Accepted
>< Content-Length: 0
>< Date: Sat, 11 Jan 2020 14:56:07 GMT
>~~~

두번째 (source : sendoff) :    
~~~sh
curl -v "http://default-broker.event-example.svc.cluster.local" \
  -X POST \
  -H "Ce-Id: say-goodbye" \
  -H "Ce-Specversion: 0.3" \
  -H "Ce-Type: not-greeting" \
  -H "Ce-Source: sendoff" \
  -H "Content-Type: application/json" \
  -d '{"msg":"Goodbye Knative!"}'
~~~

세번째 (type : greeting, source : sendoff) :  
~~~sh
curl -v "http://default-broker.event-example.svc.cluster.local" \
  -X POST \
  -H "Ce-Id: say-hello-goodbye" \
  -H "Ce-Specversion: 0.3" \
  -H "Ce-Type: greeting" \
  -H "Ce-Source: sendoff" \
  -H "Content-Type: application/json" \
  -d '{"msg":"Hello Knative! Goodbye Knative!"}'
~~~

## Verifying events were received
각 consumer들의 로그를 뜯어서 trigger가 제대로 메세지를 보내줬는지 확인해봅시다.  

먼저 첫번째 **hello-display**입니다.  
위에서 `hello-trigger`로 `type:greeting` 인 event만 수신할 수 있게 해놨었습니다.  

~~~sh
$ kubectl logs -l app=hello-display -n event-example --tail=100
~~~

![image](https://user-images.githubusercontent.com/15958325/72217506-3336e180-3572-11ea-9096-2071b74bc30c.png)  
이벤트는 총 두개가 와있고, `type:greeting`인 event만 수신한 것을 확인할 수 있습니다.  

----

**goodbye-display**도 확인해봅시다.  
위에서 goodbye-trigger로 `source:sendoff` 인 event만 수신할 수 있게 해놨었습니다.  
~~~sh
$ kubectl logs -l app=goodbye-display -n event-example --tail=100
~~~

![image](https://user-images.githubusercontent.com/15958325/72217530-8446d580-3572-11ea-8ce6-3d6dd75e16a6.png)  

`hello-display`와 마찬가지로 이벤트는 두개가 와있고, `source:sendoff` 였던 event만 수신한 것을 확인할 수 있습니다.  

특이한 점은 type과 source중 하나만 일치해도 수신한다는 것입니다.  

----

## 한장 정리
![image](https://user-images.githubusercontent.com/15958325/72217973-a3e0fc80-3578-11ea-9af9-b55f44cfbb6d.png)  


----