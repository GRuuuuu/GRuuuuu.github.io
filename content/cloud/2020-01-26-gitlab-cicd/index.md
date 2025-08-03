---
title: "k8s + GitLab으로 CI/CD환경 구축해보기"
slug: gitlab-cicd
tags:
  - Container
  - Cloud
  - Kubernetes
  - GitLab
  - Istio
  - Knative
date: 2020-01-26T13:00:00+09:00
---

## Overview
이번 포스팅에서는 k8s와 GitLab으로 CI/CD환경을 구축해보겠습니다.  

# CI/CD?
- **CI** : `Continuous Intergration`:지속적인 통합
- **CD** : `Continuous Delivery`:지속적인 서비스 제공 or `Deployment`:지속적인 배포

CI/CD는 애플리케이션 개발 단계를 자동화하여 애플리케이션을 보다 짧은 주기로 고객에게 제공하는 방법이며, 각 개발팀이 소스코드를 통합할 때 개발/운영팀에서 발생하는 **Integration hell**을 해결하기 위해 나온 솔루션입니다.  

이를 성공적으로 구축할 경우, 애플리케이션에 대한 새로운 코드 변경 사항이 정기적으로 빌드&테스트되어 공유 repository에 commit되므로 여러 개발자가 동시에 개발을 할 경우에 발생할 수 있는 충돌문제를 해결할 수 있습니다.   

또한 이를 통해 통합 및 테스트 단계에서부터 배포에 이르는 애플리케이션 라이프사이클 전체에 걸쳐 **지속적인 자동화와 모니터링을 제공**합니다.  

