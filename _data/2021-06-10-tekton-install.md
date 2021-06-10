---
title: "Tekton Tutorial - Task와 PipelineRun 다뤄보기!"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
last_modified_at: 2021-06-10T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이전 포스팅에서는 `Tekton`이 무엇이고, Tekton의 컴포넌트에 대해서 알아보았습니다.  
이번 포스팅에서는 Tekton을 설치해보고, 쿠버네티스 클러스터와 어떻게 상호작용을 할 수 있는지 실습을 진행하겠습니다.  

참고 : [tekton.dev - getting started](https://tekton.dev/docs/getting-started/)

# 1. Tekton 설치하기
tekton 설치
~~~
$ kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
~~~

> cri-o를 사용하는 `OpenShift 4.x` 같은 `image-reference:tag@digest`를 지원하지 않는 경우 :  
> ~~~
>$ kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.notags.yaml
>~~~

설치 확인:  
~~~
$ kubectl get pods --namespace tekton-pipelines

NAME                                           READY   STATUS    RESTARTS   AGE
tekton-pipelines-controller-5f88bb8695-r87jh   1/1     Running   0          21s
tekton-pipelines-webhook-77d48dc65c-2snwz      1/1     Running   0          21s
~~~

# 2. Tekton CLI 설치
