---
title: "Openshift Certificate 갱신하기"
slug: ocp-cert-renew
tags:
  - Kubernetes
  - Openshift
  - x509
date: 2023-01-16T13:00:00+09:00
---

## Overview

클러스터의 [Ingress Certificate를 구성](https://gruuuuu.github.io/ocp/ocp-ingress-ca/)하고나서 n개월이 지나면 인증서가 만료가 됩니다.  

그 이후 클러스터에 로그인을 하려고 보면 아래와 같이 x509에러가 발생하게 됩니다.  
~~~
$ oc login -u kubeadmin
error: x509: certificate has expired or is not yet valid: current time 2023-01-16T10:41:34+09:00 is after 2023-01-12T07:37:26Z
~~~

> ingress의 인증서가 만료되면 `*.apps`아래 하위 도메인은 물론, web console, cli 둘다 접속할 수 없게됩니다.  

## 문제 확인
먼저 ingress의 ca 만료일자를 확인해보도록 하겠습니다.  

~~~
$ oc project openshift-ingress

$ oc get secret secret-ca -oyaml | grep crt | awk '{print $2}' | base64 -d | openssl x509 -noout -dates -issuer -subject
notBefore=Oct 14 07:37:27 2022 GMT
notAfter=Jan 12 07:37:26 2023 GMT
issuer=C = US, O = Let's Encrypt, CN = R3
subject=CN = *.apps.clusterName.xxx.com
~~~
생성일자와 만료일자를 확인할 수 있습니다.  


그 다음 `ClusterOperator`의 `authentication`을 살펴보겠습니다.  
~~~
$ oc describe co/authentication
....
Status:
  Conditions:
    Last Transition Time:  2023-01-12T07:39:35Z
    Message:               OAuthServerRouteEndpointAccessibleControllerDegraded: Get "https://oauth-openshift.apps.clusterName.xxx.com/healthz": x509: certificate has expired or is not yet valid: current time 2023-01-16T02:01:01Z is after 2023-01-12T07:37:26Z
RouterCertsDegraded: secret/v4-0-config-system-router-certs.spec.data[apps.clusterName.xxx.com] -n openshift-authentication: certificate could not validate route hostname oauth-openshift.apps.clusterName.xxx.com: x509: certificate has expired or is not yet valid: current time 2023-01-16T02:01:01Z is after 2023-01-12T07:37:26Z
    Reason:                OAuthServerRouteEndpointAccessibleController_SyncError::RouterCerts_InvalidServerCertRouterCerts
    Status:                True
    Type:                  Degraded
...
~~~
certificate가 만료되어서 오퍼레이터가 현재 `Degraded`상태인 것을 확인할 수 있습니다.  

## ingress의 인증서 갱신하기
ingress에 인증서를 추가할때와 마찬가지로 secret을 새걸로 변경해주면 됩니다.  

### 1. Renew Certificate
Let's Encrypt와 같은 인증기관에서 ingress용으로 사용했던 인증서를 갱신해줍니다.  

### 2. secret 생성
원래 ingress secret으로 사용하고 있던 녀석을 삭제하고 새로 만들어줍니다.  

~~~
$ oc create secret tls secret-ca --cert=/path/fullchain1.pem --key=/path/privkey1.pem -n openshift-ingress

secret/secret-ca created
~~~

이후 route pod들을 재시작 시켜주면 완료  

### 3. 확인
만료일자 확인  
~~~
$ oc get secret secret-ca1 -oyaml | grep crt | awk '{print $2}' | base64 -d | openssl x509 -noout -dates -issuer -subject

notBefore=Jan 16 01:36:23 2023 GMT
notAfter=Apr 16 01:36:22 2023 GMT
issuer=C = US, O = Let's Encrypt, CN = R3
subject=CN = *.apps.clusterName.xxx.com
~~~

다시 로그인 해보면 x509에러가 뜨지 않는 것을 확인할 수 있습니다  
~~~
$ oc login -u kubeadmin
Authentication required for https://api.ocp410.garagekr.com:6443 (openshift)
Username: kubeadmin
Password:
~~~

## Appendix. CA Bundle 인증서 갱신에 대해서
공식문서([Replacing the default ingress certificate](https://docs.openshift.com/container-platform/4.11/security/certificates/replacing-default-ingress-certificate.html))를 따라서 ingress certificate를 바꾸면  
ingress cert만 바꾸는게아니라 cluster-wide proxy 설정까지 변경하라고 나와 있습니다.  

사실 본문의 x509에러 자체는 ingress쪽 인증서만 교체해주면 정상적으로 해결됩니다.  
그럼 cluster-wide proxy에서 변경했던 CA Bundle certificate는 대체 어디에 사용되는 녀석인걸까요?  

### Proxy certificates?
>doc : [OpenShift/Proxy certificates](https://docs.openshift.com/container-platform/4.11/security/certificate_types_descriptions/proxy-certificates.html)  

[여기](https://docs.openshift.com/container-platform/4.11/security/certificates/replacing-default-ingress-certificate.html)에서 ingress certificate를 바꿀 때 같이 변경했던 cluster-wide proxy의 `ca-bundle.crt`는 egress 연결 시 사용되는 인증서입니다.  

원래는 Openshift를 처음 설치할때에 `install-config.yaml`파일의 `additionalTrustBundle`을 통해서 proxy 인증서를 추가할 수 있는데,   
~~~yaml
...
proxy:
  httpProxy: http://<https://username:password@proxy.example.com:123/>
  httpsProxy: https://<https://username:password@proxy.example.com:123/>
	noProxy: <123.example.com,10.88.0.0/16>
additionalTrustBundle: |
    -----BEGIN CERTIFICATE-----
   <MY_HTTPS_PROXY_TRUSTED_CA_CERT>
    -----END CERTIFICATE-----
...
~~~

이때 설정된 인증서는 클러스터 설치 이후, RedHat CoreOS의 trust bundle과 합쳐져서 cluster-wide proxy의 `trustedCA`에 포함되고, 클러스터가 egress HTTP call을 할 때에 사용되게 됩니다.  

예를들어 `image-registry-operator`가 외부의 image registry에서 이미지를 다운로드할때에 활용하게 됩니다.  

만약 설치할 때 `additionalTrustBundle`을 비워두고 설치했다면, RHCOS의 trust bundle만 egress HTTP call에 사용되게 됩니다.  

정리하면 :  
- cluster-wide proxy는 cluster의 egress통신 시 사용
- proxy설정과 신뢰할 수 있는 인증서(`trustedCA`)를 갖고있음

ingress통신에는 영향을 주지 않아 ingress쪽 인증서만 갱신해주면 본문의 x509에러는 해결할 수 있으나, egress쪽도 갱신해주지 않으면 언제 어디서 문제가 생길지 모르기때문에 모든 인증서들은 만료되기전에 교체해주는 것이 좋습니다.  

----