![image](https://user-images.githubusercontent.com/15958325/73132902-c7ba3d00-4064-11ea-81b9-15da541fe78a.png)  

# GitLab?
![image](https://user-images.githubusercontent.com/15958325/73132922-1536aa00-4065-11ea-88aa-7e5f93281321.png)  

GitLab은 **이슈, 코드 리뷰, CI/CD를 단일 UI로 통합**해서 볼 수 있는 오픈소스 프로젝트입니다.  

설치형 Github라는 컨셉으로 시작된 프로젝트이기 때문에 Github와 비슷한 면이 많이 있습니다.  
서비스형 원격 저장소를 운영하는 것에 대한 **비용**이 부담되거나 소스코드의 **보안**이 중요한 프로젝트에 적당합니다.  

**특징:**  
1. 설치형 버전관리 시스템
    - 자신의 서버에 직접 설치해서 사용 
2. 클라우드 버전관리 시스템
    - gitlab.com을 이용하면 서버 없이도 gitlab사용 가능
    - 10명 이하의 프로젝트는 무료로 사용 가능
3. Issue Tracker 제공
4. Git Repository 제공
5. API 제공
6. Team, Group 기능 제공


# 실습 (k8s+gitlab)
그럼 지금부터 `kubernetes`와 `gitlab`으로 `CI/CD`환경을 구축해보겠습니다.  

>해당 포스팅에서는 설치형 버전의 GitLab이 아니라 **클라우드 GitLab**을 사용하여 CI/CD환경을 구축할것입니다.

## Prerequisites
먼저 쿠버네티스 클러스터를 생성해주세요.  

참고링크 : [호롤리한하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)  

> 본 실습에서 사용한 spec :   
>`OS : CentOS v7.6`  
>`Arch : x86` 
>
>`Kubernetes` : `v1.16.2`  
>`Master` : 4cpu, ram16G (1개)  
>`Node` : 4cpu, ram16G (2개) 

## GitLab Configuration
### 계정 생성
[https://gitlab.com/](https://gitlab.com/)에 접속하여 계정 생성  

![image](https://user-images.githubusercontent.com/15958325/73133846-cd6a4f80-4071-11ea-8ab6-e0f8659a8c03.png)


### 새로운 프로젝트 생성
![image](https://user-images.githubusercontent.com/15958325/73133869-1f12da00-4072-11ea-8dbc-4af0a3b85a99.png)  
project name을 입력해주고 public으로 설정해줍니다.  

### 초기화면
![image](https://user-images.githubusercontent.com/15958325/73133889-4e294b80-4072-11ea-9e07-5d37a105e716.png)  


### Kubernetes연동

메뉴 -> Operations -> Kubernetes로 이동   

![image](https://user-images.githubusercontent.com/15958325/73133910-8761bb80-4072-11ea-90ef-2050663d3561.png)  

![image](https://user-images.githubusercontent.com/15958325/73133929-f17a6080-4072-11ea-9109-aba1d96a537b.png)  
이미 존재하는 cluster를 연동할 것이므로 **Add Existing Cluster** 클릭  


![image](https://user-images.githubusercontent.com/15958325/73133940-2ab2d080-4073-11ea-836c-60a84889a9f0.png)  
뭔가 적으라는게 많습니다. 일단 이 화면까지 진행했으면 잠시 멈추고 쿠버네티스 클러스터 서버로 돌아갑니다.  

Master노드에서 노드가 제대로 떠있는지 확인해주고,  
~~~sh
$ kubectl get nodes
~~~
![image](https://user-images.githubusercontent.com/15958325/73133958-8a10e080-4073-11ea-8e92-9317b98f6db9.png)  

이제 깃랩에서 적어야하는 쿠버네티스 클러스터 정보를 차례대로 보여드리겠습니다.  

#### Kubernetes Cluster Name
아무이름이나 적어줍니다.  

#### API URL
~~~
https://{Master node ip}:6443
~~~

#### CA Certificate
~~~sh
$ kubectl config view --raw \
-o=jsonpath='{.clusters[0].cluster.certificate-authority-data}' \
| base64 --decode
~~~

#### Service Token
서비스 토큰을 얻기 전에, 깃랩에서 사용할 서비스 어카운트를 생성해 주어야 합니다.  

~~~yaml
# gitlab-admin.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gitlab-admin
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: gitlab-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: gitlab-admin
  namespace: kube-system
~~~

실행시켜주고,   
![image](https://user-images.githubusercontent.com/15958325/73134001-42d71f80-4074-11ea-84c6-b00eb311e2a7.png)  

토큰을 얻습니다.  
~~~sh
$ SECRET=$(kubectl -n kube-system get secret | grep gitlab-admin-token | awk '{print $1}')

$ TOKEN=$(kubectl -n kube-system get secret $SECRET -o jsonpath='{.data.token}' | base64 --decode)
echo $TOKEN
~~~

Add 해주면 쿠버네티스와 깃랩의 연동이 완료됩니다.  

### CI/CD 설정

> **중요!**  
> 이 단계를 진행하기 전에 Kubernetes 클러스터에 `Knative`가 설치되어 있어야 합니다.  
> 원래는 클러스터 설정 하단에 있는 Applications에서 쉽게 설치할 수 있지만,  
> (20.1.26 기준) Helm까지는 정상적으로 설치되지만 Knative설치가 정상적으로 진행되지 않습니다.  
> 따라서 **수동으로 Knative를 설치**해주셔야 합니다.  
>
> 다음 링크를 참고해서 설치해주세요.  
> [Knative 설치](https://gruuuuu.github.io/cloud/knative-hands-on/#)  

Settings > Repository > DeployTokens로 이동하여 토큰을 생성해줍니다.  

![image](https://user-images.githubusercontent.com/15958325/73134165-c560de80-4076-11ea-8173-bf2e03959c27.png)  

생성된 토큰은 Settings > CI/CD > Variables로 이동하여   
`CI_DEPLOY_USER`  
`CI_DEPLOY_PASSWORD`  
키 값에 토큰값들을 넣어줍니다.  

![image](https://user-images.githubusercontent.com/15958325/73134181-f3deb980-4076-11ea-9940-fd016a165d76.png)  

## CI/CD 테스트
모든 설정이 끝났으니 이제 실제로 테스트를 진행해봅시다.  

git repository에 어떤 파일이던 생성해서 push해줍니다.  
프로젝트는 해당 링크를 참조 : [Gitlab-CICD-튜토리얼#프로젝트-작성](https://velog.io/@wickedev/Gitlab-CICD-%ED%8A%9C%ED%86%A0%EB%A6%AC%EC%96%BC-bljzphditt#%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EC%9E%91%EC%84%B1)

그 다음, CI/CD > Pipeline으로 이동하면  
push한 git이 pipeline에서 돌아가고 있다는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73134214-4324ea00-4077-11ea-9041-aaf298926bd2.png)  

해당 pipeline을 클릭해보면 현재 job이 어떤 상태인지 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73134234-87b08580-4077-11ea-8a5f-0f8310089a06.png)  

Deploy까지 정상적으로 진행되면 클러스터로 이동해서 서비스가 정상적으로 배포되었는지 확인가능합니다.  
![image](https://user-images.githubusercontent.com/15958325/73134244-a9aa0800-4077-11ea-8d2e-a02f18303d8d.png)  
![image](https://user-images.githubusercontent.com/15958325/73134247-ab73cb80-4077-11ea-92a9-0eff3d936e8d.png)  


완성된 이미지는 Operations > Serverless에서 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/73134253-d2ca9880-4077-11ea-8598-1df020c103a1.png)   

세부적인 커스터마이징은 `.gitlab-ci.yaml`을 통해 가능합니다.  
이 부분은 나중에 시간이 나면 다뤄보도록 하겠습니다.  

----