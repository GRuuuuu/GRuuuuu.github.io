---
title: "Tekton pipeline과 ArgoCD 연동하기"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
  - GitOps
last_modified_at: 2021-06-21T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
ArgoCD와 Tekton Pipeline를 연동하여 CI/CD 파이프라인을 구성하는 방법에 대해서 기술하도록 하겠습니다.  

실습에서는 지난 포스팅의 Pipeline을 사용할 것이므로 지난 포스팅을 보고 이번 포스팅을 읽는 것을 추천합니다.  

지난 포스팅- [Tekton Trigger를 사용하여 Pipeline 자동으로 돌려보기
](https://gruuuuu.github.io/cloud/tekton-trigger/)  

### [As-Is] Tekton Pipeline
현재 Tekton Pipeline은 대략 아래와 같은 구성입니다.  
![그림2](https://user-images.githubusercontent.com/15958325/122731658-7a241d00-d2b6-11eb-8f39-68be838f7073.png)  

이거를
### [To-Be] Tekton+ArgoCD


이렇게 만들어보도록 하겠습니다.  

## 1. [ArgoCD] ArgoCD 배포  
~~~
$ kubectl create namespace argocd
$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.0.3/manifests/install.yaml
~~~

>버전 release 정보 : [argoproj/argo-cd](https://github.com/argoproj/argo-cd/releases)  

확인:  
~~~
$ kubectl get pod -n argocd
NAME                                 READY   STATUS    RESTARTS   AGE
argocd-application-controller-0      1/1     Running   0          56s
argocd-dex-server-65f7d98b78-l877c   1/1     Running   0          56s
argocd-redis-9567956cd-2zg5p         1/1     Running   0          56s
argocd-repo-server-d6ffd9d98-49sc4   1/1     Running   0          56s
argocd-server-5cbd9669f7-p65t7       0/1     Running   0          56s
~~~

이제 외부에서 접근할 수 있도록 서비스를 NodePort 타입으로 변경하거나 Ingress를 통해 외부로 노출할 수 있도록 해주겠습니다.  

### Using NodePort or LoadBalancer
~~~sh
# SVC_TYPE은 NodePort || LoadBalancer
$ kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "{SVC_TYPE}"}}'
~~~

### add `--insecure`
기본적으로 `argocd-server`는 tls가 활성화 되어있어 http로 접속하려면 tls를 비활성화 시켜줘야 합니다.  

~~~
$ kubectl edit svc argocd-server -n argocd
~~~
![image](https://user-images.githubusercontent.com/15958325/123050222-6d7d0180-d43b-11eb-840b-31ee7fcdbbdf.png)  

Container command에 `--insecure`옵션을 추가시켜줍니다.  

### ArgoCD GUI 접속
경로로 접속하면 꼴뚜기(?)가 환영해줍니다!ㅋㅋ  

![image](https://user-images.githubusercontent.com/15958325/123050423-a87f3500-d43b-11eb-9a11-90262458e74f.png)  


### ArgoCD 초기 계정

초기 `admin`의 비밀번호는 아래 커맨드를 통해 알아낼 수 있습니다.  
~~~
$ kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
~~~

접속!
![image](https://user-images.githubusercontent.com/15958325/123050829-14619d80-d43c-11eb-89d9-57a35922d71f.png)  

접속하면 다음과 같은 대시보드 화면을 확인할 수 있습니다.
![image](https://user-images.githubusercontent.com/15958325/123050957-3529f300-d43c-11eb-89b7-6f7a557459ee.png)  

## 2. [Tekton] Kustomize task 추가
![image](https://user-images.githubusercontent.com/15958325/123055237-a370b480-d440-11eb-9be3-25e068db0b4e.png)  

**Kustomize**는 `kustomization` 파일을 통해 쿠버네티스 오브젝트를 사용자가 원하는 대로 변경(Customize)하는 도구입니다.  
>참고 : [Kustomize를 이용한 쿠버네티스 오브젝트의 선언형 관리](https://kubernetes.io/ko/docs/tasks/manage-kubernetes-objects/kustomization/)

`Kubectl v1.14` 이후로 `kustomization`파일을 통한 관리를 지원하고 있습니다.  

예를들어 복잡한 application을 배포할때는 종종 `Helm` chart를 사용하여 배포할 수 있는데요, Helm chart의 value로 설정되어 있지 않거나, 새로운 resource를 추가하기 위해서는 chart 자체의 개선이 필요했습니다.  

대신 `kustomize`는 원래의 **manifest yaml들을 그대로 두고** `kustomization.yaml`파일을 사용해 커스텀할 수 있게 해줍니다.  
또한 production, staging, dev 등 스테이지 별로 관리가 가능합니다.  

그런데 갑자기 ArgoCD얘기를하다가 Kustomize얘기가 왜 나왔냐!   
그것은 필요하기 때문입니다...(끄덕)  

우리가 이번 포스팅에서 할 것은 `Tekton`+`ArgoCD`, **자동으로 Tekton pipeline이 완료되면 ArgoCD가 빌드된 이미지를 클러스터에 배포**해주는 것입니다.  

다시 [이전 포스팅](https://gruuuuu.github.io/cloud/tekton-trigger/)의 기억을 되살려 봅시다.  
Pipeline의 맨 마지막 Task인 `Buildah`에서 Image Registry에 빌드한 이미지를 push할 때 이미지의 태그를 유니크한 값을 주기 위해 Image push commit의 해시값을 사용하였습니다.  

즉, Tekton pipeline이 돌때마다 latest 이미지는 각각 다른 태그 값을 갖게 된다는 얘기이고  
ArgoCD가 latest 이미지를 배포할때마다 **변동된 태그값을 수정**해주어야 한다는 뜻입니다.  

관리자가 매번 수정해서 ArgoCD를 돌릴 수도 있지만, 이번 포스팅에서는 모든 스텝을 자동으로! 하게 하기위해 Kustomize를 사용하여 매 빌드버전을 kubernetes manifest 파일에 업데이트 해두도록 하겠습니다.  

### 2.1 k8s manifest용 폴더와 git repo 만들기
먼저 Application Repo에 쿠버네티스 배포용 폴더를 만들어주도록 하겠습니다.   

여기에 Manifest파일들을 저장하고 Kustomize로 커스텀하여 Manifest Repo로 push해줄겁니다.  

~~~
$ cd {APP_REPO}
$ mkdir k8s
~~~





