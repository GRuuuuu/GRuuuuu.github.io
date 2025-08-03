---
title: "Cloud Loadbalancer가 없을 때 Domain Forwarding 하는 방법 : Nginx"
slug: loadbalancer
tags:
  - Container
  - Cloud
  - Knative
  - ServiceMesh
  - Istio
date: 2020-01-21T13:00:00+09:00
---

## Overview
pod의 서비스를 외부에 노출시키기 위해서는  
- Service의 type을 `NodePort`로 변경
- Ingress를 사용(물론 `NodePort`로)
- Cloud의 `Loadbalancer`사용  

보통 이 세가지 방법을 사용합니다.  

이번 포스팅에서는 제가 일주일간의 삽질로 알아낸 가장 심플한 도메인포워딩 방법을 소개해드리도록 하겠습니다.  

> 문서를 읽기 전에 보면 좋을 글들 :   
>-[호롤리한하루/Service Mesh Architecture & Istio를 알아보자](https://gruuuuu.github.io/cloud/service-mesh-istio/)  
>-[호롤리한하루/Knative란?](https://gruuuuu.github.io/cloud/knative/)   
>-[호롤리한하루/Knative를 다뤄보자! (Serving, Eventing 실습)](https://gruuuuu.github.io/cloud/knative-hands-on/#)


# Background
쿠버네티스 클러스터 위의 `Pod`들은 한군데 고정되어있지 않습니다.  
그렇기 때문에 `Service`를 통해 사용자들은 Pod에 접근할 수 있게 되는것이죠.  

그런데 클러스터 내부에서의 접근은 문제가 되지 않지만, 클러스터 외부에서 클러스터 내부로의 접근은 생각해야할 것들이 있습니다.  

## 1. NodePort
가장 단순하고 가장 많이 사용하는 방법입니다.  

`Service`의 type을 NodePort로 바꿔 **ip는** Service가 올라가있는 **노드의 ip를 사용하되 포트를 새로 할당**해주는 방식이죠.  

그래서 `{노드의 ip}:할당받은 포트`와 같은 형식으로 특정 서비스에 접근할 수 있게 됩니다.  

`Ingress`같은경우는 Service의 type을 ClusterIP로 유지해도 사용자는 Ingress를 통해 Pod에 접근할 수 있다는 점만 다르고 결국 Ingress자체의 type을 NodePort로 변경해야된다는 점에서는 동일합니다.  

거의 대부분의 경우에서 문제없이 사용할 수 있는 방법입니다.  

## 1번의 문제
문제가 생기는경우는 어떤 경우일까요?  
사실 NodePort의 문제가 아니라 NodePort만 사용했을 때의 문제점이라고 해야지 맞을 것 같습니다.    

먼저 [호롤리한하루/Knative를 다뤄보자! (Serving, Eventing 실습)](https://gruuuuu.github.io/cloud/knative-hands-on/#)의 **실습 - Serving**부분을 예시로 설명하겠습니다.  

`helloworld-go` pod을 **Knative Serving**기능을 사용해 클러스터에 배포하게 되면 아래 그림과 같은 구조를 띄게 됩니다.  
![Picture1](https://user-images.githubusercontent.com/15958325/72872527-ed77d700-3d30-11ea-9834-736e06f7fe30.png)  

pod이 배포될때 Istio에 의해 `envoy proxy`가 내장되며 각 프록시들의 control plain 역할을 `Istio`가 맡게 됩니다.  
따라서 모든 pod들을 접속하려면 Istio의 `Ingressgateway`에 접근해야만 합니다.  

`Knative`의 성질에 따라 pod은 자동으로 scale up&down이 되며 `Service`에 요청이 올때만 pod이 뜨게 됩니다.  

좀 더 자세히 들여다보면 :   
~~~sh
$ kubectl get ksvc helloworld-go
~~~
![image](https://user-images.githubusercontent.com/15958325/72871671-d637ea00-3d2e-11ea-92b9-324f66f371cc.png)   
knative service에는 외부에서 접근가능한 URL이 적혀있습니다.  

>도메인이 사용가능하며 외부에서 접근할 수 있다는 전제하에,  

따라서 저 도메인으로 접근하게되면 특정 포트를 사용하지 않고도, `Ingressgateway` -> `ksvc` -> `pod` 의 순서로 원하는 pod에 접근할 수 있게 됩니다.  

~~~sh
# domain
$ curl http://helloworld-go.default.hololy-dev.com
~~~
~~~sh
# ip
$ curl -H "Host: helloworld-go.default.hololy-dev.com" http://{ip address}:port
~~~
위 둘은 같은 의미를 가지며 요청했을때의 출력도 같습니다.  

이전 포스팅에서의 실습은 도메인을 이용해 접근하는 방식을 사용하지 않고 ingress gateway의 **ip**와 **port** 그리고 **Host**정보를 사용했었습니다.  

근데 domain으로 접근해보면 접근이 안되실겁니다.  

이유는 다음과 같습니다. **http의 기본 포트정보는 80이고**, 거의 대부분의 도메인 업체에서 도메인의 기본포트는 80이기 때문입니다.   
결국 Istio의 `ingressgateway`에 접근해야 하니 관련 포트정보를 확인해봅시다 :    
~~~sh
$ kubectl get svc istio-ingressgateway -n istio-system
~~~
![image](https://user-images.githubusercontent.com/15958325/72874267-ee126c80-3d34-11ea-9faf-8e8ee3063528.png)  

제 경우엔 31380포트로 접근해야 하네요.  

그럼 `도메인:port`로 접근하면 되는거 아닌가? 하실 수 있습니다.  

**결론 : 안됨**    
![image](https://user-images.githubusercontent.com/15958325/72874552-a7714200-3d35-11ea-8304-420f10a0d630.png)
  
호스트정보가 명확하지 않아서 404에러가 발생합니다.  

결국!  
1. ingressgateway가 독립적인 ip를 소유하고(loadbalancer) 도메인은 ingressgateway의 ip를 가리키도록 설정
2. Cloud Node의 ip를 가리키는 도메인의 http요청이 올 때, 해당 요청을 원하는 포트로 포워딩    

둘 중 하나의 방법을 사용해야 합니다.  

잠시 로드밸런서에 대해 간단히 짚고 넘어가겠습니다.  

## 2. LoadBalancer
클라우드환경에서 클러스터를 구축한 경우에 많이 사용하는 방법입니다.  

로드밸런서는 주로 **여러대의 서버에게 균등하게 트래픽을 분산**시켜주는 역할을 합니다.  

서비스의 type을 Loadbalancer로 변경하게되면 로드밸런서의 ip를 받게 됩니다.  
해당 ip를 통해서 직접 외부에서 접근할 수 있습니다.  
또한 도메인의 포워딩 설정이 쉽게 가능합니다.  

하지만 **추가적인 비용**이 발생하게 됩니다.  
프로덕션 환경이면 몰라도 테스트 환경에서 로드밸런서를 쓰기엔 조금 과할 수 있습니다.  

그래서 로드밸런서를 사용하지 않고 도메인 포워딩을 가능하게 하는 방법을 지금부터 기술하겠습니다.  

# Domain Forwarding using NGINX
이번 포스팅에서 하려고 하는 것 :       
>Node의 ip를 가리키는 도메인의 http요청이 올 때, 해당 요청을 원하는 포트로 포워딩   

그림으로 보면 다음과 같습니다.   
![Picture2](https://user-images.githubusercontent.com/15958325/72876151-35026100-3d39-11ea-998b-232ce3d7bf32.png)   

## Domain Configuration
실습을 시작하기전에 한가지 전제가 있습니다.  
**개인 도메인을 가지고 있어야 한다는 것**입니다. 대략 1만원정도에 1년 사용할 수 있는 것 같습니다.  

도메인을 마련하셨으면 DNS를 수정해줄 차례입니다.  
![image](https://user-images.githubusercontent.com/15958325/72876732-89f2a700-3d3a-11ea-9389-02e6bf44c896.png)  

위 사진과 같이 도메인이 클러스터의 IP를 가리키도록 설정합니다.  

설정하고 5~10분 뒤에 nslookup으로 확인해줍니다.  
~~~sh
$ nslookup hololy-dev.com
~~~
![image](https://user-images.githubusercontent.com/15958325/72876864-de962200-3d3a-11ea-8aec-2cdc18a32e41.png)

Address에 설정한 클러스터 IP가 뜬다면 성공입니다.   

## Nginx Configuration

설치 :  
~~~sh
$ vim /etc/yum.repos.d/nginx.repo

[nginx] 
name=nginx repo 
baseurl=http://nginx.org/packages/centos/7/$basearch/ 
gpgcheck=0 
enabled=1
~~~

~~~sh
yum install nginx
~~~

nginx 시작:   
~~~sh
$ systemctl enable nginx
$ systemctl start nginx
~~~

바로 도메인을 웹에 쳐보면 nginx 기본화면이 뜨는 것을 확인할 수 있습니다.  
~~~sh
http://hololy-dev.com
~~~

그럼 이제 기본 80포트로 접근하였을 때, Istio-ingressgateway의 31380포트로 포워딩을 시켜보겠습니다.  

~~~sh
$ vim /etc/nginx/conf.d/default.conf
~~~

다음 줄을 추가해줍니다.  
~~~
# 80 -> 31380
proxy_pass http://{ip address}:31380

# host정보를 포워딩할때도 전송
proxy_set_header Host $host;

# http버전이 다르면 426에러가 발생
# 버전을 맞춰줘서 에러를 막음
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
~~~
![image](https://user-images.githubusercontent.com/15958325/72877202-c672d280-3d3b-11ea-900d-eccc4f3df0c5.png)  

nginx 재시작 :  
~~~sh
$ systemctl restart nginx
~~~


## Test
이제 제대로 포워딩이 되는지 확인해보겠습니다.  

~~~sh
$ curl helloworld-go.default.hololy-dev.com
~~~

![image](https://user-images.githubusercontent.com/15958325/72877506-6b8dab00-3d3c-11ea-917f-7bb5f6d327b2.png)   

제대로 응답이 왔습니다!  

`/etc/nginx/conf.d/default.conf`파일을 잘 수정하면 지금처럼 도메인 1개를 포워딩하는게 아니라 여러 도메인을 가지고 한 서버에서 운영할 수 있게도 할 수 있습니다.  

-----