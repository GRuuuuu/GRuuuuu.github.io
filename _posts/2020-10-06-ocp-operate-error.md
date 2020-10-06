---
title: "Openshift4 Operations -Errors"
categories: 
  - OCP
tags:
  - Kubernetes
  - RHCOS
  - Openshift
last_modified_at: 2020-10-06T13:00:00+09:00
author_profile: true
toc : true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
Openshift를 다루며 생겼던 에러들에 대해서 정리해둔 문서입니다.  

설치할때 만난 에러들은 여기 -> [Openshift4.3 Installation on Baremetal -Errors](https://gruuuuu.github.io/ocp/ocp4-install-error/)

# Errors
## 1. remote error: tls: internal error
`rsh logs exec` 했을때 발생한 에러.  
~~~sh
Error from server: error dialing backend: remote error: tls: internal error
~~~

**해결:**   
`oc get csr`해서 pending되어있는것들 확인 후 `approve`
~~~sh
oc get csr -o name | xargs oc adm certificate approve
~~~

## 2. error: x509: certificate signed by unknown authority
openshift클러스터에 로그인을 하려고할때 발생  
~~~sh
I0911 01:24:55.482060   27088 loader.go:375] Config loaded from file:  /root/dir/auth/kubeconfig
I0911 01:24:55.488669   27088 round_trippers.go:443] HEAD https://api.gru.hololy-dev.com:6443/ 403 Forbidden in 6 milliseconds
I0911 01:24:55.488688   27088 request_token.go:86] GSSAPI Enabled
I0911 01:24:55.489273   27088 round_trippers.go:443] GET https://api.gru.hololy-dev.com:6443/.well-known/oauth-authorization-server 200 OK in 0 milliseconds
I0911 01:24:55.506423   27088 round_trippers.go:443] HEAD https://oauth-openshift.apps.gru.hololy-dev.com  in 17 milliseconds
I0911 01:24:55.506434   27088 request_token.go:438] falling back to kubeconfig CA due to possible x509 error: x509: certificate signed by unknown authority
I0911 01:24:55.509948   27088 round_trippers.go:443] GET https://oauth-openshift.apps.gru.hololy-dev.com/oauth/authorize?client_id=openshift-challenging-client&code_challenge=2O9S3Xn3IUl6cmCSRhffG9X-CnUDFoVv0OW8pzb8bbM&code_challenge_method=S256&redirect_uri=https%3A%2F%2Foauth-openshift.apps.gru.hololy-dev.com%2Foauth%2Ftoken%2Fimplicit&response_type=code  in 3 milliseconds
I0911 01:24:55.511192   27088 round_trippers.go:443] GET https://api.gru.hololy-dev.com:6443/api/v1/namespaces/openshift/configmaps/motd 403 Forbidden in 0 milliseconds
F0911 01:24:55.512004   27088 helpers.go:114] error: x509: certificate signed by unknown authority
~~~

**해결:**
~~~sh  
$ oc rsh -n openshift-authentication <oauth-openshift-pod> cat /run/secrets/kubernetes.io/serviceaccount/ca.crt > ingress-ca.crt
~~~
~~~sh
$ oc login -u username -p password https://api.example.local:6443 --certificate-authority=ingress-ca.crt
~~~
