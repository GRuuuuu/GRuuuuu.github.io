---
title: "Tekton Tutorial - Tekton Hub 사용법"
slug: tekton-catalog
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
date: 2021-06-13T13:00:00+09:00
---

## Overview
이전 포스팅에서는 Tekton의 가장 기본적인 요소들, Task와 Pipeline에 대해서 알아보았습니다.([Tekton Tutorial - Task와 PipelineRun 다뤄보기!](https://gruuuuu.github.io/cloud/tekton-install/))  

이번 포스팅에서는 Tekton을 좀 더 쉽게(?) 사용할 수 있게 만들어주는 Tekton Hub에 대해서 알아보겠습니다.  


## Tekton Hub란? 
![image](https://user-images.githubusercontent.com/15958325/121805581-c358e900-cc86-11eb-8055-9487c8b6811f.png)  


Tekton의 가장 큰 장점 중 하나는 **각 요소가 모듈화가 되어있어 재사용이 가능**하다는 점인데요, 그래서 다른사람이 미리 정의해둔 task도 가져다가 사용할 수 있습니다.  

그런 **이미 정의된 Task들**을 모아둔 곳이 **Tekton Hub**입니다.  

(21.06.13)현재는 Tekton Hub에서 Task만 지원하지만 추후 Pipeline이나 Trigger 템플릿도 제공할 예정이라고 합니다.  

### 사용방법!
사용방법은 매우 간단합니다.  

**Tekton Hub 사이트 접속** -> [hub.tekton.dev](https://hub.tekton.dev/)  

![image](https://user-images.githubusercontent.com/15958325/121807783-99a4bf80-cc90-11eb-92f7-4b0677306c7b.png)  
 
현재 사용가능한 Task들이 메인페이지에 뜨고 왼쪽 카테고리에서 Task 종류별로 검색할 수 있습니다.  

### (예시) Curl task 사용해보기
한번 `Curl` 명령어에 대한 Task를 클러스터에 배포해서 사용해보도록 하겠습니다.  

**Tekton Hub**에서 Curl 검색:  
![image](https://user-images.githubusercontent.com/15958325/121808003-99f18a80-cc91-11eb-85c2-29991db0637a.png)  

버전과, 해당 Task에 대한 description을 확인할 수 있습니다.  

클러스터에 배포하려면 **Install the Task** 항목을 참고하시면 됩니다.  

~~~
$ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/curl/0.1/curl.yaml
~~~

그 다음, Description의 Parameter항목을 참고하여, 이 Task를 사용하는 TaskRun 또는 Pipeline을 생성하면 끝입니다.  

예시)  
~~~
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: curl-task-run-
spec:
  taskRef:
    kind: Task
    name: curl
  params:
    - name: url
      value: "https://google.com"
    - name: options
      value:
        - "--silent"
~~~

### 여담

**Tekton** 자체는 beta버전오면서 어느정도 안정된 모습을 보여주고 있지만, **Tekton Hub**의 Task들은 아직 완성도가 그리 높지는 않습니다.  

빠른 속도로 피드백을 받아가며 변화하고 있으니 추후에는 더 나은 모습을 보여줄거라고 생각합니다 :)

----
