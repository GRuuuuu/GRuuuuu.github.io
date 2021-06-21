---
title: "Tekton Trigger를 사용하여 Pipeline 자동으로 돌려보기"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
last_modified_at: 2021-06-19T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
[지난 포스팅](https://gruuuuu.github.io/cloud/tekton-buildah/)에서는 `Buildah`를 사용하여 nodejs express app을 build하고 container registry에 push하는 파이프라인을 만들어봤습니다.  

하지만 지난 포스팅에서 만든 파이프라인은 실행시킬때마다 수동으로 돌려줘야한다는 불편함이 있었는데요,  
이번 포스팅에서는 `Tekton Trigger` 기능을 사용하여 특정 **이벤트가 발생할때마다 파이프라인을 자동으로 돌려주는 방법**에 대해서 기술하도록 하겠습니다.  



## Tekton Trigger란?
Overview에서 짧게 언급했듯이 Tekton Trigger의 기능은 특정 이벤트를 web hook으로 받아 등록된 pipeline을 실행시키는 역할을 합니다.  

![image](https://user-images.githubusercontent.com/15958325/122644238-26e38a80-d14f-11eb-8d9b-cc023e1a2523.png)  
> 이미지 출처 : [IBM Developer/Tekton Triggers 101](https://developer.ibm.com/devpractices/devops/tutorials/tekton-triggers-101/)   

크게 4가지 구성요소가 있습니다.  

Name|Description
----|----
EventListener|Pod으로 실행되며, 서비스를 노출시켜 HTTP기반의 event를 받아 `Trigger`로 전달
Trigger|전달된 이벤트에 대한 검증, 파싱 로직을 실행시킨 뒤 `Trigger Template`과 `Trigger Binding`을 연결
Trigger Binding| `EventListener`로부터 받은 데이터를 `Trigger Template`의 파라미터와 매핑
Trigger Template|`Trigger Binding`/`EventListener` 로부터 어떤 파라미터를 받을건지, 어떤 파이프라인을 실행시킬건지 정의

아래 실습에서는 이전 포스팅에서 제작했던 [Pipeline](https://gruuuuu.github.io/cloud/tekton-buildah/#3-5-%EC%A0%84%EC%B2%B4-pipeline-%EC%98%88%EC%8B%9C)을 Tekton Trigger로 실행시켜보도록 하겠습니다.  

## 1. Tekton Trigger 배포하기
### Prerequisites
1. Kubernetes v1.16이상
2. 현재 유저가 `Cluster-admin` 권한을 소유하고 있어야 함
3. Tekton Pipeline이 설치되어 있어야 함

### Installation
Tekton Trigger 배포:  
~~~
$ kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/previous/v0.14.2/release.yaml
~~~
> Tekton Trigger 버전 정보 : [Tekton Triggers Release](https://github.com/tektoncd/triggers/releases)  

확인:  
~~~
$ kubectl get pods --namespace tekton-pipelines

NAME                                           READY   STATUS    RESTARTS   AGE
tekton-dashboard-597868947b-jgf4p              1/1     Running   0          26d
tekton-pipelines-controller-5f88bb8695-r87jh   1/1     Running   0          26d
tekton-pipelines-webhook-77d48dc65c-2snwz      1/1     Running   0          26d
tekton-triggers-controller-7bdc5c466-sgw9h     1/1     Running   0          11s
tekton-triggers-webhook-7b59947444-tvdfs       1/1     Running   0          11s
~~~

## [복습] 무슨 Pipeline이었지?
참고 : [Tekton에서 Buildah 사용해보기
-Pipeline](https://gruuuuu.github.io/cloud/tekton-buildah/#3-5-%EC%A0%84%EC%B2%B4-pipeline-%EC%98%88%EC%8B%9C)  

![그림1](https://user-images.githubusercontent.com/15958325/122646424-0240e000-d15a-11eb-9bf9-210fa4fb2fab.png)  
대략 이런 내용의 파이프라인입니다.  

이제 **Trigger**를 사용해 **Github repository에 push 이벤트가 일어날 때마다 요 파이프라인을 실행**시켜보도록 하겠습니다.  

## 2. Trigger Binding 만들기
`Trigger Binding`에서는 **이벤트로부터 어떤 파라미터를 받아서 넘겨줄지 정의**하는 부분입니다.  

이 부분에서는 이벤트에서 어떤 payload를 날리는지 파악하는 것이 중요합니다.  
이번 실습에서는 Github의 **Webhook** 이벤트의 Payload를 받아서 처리할 것이므로 어떤 파라미터가 있는지 알아야 합니다.  

참고 : [Github Webhook events and payloads](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)  

이번 실습에서 Github에 관련된 task는 1번task(`git-clone`)밖에 없고 사용하는 파라미터는 `git repo url`와 `revision`입니다.  
~~~yaml
# task1번
- name: clone-repository
  params:
    - name: url
      value: https://github.com/GRuuuuu/tekton-buildah-express
    - name: revision
      value: "master"
    - name: deleteExisting
      value: "true"
~~~

Github webhook payload를 살펴보니 관련된 파라미터는 `repository.url`과 마스터 브랜치 이름을 나타내는 `repository.master_branch`가 있습니다.  

파라미터를 참고하여 Trigger Binding을 작성하면 다음과 같이 나타낼 수 있습니다.  
~~~
apiVersion: triggers.tekton.dev/v1alpha1
kind: TriggerBinding
metadata:
  name: triggerbinding
spec:
  params:
    - name: giturl
      value: $(body.repository.url)
    - name: gitrevision
      value: $(body.repository.master_branch)
~~~

## 3. Trigger Template 만들기
`Trigger binding`에서 어떤 파라미터를 받아서 넘겨받을지를 정의했으니 이제 `Trigger Template`에서 `PipelineRun`으로 무슨 파라미터를 넘길지, 어떤 Pipeline을 실행시킬지 정의할 차례입니다.  

`Trigger Template`을 먼저 선언하고, 그 안에 이벤트를 받으면 실행시킬 `PipelineRun`을 정의하면 됩니다.  
~~~
apiVersion: triggers.tekton.dev/v1alpha1
kind: TriggerTemplate
metadata:
  name: triggertemplate
spec:
  params:
    - name: gitrevision
      description: git revision(master branch name)
      default: master
    - name: giturl
      description: git repository url
  resourcetemplates:
    - apiVersion: tekton.dev/v1beta1
      kind: PipelineRun
      metadata:
        generateName: tekton-buildah-express-pipeline-run-
      spec:
        serviceAccountName: build-bot
        pipelineRef:
          name: tekton-buildah-express-pipeline
        params:
          - name: git-revision
            value: $(tt.params.gitrevision)
          - name: git-url
            value: $(tt.params.giturl) 
        workspaces:
          - name: pipeline-shared-data
            persistentvolumeclaim:
              claimName: pvc
~~~
>Parameter 받는 방법 참고: [Pipeline에서 parameter 다루기](https://gruuuuu.github.io/cloud/tekton-install/#5-%EC%B0%B8%EA%B3%A0-pipeline%EC%97%90%EC%84%9C-parameter-%EB%8B%A4%EB%A3%A8%EA%B8%B0)

Trigger Binding에서 파라미터를 받아올때에는 `$(tt.params.{name})`형식을 사용하시면 됩니다.  

> PipelineRun의 이름이 `generateName`인 이유는... push이벤트가 올때마다 파이프라인을 생성해야하기때문에 유니크한 이름을 주기 위해서!

## 4. Pipeline 수정하기
현재 Pipeline의 `git-clone` task는 변수를 받지 않고 하드코딩된 변수를 사용하고 있습니다.  
이 부분을 변수를 받아오도록 수정해주도록 하겠습니다.  
~~~
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: tekton-buildah-express-pipeline
spec:
  workspaces:
    - name: pipeline-shared-data
      description: |
        This workspace will be shared throughout all steps.
  params:
    - name: image-repo
      type: string
      description: Docker image name
      default: kongru/tekton-buildah-express
    - name: git-url
      type: string
    - name: git-revision
      type: string
      default: master
  tasks:
    - name: clone-repository
      params:
        - name: url
          value: "$(params.git-url)"
        - name: revision
          value: "$(params.git-revision)"
        - name: deleteExisting
          value: "true"
      taskRef:
        kind: Task
        name: git-clone
      workspaces:
        - name: output
          workspace: pipeline-shared-data
...
~~~
`spec.params`에 변수를 추가해주었고, `clone-repository`의 params를 수정해주었습니다.  

## 5. EventListener 정의하기
`Trigger Binding`, `Trigger Template`, `Pipline`까지 준비를 마쳤습니다.  

그럼 이제 Event를 제일 처음으로 받아주고 Trigger Binding과 Trigger Template을 이어주는 `EventListener`를 정의하도록 하겠습니다.  

~~~
apiVersion: triggers.tekton.dev/v1alpha1
kind: EventListener
metadata:
  name: trigger-eventlistner
spec:
  serviceAccountName: tekton-triggers-sa
  triggers:
    - bindings:
        - ref: triggerbinding
      template:
        ref: triggertemplate
~~~

spec의 triggers아래 연결해줄 binding과 template의 이름을 기재해주고,  
이 `EventListener`의 서비스 어카운트를 등록해주면 됩니다.  

## 6. EventListener의 Service Account 만들기
EventListener는 실제 Pod으로 동작하며 Event를 받아주는 역할을 합니다.  
그리고 `TriggerBinding`과 `TriggerTemplate`을 참고하여 `Pipeline`까지 실행시켜야하니 그에 맞는 권한을 부여해주어야 합니다.  


### 5.1 Webhook Service Account생성

~~~
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tekton-triggers-sa
~~~

### 5.3 Role&RoleBinding 
~~~
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: tekton-triggers-role
rules:
# EventListeners need to be able to fetch all namespaced resources
- apiGroups: ["triggers.tekton.dev"]
  resources: ["eventlisteners", "triggerbindings", "triggertemplates", "triggers"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
 # secrets are only needed for GitHub/GitLab interceptors
 # configmaps is needed for updating logging config
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
 # Permissions to create resources in associated TriggerTemplates
- apiGroups: ["tekton.dev"]
  resources: ["pipelineruns", "pipelineresources", "taskruns"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["serviceaccounts"]
  verbs: ["impersonate"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tekton-triggers-rolebinding
subjects:
- kind: ServiceAccount
  name: tekton-triggers-sa
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: tekton-triggers-role
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tekton-triggers-clusterrole
rules:
  # EventListeners need to be able to fetch any clustertriggerbindings
- apiGroups: ["triggers.tekton.dev"]
  resources: ["clustertriggerbindings","clusterinterceptors"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tekton-triggers-clusterbinding
subjects:
- kind: ServiceAccount
  name: tekton-triggers-sa
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: tekton-triggers-clusterrole
~~~

## 7. EventListener 서비스 생성
여기까지 따라오셨다면 현재 EventListener pod이 떠있는 상태일겁니다.  
~~~
$ kubectl get pod
NAME                                                              READY   STATUS      RESTARTS   AGE
el-trigger-eventlistner-766cc5cb54-pzzmf                          0/1     Running     0          6s

$ kubectl get svc
NAME                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
el-trigger-eventlistner   ClusterIP   10.101.123.71   <none>        8080/TCP   12m
~~~

EventListener는 외부로부터 이벤트를 수신해야하는 pod이기 때문에 서비스가 있어야 하고 외부로 노출되어야 합니다.  

두가지 방법으로 노출시킬수가 있는데요, 
1. Ingress사용 
2. Route사용  

2번방법인 Route는 Openshift를 사용할 경우이므로 이번 실습에서는 Ingress를 사용해 서비스를 외부로 노출시키도록 하겠습니다.  

### 7.1 Nginx Ingress Controller 배포

[Nginx Ingress Controller/Deployment Guide](https://kubernetes.github.io/ingress-nginx/deploy/)
~~~
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.47.0/deploy/static/provider/cloud/deploy.yaml
~~~

### 7.2 Ingress 배포 
~~~
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-resource
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {EVENTLISTENER_SERVICE_NAME}
                port:
                  number: 8080
~~~
서비스 이름을 적어주고 배포

### 7.3 Ingress 서비스 확인

제대로 연결이 되었는지 확인해보도록 하겠습니다.  

~~~
$ kubectl get svc -A
NAMESPACE          NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                              AGE
default            el-trigger-eventlistner              ClusterIP      10.101.123.71    <none>        8080/TCP                             11h
default            kubernetes                           ClusterIP      10.96.0.1        <none>        443/TCP                              27d
ingress-nginx      ingress-nginx-controller             LoadBalancer   10.97.152.72     <pending>     80:30275/TCP,443:30123/TCP           6s
ingress-nginx      ingress-nginx-controller-admission   ClusterIP      10.108.133.7     <none>        443/TCP                              6s
kube-system        kube-dns                             ClusterIP      10.96.0.10       <none>        53/UDP,53/TCP,9153/TCP               27d
tekton-pipelines   tekton-dashboard                     NodePort       10.106.171.200   <none>        9097:31364/TCP                       27d
tekton-pipelines   tekton-pipelines-controller          ClusterIP      10.106.198.29    <none>        9090/TCP,8080/TCP                    27d
tekton-pipelines   tekton-pipelines-webhook             ClusterIP      10.109.254.8     <none>        9090/TCP,8008/TCP,443/TCP,8080/TCP   27d
tekton-pipelines   tekton-triggers-controller           ClusterIP      10.109.87.249    <none>        9000/TCP                             37h
tekton-pipelines   tekton-triggers-webhook              ClusterIP      10.105.168.218   <none>        443/TCP                              37h
~~~

서비스를 출력했을때 위와 비슷하게 나올것입니다.  
이중에서 `ingress-nginx-controller`의 서비스 타입은 `LoadBalancer`로 되어있을텐데, 클라우드 로드밸런서를 사용하지 않는 이상 `<pending>`으로 떠있어 외부 ip를 받아오지 못하는 상태입니다.  

로드밸런서 타입을 노드포트 타입으로 바꿔주도록 하겠습니다.  
~~~
$ kubectl edit svc ingress-nginx-controller -n ingress-nginx
~~~
![image](https://user-images.githubusercontent.com/15958325/122704001-b1ca9f00-d28d-11eb-9295-7d298b63fd96.png)    

`externalTrafficPolicy: Local`줄을 삭제하고  
type을 `NodePort`로 변경해줍니다.  

80포트의 노드포트로 `30275`포트가 외부로 개방되어있으므로, 노드 ip와 노드포트로 서비스를 노출시킬 수 있습니다.  

`curl`로 서비스 연결 확인
~~~
$ curl http://{NODE_IP}:30275/
{"eventListener":"trigger-eventlistner","namespace":"default","eventListenerUID":"","errorMessage":"Invalid event body format format: unexpected end of JSON input"}
~~~
위와 같이 `JSON`인풋이 없어 에러가 난다는 메세지를 받으면 정상적으로 연동이 된 것입니다.  
만약 503에러가 뜬다면 `EventListener` pod이 정상적으로 뜨지 않은것이니 확인해주시면 되겠습니다.  

### 7.4 Github Webhook에 EventListener 등록하기
Push이벤트를 받고싶어하는 Repository의  
settings > webhooks > add webhook  

![image](https://user-images.githubusercontent.com/15958325/122704119-f81ffe00-d28d-11eb-9e05-15dc59c5f28c.png)  
Payload url에는 EventListener의 IP 또는 주소를 작성해주시면 됩니다.  

webhook test를 성공적으로 마치면 아래와같이 초록색 체크표시가 뜹니다.  
![image](https://user-images.githubusercontent.com/15958325/122704199-29003300-d28e-11eb-9b6f-95743a10c0ca.png)    

## 8. TEST!
### 8.1 Push 이벤트 발생시키기!
push 이벤트를 발생시키기 위해 index.ejs파일을 아래와 같이 수정한다음에 push해주도록 하겠습니다.  
~~~html
<!DOCTYPE html>
<html>
  <head>
    <title><%= title %></title>
    <link rel='stylesheet' href='/stylesheets/style.css' />
  </head>
  <body>
    <h1><%= title %></h1>
    <p>Welcome to <%= title %></p>
    <p>Hello Tekton Trigger!!!</p>
  </body>
</html>
~~~

### 8.2 Pipeline 확인
Push Event를 발생시키고나서 PipelineRun을 살펴보면 새로 생성되어 돌고 있는 모습을 확인할 수 있습니다.  
~~~
$ tkn pr list
NAME                                        STARTED         DURATION     STATUS
tekton-buildah-express-pipeline-run-8kt28   7 seconds ago   ---          Running
~~~

~~~
$ tkn pr logs tekton-buildah-express-pipeline-run-8kt28

...
[clone-repository : clone] + /ko-app/git-init '-url=https://github.com/GRuuuuu/tekton-buildah-express' '-revision=master' '-refspec=' '-path=/workspace/output/' '-sslVerify=true' '-submodules=true' '-depth=1' '-sparseCheckoutDirectories='
...
~~~
로그중간에 보면 제대로 `git url`정보와 `revision`정보를 받아서 `git-clone` task를 실행하고 있는 모습을 확인할 수 있습니다.  


## 9. Troubleshooting
### 9.1 Webhook deliver가 실패한경우
![image](https://user-images.githubusercontent.com/15958325/122704290-55b44a80-d28e-11eb-9931-0c3512947ecc.png)  

디버깅하는 방법:  

로컬 테스트를 위해 포트포워딩
~~~
$ kubectl port-forward el-seung-trigger-eventlistner-d95d9b5cd-vvhzk 8080:8080
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
~~~

터미널 하나 띄워서 Eventlistener 로그띄움  
~~~
$ kubectl logs el-seung-trigger-eventlistner-d95d9b5cd-vvhzk -f
~~~

간단한 커밋이벤트 발생  
~~~
$ curl -X POST \
    -d '{"head_commit": {"id": "851f5af8d73e8aa9c53e76d0605fbaf53b9a09f6"}, "repository": {"url": "https://github.com/GRuuuuu/tekton-buildah-express", "name": "tekton-buildah-express"}}' \
    -H "Content-Type: application/json" \
    http://localhost:8080
~~~

에러발생!
~~~
curl: (52) Empty reply from server
~~~

Eventlistener 로그를 확인해보니 아래와 같은 에러 발견:  
~~~
{"level":"fatal","logger":"eventlistener","caller":"sink/sink.go:73","msg":"Error getting EventListener seung-trigger-eventlistner in Namespace seung-pipeline-from-scratch: eventlisteners.triggers.tekton.dev \"seung-trigger-eventlistner\" is forbidden: User \"system:serviceaccount:seung-pipeline-from-scratch:tekton-triggers-sa\" cannot get resource \"eventlisteners\" in API group \"triggers.tekton.dev\" in the namespace \"seung-pipeline-from-scratch\"","knative.dev/controller":"eventlistener","stacktrace":"github.com/tektoncd/triggers/pkg/sink.Sink.HandleEvent\n\t/opt/app-root/src/go/src/github.com/tektoncd/triggers/pkg/sink/sink.go:73\nnet/http.HandlerFunc.ServeHTTP\n\t/usr/lib/golang/src/net/http/server.go:2036\nnet/http.(*ServeMux).ServeHTTP\n\t/usr/lib/golang/src/net/http/server.go:2416\nnet/http.serverHandler.ServeHTTP\n\t/usr/lib/golang/src/net/http/server.go:2831\nnet/http.(*conn).serve\n\t/usr/lib/golang/src/net/http/server.go:1919"}
~~~

중요한 메세지는  
**cannot get resource \"eventlisteners\" in API group \"triggers.tekton.dev\" in the namespace**  

EventListener에 달린 서비스어카운트가 `triggers.tekton.dev` API 그룹에 대한 리소스를 가져올 수 없다는 것.  

`can-i`로 권한확인
~~~
$ kubectl auth can-i get el --as system:servicount:seung-pipeline-from-scratch:tekton-triggers-sa
no
~~~

Role&ClusterRole확인 후 적당한 권한으로 수정  

~~~
$ kubectl auth can-i get el --as system:serviceaccount:seung-pipeline-from-scratch:tekton-triggers-sa
yes
~~~

----