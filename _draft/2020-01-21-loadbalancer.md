---
title: "Cloud Loadbalancer가 없을 때 Domain Proxy 하는 방법 : Nginx"
categories: 
  - Cloud
tags:
  - Container
  - Cloud
  - Knative
  - ServiceMesh
  - Istio
last_modified_at: 2020-01-21T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
pod의 서비스를 외부에 노출시키기 위해서는  
- Service의 type을 `NodePort`로 변경
- Ingress를 사용(물론 `NodePort`로)
- Cloud의 `Loadbalancer`사용  

보통 이 세가지 방법을 사용합니다.  

이번 포스팅에서는 제가 일주일간의 삽질로 알아낸 가장 심플한 도메인프록시 방법을 소개해드리도록 하겠습니다.  

> 문서를 읽기 전에 보면 좋을 글들 :   
>-[호롤리한하루/Knative란?](https://gruuuuu.github.io/cloud/knative/)   
>-[호롤리한하루/Knative를 다뤄보자! (Serving, Eventing 실습)](https://gruuuuu.github.io/cloud/knative-hands-on/#)


# 왜 필요한가?
