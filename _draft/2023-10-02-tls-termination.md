---
title: "호다닥 톺아보는 SSL/TLS (feat. Openshift)"
categories: 
  - Openshift
tags:
  - Kubernetes
  - Openshift
  - Security
  - Auth
last_modified_at: 2023-10-02T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
2년전쯤에 [X509에 관한 포스팅](https://gruuuuu.github.io/security/what-is-x509/)을 한 적이 있었는데요, 이번 포스팅은 그 후속편이라고 봐주시면 될 것 같습니다.  

>아니 근데 그게 벌써 2년전이라니... 이거 적으면서 확인했는데 너무 충격...🥲  

우리가 웹사이트를 방문할 때 신뢰할 수 있는 연결을 수립하기 위해선, 보안 통신과 신뢰할 수 있는 인증서가 필요합니다.  
지난 포스팅에서는 그 중에서 인증서에 대한 내용을 다뤘었고,  
이번 포스팅에서는 통신 자체에 대해서 다뤄보려고 합니다.  

그리고 그 연결이 Kubernetes 또는 Openshift에서는 어떤식으로 동작하는지도 알아보겠습니다.  

