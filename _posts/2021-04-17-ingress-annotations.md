---
title: "Nginx Ingress Controller Annotations - Rewirte"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Controller
  - Service
  - Ingress
last_modified_at: 2021-04-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
여러 annotation을 통해 **Nginx Ingress Controller**의 설정값들을 변경할 수 있습니다.  

-> [전체 Annotation](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)  

이번문서에서는 여러 Annotation 중 url `rewrite`에 관련된 annotation에 대해서 알아보겠습니다.  

-> [Annotation/rewrite](https://kubernetes.github.io/ingress-nginx/examples/rewrite/)  

# Rewrite Target
Ingress규칙을 작성하다보면 path에 따라 서비스를 나누게 되는데요,  
경우에 따라 해당 서비스 안에서도 하위 path를 이용해야하는 경우가 있을 수도 있습니다.  

예를 들어, Ingress규칙이 다음과 같을 때  
~~~
    http:
      paths:
      - path: /something
        backend:
          serviceName: http-svc
          servicePort: 80
~~~
`xxx.com/something` 으로 접속했을시 `http-svc` 서비스로 리다이렉트 되게 됩니다.  

그런데 내부 서비스에서 하위 주소를 입력하여 서비스 내에서도 다른페이지를 보여주어야 하는 경우 (예를 들어 `xxx.com/something/home.html`또는 `xxx.com/something/login.html`)  
404에러가 발생하게 됩니다.  

이유는 request하는 헤더에 `/something`까지 같이 포함되기 때문입니다.  
ex)  
Ingress로의 요청 : /something/home.html -> 실제 서비스로의 요청 : /something/home.html  

서비스를 구분하는 path는 그대로두되, 하위 path만을 요청하고 싶은 경우 **Rewrite annotation**을 사용합니다.  

~~~
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
~~~

`rewrite-target`을 사용하게 되면 구분 path는 사라지고 rewrite-target에 적은 url path로 대체되게 됩니다.  
ex)  
위의 annotation대로 요청했을 시:  
Ingress로의 요청 : /something -> 실제 서비스로의 요청 : /  

이걸 이용해서 하위 path까지 포함하게 하는 방법은 다음과 같습니다.  
~~~
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
  name: rewrite
  namespace: default
spec:
  rules:
  - host: rewrite.bar.com
    http:
      paths:
      - backend:
          serviceName: http-svc
          servicePort: 80
        path: /something(/|$)(.*)
~~~
정규식과 비슷하게 적용하시면 됩니다. 다 같은데 capture group을 하는 방법이 다릅니다.  
(정규식 : /1, nginx ingress에서 사용하는 방법 : $1)   

**주요 식 정리:**   
(/|$) : /로끝나거나 something으로 끝나거나   
$2 : 두번째 그룹  

그래서 위와 같이 적용하면 아래와 같이 원하는 서비스에 하위 path를 그대로 요청할 수 있습니다.    
/something -> /  
/something/ddd -> /ddd  

# App Root
`app-root`는 default경로를 정하는 annotation입니다.  

~~~
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/app-root: /app1
  name: approot
  namespace: default
spec:
  rules:
  - host: approot.bar.com
    http:
      paths:
      - backend:
          serviceName: http-svc
          servicePort: 80
        path: /
~~~
위와 같이 경로가 설정되어있다면  
default("/")경로로 접근하였을 때, http-svc의 /app1경로로 리다이렉트되게 됩니다.  

----