---
title: "Openshift Custom Domain 설정"
categories:
  - OCP
tags:
  - Kubernetes
  - Openshift
last_modified_at: 2021-10-29T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview

Kubernetes같은 경우는 클러스터 생성시, 도메인이 필요하지 않기 때문에 원하는 도메인을 사용하고 싶다면 별도로 ingress를 통해 세팅해줘야하는데요,

**Openshift**는 클러스터 생성시, 도메인을 넣어서 설치를 하게 되어있습니다. 그래서 클러스터가 가지고 있는 기본 도메인이 있고 서비스를 `expose`하여 route를 생성하게 되면 `<svcName>.apps.<basedomain>`이런 식으로 주소를 부여받게 됩니다.

그런데 Managed Cluster의 경우 자동적으로 클러스터에 부여받는 domain이 있는데요, 대부분의 경우 그 domain이 어마어마하게 깁니다.

```
$ oc get route

NAME                               HOST/PORT                                                                                                                                PATH   SERVICES                                       PORT    TERMINATION     WILDCARD

test-router         test-router-testnamespace.kr-ddd-298fdf11110631bdad517f871be4f871-0000.seo01.containers.appdomain.cloud                test-svc    8000                    None
```


미관상 보기 좋게 하기위해서, 또는 기존의 도메인 말고 다른 도메인으로 클러스터의 서비스에 접근하고 싶을 때, **ingress를 사용하면 간단하게 해결할 수 있습니다.**

> **주의!**  
> Openshift의 base domain을 변경한다는 뜻이 아닙니다!

## Steps

### 1. Custom Domain 준비하기

사용할 도메인을 준비하여 클러스터를 가리키게 합니다.  
![image](https://user-images.githubusercontent.com/15958325/139383918-a71c92eb-c989-4fa4-81c1-0d92ec96b886.png)

> Managed Cluster의 경우 basedomain을 그대로 CNAME으로 등록하면 편합니다.

### 2. Cert준비

https연결을 위해 새로 만들 도메인의 cert를 발급받습니다.

참고 : [호다닥 공부해보는 x509와 친구들(2) - Let’s Encrypt](https://gruuuuu.github.io/security/letsencrypt/)

> http연결에 대해서는 해당 과정 불필요

### 3. secret 생성

발급받은 cert를 ocp의 secret으로 생성합니다.

```
$ oc create secret tls testtest-ca \
--cert={location of certificate} \
--key={location of private key}
```

### 4. ingress 생성

다음으로 custom domain으로 연결할 서비스를 ingress로 정의해줍니다.

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
spec:
  tls:
  - hosts:
    - app.testtest.testdomain.com
    secretName: testtest-ca
    - host: app.testtest.testdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: test-svc
                port:
                  number: 80
```

그리고 배포해주면

```
$ oc get ingress
NAME               CLASS    HOSTS                                                                                                                            ADDRESS                                                                              PORTS     AGE
test-ingress   <none>   app.testtest.testdomain.com                                                                                                        kr-ddd-298fdf0f111631bdad517f8111e4f871-0000.seo01.containers.appdomain.cloud   80, 443   6h34m


$ oc get route

NAME                               HOST/PORT                                                                                                                                PATH   SERVICES                                       PORT    TERMINATION     WILDCARD

test-router         app.testtest.testdomain.com                test-svc    80                    None
```

생성했던 ingress와 ingress규칙별로 route가 생성되는 것을 확인할 수 있습니다.

이제 길고 어지러운 주소 대신 깔끔한 주소로 서비스를 사용할 수 있습니다!!

---
