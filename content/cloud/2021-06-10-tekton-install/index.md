---
title: "Tekton Tutorial - Task와 PipelineRun 다뤄보기!"
slug: tekton-install
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
date: 2021-06-12T13:00:00+09:00
---

## Overview
이전 포스팅에서는 `Tekton`이 무엇이고, Tekton의 컴포넌트에 대해서 알아보았습니다.  
이번 포스팅에서는 Tekton을 설치해보고, 쿠버네티스 클러스터와 어떻게 상호작용을 할 수 있는지 실습을 진행하겠습니다.  

참고 : [tekton.dev - getting started](https://tekton.dev/docs/getting-started/)

## 1. Tekton 설치하기
tekton (`v0.24.1`) 설치
~~~
$ kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/previous/v0.24.1/release.yaml
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

## 2. Tekton CLI 설치
Tekton CLI는 tekton 컴포넌트들을 쉽게 볼 수 있게 해주는 역할을 합니다.  
(그냥 `kubectl get task` 이런식으로 볼 수도 있음)  

먼저 OS에 따라 맞는 버전을 설치해주세요.  
[tektoncli - releases](https://github.com/tektoncd/cli/releases)  

저는 리눅스용으로 받았습니다.  
rpm으로 설치 :  
~~~
$ rpm -Uvh https://github.com/tektoncd/cli/releases/download/v0.18.0/tektoncd-cli-0.18.0_Linux-64bit.rpm

Retrieving https://github.com/tektoncd/cli/releases/download/v0.18.0/tektoncd-cli-0.18.0_Linux-64bit.rpm
Preparing...                          ################################# [100%]
Updating / installing...
   1:cli-0:0.18.0-1                   ################################# [100%]
~~~

cli 설치 완료
~~~
$ tkn version

Client version: 0.18.0
Pipeline version: v0.24.1
~~~

## 3. Task 돌려보기!
tekton 설치가 완료되었으니 이번엔 tekton으로 돌릴 수 있는 최소단위인 task를 돌려보도록 하겠습니다.  

### 3.1 Task 정의
먼저 아래와 같은 간단한 task를 정의합니다.  
~~~
$ vim task-hello.yaml

apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: hello
spec:
  steps:
    - name: hello
      image: ubuntu
      command:
        - echo
      args:
        - "Hello World!"
~~~
task는 작업하나를 나타내는 step의 집합입니다.  
그래서 spec부분에는 각 step들이 정의가 되어있습니다.  

예시의 `hello`라는 step은 `ubuntu`이미지의 `echo`커맨드로 `"Hello World"`라는 문자열을 출력하는 작업입니다.  

### 3.2 Task 배포
task를 Kubernetes 클러스터에 배포:  
~~~
$ kubectl apply -f task-hello.yaml
~~~

배포된 Task를 확인하려면:  
~~~
$ kubectl get task
NAME    AGE
hello   4s
~~~
또는
~~~
$ tkn task list
NAME    DESCRIPTION   AGE
hello                 3 minutes ago
~~~

### 3.3 Task 실행
지금은 단순히 작업들의 나열이 클러스터에 배포된 상태입니다.  
이 작업들을 실행시키려면 `tkn` 커맨드를 사용하거나, `taskrun`파일을 생성하여 실행할 수 있습니다.  

`tkn start` 사용 :  
~~~
$ tkn task start hello
TaskRun started: hello-run-lzspr
~~~

또는 TaskRun파일을 만들어서 실행할수도 있습니다.  
위의 명령어에 `--dry-run`를 붙이면 `TaskRun` yaml파일을 출력합니다.  
이걸 파일로 떨어뜨려서 따로 `kubectl create`로 실행시키면 끝입니다.  
~~~
$ tkn task start hello --dry-run

apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  creationTimestamp: null
  generateName: hello-run-
  namespace: default
spec:
  resources: {}
  serviceAccountName: ""
  taskRef:
    name: hello
status:
  podName: ""
~~~

~~~
$ tkn task start hello --dry-run > taskRun-hello.yaml
~~~

> `metadata`의 `generateName`은 yaml파일을 실행할 때마다 새로운 이름을 부여해줍니다.  
> 일반적으로 적는 `name`대신, `generateName`에 `{NAME}-` 형식으로 적어주면 됩니다.  
>
>CICD파이프라인의 경우 동일한 파이프라인을 트리거를 통해 자동으로 실행하기 때문에 `generateName`을 써주는게 일반적입니다.  

### 3.4 실행된 Task 확인하기
실행된 Task들의 리스트를 보려면 :   
~~~
$ tkn taskrun list

NAME              STARTED          DURATION     STATUS
hello-run-lzspr   14 seconds ago   10 seconds   Succeeded
~~~
또는
~~~ 
$ kubectl get taskrun

NAME              SUCCEEDED   REASON      STARTTIME   COMPLETIONTIME
hello-run-lzspr   True        Succeeded   88s         78s
~~~

### 3.5 Task 로그 확인
~~~
$ tkn tr logs hello-run-lzspr

[hello] Hello World!
~~~

`--last`를 붙이면 가장 최근에 실행한 TaskRun의 로그를 출력합니다.(`-f`는 끊어지지 않고 계속 출력)  
~~~
$ tkn tr logs hello-run-lzspr --last -f

[hello] Hello World!
~~~


## 4. Pipeline 돌려보기!

이번엔 task들의 집합인 Pipeline을 만들어서 돌려보도록 하겠습니다.  

### 4.1 task생성 및 배포
위에서 생성한 task와 별개로 새로운 task를 하나 생성해주도록 합시다.  

~~~
$ vim task-goodbye.yaml

apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: goodbye
spec:
  steps:
    - name: goodbye
      image: ubuntu
      script: |
        #!/bin/bash
        echo "Goodbye World!"
~~~

아까 task와 유사하게,  
`ubuntu`이미지에서 script를 실행하는데 `"Goodbye World"`를 출력하는 작업을 합니다.  

### 4.2 Pipeline 생성 및 배포 
이제 각 task를 실행할 Pipeline을 생성하겠습니다.  
~~~
$ vim pipeline.yaml

apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: hello-goodbye
spec:
  tasks:
  - name: hello
    taskRef:
      name: hello
  - name: goodbye
    runAfter:
     - hello
    taskRef:
      name: goodbye
~~~
Pipeline의 Spec에는 Task들의 나열이 정의되어 있습니다.  
이름과 `taskRef`를 통해 배포된 Task들을 명시할 수 있습니다.  

배포:  
~~~
$ kubectl apply -f pipeline.yaml

pipeline.tekton.dev/hello-goodbye created
~~~
### 4.3 PipelineRun 생성 및 배포
> *) task를 실행시킬때와 다르게 Pipeline을 실행시킬 때에는 따로 TaskRun을 만들 필요가 없습니다.  

TaskRun과 유사하게 `--dry-run`을 통해 PipelineRun yaml파일을 얻어낼 수 있습니다.  

~~~
$ tkn pipeline start hello-goodbye --dry-run

apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  creationTimestamp: null
  generateName: hello-goodbye-run-
  namespace: default
spec:
  pipelineRef:
    name: hello-goodbye
status: {}
~~~

배포:  
~~~
$ tkn pipeline start hello-goodbye --dry-run > pipelineRun-hello-goodbye.yaml

$ kubectl create -f pipelineRun-hello-goodbye.yaml
~~~

### 4.4 결과 확인
로그를 출력해보면:  
~~~
$ tkn pipelinerun logs --last -f

[hello : hello] Hello World!
[goodbye : goodbye] Goodbye World!
~~~

두 개의 task가 정상적으로 실행되는 것을 확인할 수 있습니다.  

## 5. [참고] Pipeline에서 parameter 다루기
PipelineRun에서는 Pipeline를 실행시키는 역할을 할 뿐만 아니라 특정 파라미터를 넘길 수 있습니다.  

### 5.1 PipelineRun에서 Pipeline으로 넘길 파라미터 정의
위에서 만들었던 task와 pipeline들을 약간만 수정해보도록 하겠습니다.  
원래는 지정된 문장을 출력하는 task였지만, **PipelineRun에서 넘겨주는 문장을 출력**하도록 바꿔보도록 하겠습니다.  

~~~
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  creationTimestamp: null
  generateName: hello-goodbye-run-
  namespace: default
spec:
  pipelineRef:
    name: hello-goodbye
  params:
    - name: whatyousay
      value: helllllloooooo
~~~
spec의 params에서 변수이름과 값을 정의  

### 5.2 Pipeline에서 task로 넘길 파라미터 정의
~~~
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: hello-goodbye
spec:
  params:
    - name: whatyousay
      type: string
      description: ddd
      default: byebye
  tasks:
  - name: hello
    taskRef:
      name: hello
    params:
      - name: whatyousay
        value: "$(params.whatyousay)"
~~~
`spec.params`에서 PipelineRun에서 넘어올 변수의 이름과 `type`, `description`, 넘어올 값이 없을 경우의 `default`값을 정의  

task로 넘길 변수는 `tasks`의 `task`아래 `params`에 정의  

### 5.3 받아온 파라미터를 어떻게 사용할 지 task에 정의
~~~
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: hello
spec:
  params:
    - name: whatyousay
      type: string
  steps:
    - name: hello
      image: ubuntu
      command:
        - echo
      args:
        - "$(params.whatyousay)"
~~~
`Pipeline`과 마찬가지로 어떤 변수를 사용할건지 `spec.params`에 선언  

`steps`에 받아온 파라미터를 어떻게 사용할 건지 정의   

### 5.4 로그 확인

~~~
$ tkn pr logs hello-goodbye-run-fk6gf

[hello : hello] helllllloooooo
~~~
파이프라인을 실행 후, 로그를 확인해보니 정상적으로 PipelineRun에서 받아온 변수를 출력하는 것을 확인할 수 있습니다.  


## 6. Tekton Dashboard
![image](https://user-images.githubusercontent.com/15958325/121780431-3e64c580-cbdb-11eb-88bf-4b3ceedf6bb7.png)  

> 참고 : [Tekton.dev -Dashboard](https://tekton.dev/docs/dashboard/)  

지금까지는 CLI환경에서 Tekton을 다뤄봤습니다.  
아직 기능이 많지는 않지만 Tekton에서는 자체 Dashboard도 제공하고 있습니다.  

근데 Dashboard 버전별로 호환 가능한 Tekton Pipeline버전이 있으니 아래 링크를 참고하여 맞는 버전을 설치하면 됩니다.  
[Tekton Dashboard - Which version should I use?](https://github.com/tektoncd/dashboard#which-version-should-i-use)  

| Version | Docs | Pipelines | Triggers |
| ------- | ---- | --------- | -------- |
| [HEAD](./DEVELOPMENT.md) | [Docs @ HEAD](./docs/README.md) | v0.20.x - v0.24.x | v0.10.x - 0.14.x |
| [v0.17.0](https://github.com/tektoncd/dashboard/releases/tag/v0.17.0) | [Docs @ v0.17.0](https://github.com/tektoncd/dashboard/tree/v0.17.0/docs) | v0.20.x - v0.24.x | v0.10.x - 0.14.x |
| [v0.16.1](https://github.com/tektoncd/dashboard/releases/tag/v0.16.1) | [Docs @ v0.16.1](https://github.com/tektoncd/dashboard/tree/v0.16.1/docs) | v0.20.x - v0.23.x | v0.10.x - 0.13.x |
| [v0.15.0](https://github.com/tektoncd/dashboard/releases/tag/v0.15.0) | [Docs @ v0.15.0](https://github.com/tektoncd/dashboard/tree/v0.15.0/docs) | v0.20.x - v0.22.x | v0.10.x - 0.12.x |
| [v0.14.0](https://github.com/tektoncd/dashboard/releases/tag/v0.14.0) | [Docs @ v0.14.0](https://github.com/tektoncd/dashboard/tree/v0.14.0/docs) | v0.11.x - v0.20.x | v0.5.x - 0.11.x |
| [v0.13.0](https://github.com/tektoncd/dashboard/releases/tag/v0.13.0) | [Docs @ v0.13.0](https://github.com/tektoncd/dashboard/tree/v0.13.0/docs) | v0.11.x - v0.20.x | v0.5.x - 0.10.x |
| [v0.12.0](https://github.com/tektoncd/dashboard/releases/tag/v0.12.0) | [Docs @ v0.12.0](https://github.com/tektoncd/dashboard/tree/v0.12.0/docs) | v0.11.x - v0.19.x | v0.5.x - 0.10.x |
| [v0.11.1](https://github.com/tektoncd/dashboard/releases/tag/v0.11.1) | [Docs @ v0.11.1](https://github.com/tektoncd/dashboard/tree/v0.11.1/docs) | v0.11.x - v0.18.x | v0.5.x - 0.9.x |
| [v0.10.2](https://github.com/tektoncd/dashboard/releases/tag/v0.10.2) | [Docs @ v0.10.2](https://github.com/tektoncd/dashboard/tree/v0.10.2/docs) | v0.11.x - v0.17.x | v0.5.x - 0.9.x |
| [v0.9.0](https://github.com/tektoncd/dashboard/releases/tag/v0.9.0) | [Docs @ v0.9.0](https://github.com/tektoncd/dashboard/tree/v0.9.0/docs) | v0.11.x - v0.15.x | v0.5.x - 0.7.x |
| [v0.8.2](https://github.com/tektoncd/dashboard/releases/tag/v0.8.2) | [Docs @ v0.8.2](https://github.com/tektoncd/dashboard/tree/v0.8.2/docs) | v0.11.x - v0.14.x | v0.5.x - 0.6.x |
| [v0.7.1](https://github.com/tektoncd/dashboard/releases/tag/v0.7.1) | [Docs @ v0.7.1](https://github.com/tektoncd/dashboard/tree/v0.7.1/docs) | v0.11.x - v0.13.x | v0.5.x - 0.6.x |
| [v0.6.1.5](https://github.com/tektoncd/dashboard/releases/tag/v0.6.1.5) | [Docs @ v0.6.1.5](https://github.com/tektoncd/dashboard/tree/v0.6.1.5/docs) | v0.11.x - v0.12.x | v0.4.x |  


이 포스팅에서는 Tekton Pipeline `v0.24.1`을 사용하고 있으니, 현재(21.06.13)가장 최신인 Dashboard `v0.17.0`을 설치해보겠습니다.  

~~~
$ kubectl apply --filename https://github.com/tektoncd/dashboard/releases/download/v0.17.0/tekton-dashboard-release.yaml
~~~

> [Tekton Dashboard Release -versions](https://github.com/tektoncd/dashboard/releases)

서비스를 외부에 노출시킨 뒤, 접속해보면 다음과 같은 GUI 화면을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/121780564-e4183480-cbdb-11eb-93a7-0b62b2da4318.png)  
![image](https://user-images.githubusercontent.com/15958325/121780566-e5e1f800-cbdb-11eb-8f8e-305c979a6ef5.png)

----