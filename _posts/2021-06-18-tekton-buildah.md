---
title: "Tekton에서 Buildah 사용해보기"
categories: 
  - Cloud
tags:
  - Kubernetes
  - Tekton
  - CICD
  - DevOps
last_modified_at: 2021-06-18T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 포스팅에서는 클라우드 CI/CD의 중추인 이미지 빌드와 배포에 대해서 알아보겠습니다.  

## Buildah란? 
![image](https://user-images.githubusercontent.com/15958325/122533559-aba1ac00-d05c-11eb-9b3f-60ad18633277.png)  

기존 컨테이너 이미지의 비공식적 표준이었던 도커(Docker)가 CE버전 중단 선언, 무거운 기능으로 더이상 완벽한 오픈소스로서의 역할을 하지 못하게 되었습니다.  

도커는 클라이언트역할을 하는 `Docker CLI`와 서버인 `Docker Daemon`으로 구성됩니다. 그 중 서버는 컨테이너 이미지 빌드, 관리, 실행 등 많은 기능을 담당하는 데몬으로 모든 컨테이너들을 자식 프로세스로 소유하고 있습니다.  
**이로 인해 무거울뿐만 아니라 장애가 발생하면 모든 자식프로세스(컨테이너)에 영향을 끼칠 수 있습니다.**  

이러한 문제점을 해결하기 위해 OCI호환 오픈소스프로젝트인 `CRI-O`(Container Runtime Interface - Open Container Initiative)가 탄생하였습니다.  

CRI-O는 컨테이너의 실행을 목적으로 경량화했기 때문에 도커가 기본적으로 제공했던 컨테이너 생성이나 빌드같은 기능은 제공하지 않았고, 이런 부분에서 여전히 도커가 필요했기 때문에 새로운 툴을 제작하기로 했습니다.  

그렇게 나온 툴들이 `Buildah`, `Podman`, `Skopeo` 입니다.  
  
이 중 `Buildah`는 CRI-O에서 이미지를 빌드할 때 도커의 종속성을 제거하기 위해 개발되었고, Dockerfile없이 다른 스크립트 언어를 사용해 컨테이너 이미지를 빌드하는 것을 목표로 하고 있습니다(Dockerfile로 빌드하는 것도 당연히 지원).   
즉, **OCI 컨테이너 이미지 build&push 역할을 맡은 툴**이라고 보시면 됩니다.  

> 참고 : [OCI와 CRI 중심으로 재편되는 컨테이너 생태계: 흔들리는 도커(Docker)의 위상
](https://www.s-core.co.kr/insight/view/oci%EC%99%80-cri-%EC%A4%91%EC%8B%AC%EC%9C%BC%EB%A1%9C-%EC%9E%AC%ED%8E%B8%EB%90%98%EB%8A%94-%EC%BB%A8%ED%85%8C%EC%9D%B4%EB%84%88-%EC%83%9D%ED%83%9C%EA%B3%84-%ED%9D%94%EB%93%A4%EB%A6%AC%EB%8A%94/)

## Tekton에서 Buildah사용해보기!
그럼 이제 **Tekton**에서 `Buildah`를 사용해 app을 빌드해 container registry에 push해보는 파이프라인을 만들어보도록 하겠습니다.  

### 1. Build할만한 app 만들기
먼저 컨테이너 이미지로 빌드할만한 app을 만들어보겠습니다.  

이번 실습에서는 간단하게 Nodejs express app을 생성한 뒤, 이미지로 빌드해보도록 하겠습니다.  

nvm 설치 :  
~~~
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash

$ source ~/.bashrc

$ nvm -v
  0.38.0
~~~

node 설치(v14.16.0) : 
~~~
$ nvm install 14.16.0
$ node -v
  v14.16.0
$ npm -v
  6.14.11
~~~

express 프로젝트 생성:  
~~~
$ npm install -g express-generator

$ express -e tekton-buildah-express
~~~

~~~
$ tree tekton-buildah-express
  tekton-buildah-express
  ├── app.js
  ├── bin
  │   └── www
  ├── package.json
  ├── public
  │   ├── images
  │   ├── javascripts
  │   └── stylesheets
  │       └── style.css
  ├── routes
  │   ├── index.js
  │   └── users.js
  └── views
      ├── error.ejs
      └── index.ejs

  7 directories, 8 files
~~~

`package-lock.json`을 생성하기 위해 초기 `npm install` 실행:  
~~~
$ npm install
~~~

> **package-lock.json을 생성하는 이유** : 같은 개발 환경을 재현하기 위해...   
>참고링크 : [당신이 npm install을 사용하지 말아야할 때](https://devhyun.com/blog/post/8)


그다음, 이 app을 결국 컨테이너 이미지로 만들어야 하니 **Dockerfile**을 만들어주도록 하겠습니다.  

Dockerfile 생성:  
~~~
FROM node:16.3.0-alpine3.13
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
~~~



### 2. git에 push
repo를 로컬에서 가져올수도 있지만, 추후에 gitops 실습과 연결시키기 위해 git repository로 push하도록 하겠습니다.  

git repository 생성 :
![image](https://user-images.githubusercontent.com/15958325/122633307-da7a5980-d112-11eb-890d-c456e0df402f.png)

git push:  
~~~
$ git init
$ git add .
$ git commit -m "initial commit"
$ git remote add origin {github repository 주소}
$ git push origin master  
~~~
![image](https://user-images.githubusercontent.com/15958325/122642709-c0f30500-d146-11eb-9fec-5b2e8dbf9475.png)  

### 3. Tekton Pipeline 설계
git repository도 만들었으니 이제 Pipeline을 설계해보도록 하겠습니다.  

대충 순서를 정리해보면 다음과 같은 흐름으로 전개될 것입니다.  

1. **git clone** repository
2. **build**(npm install)
3. container registry에 **push**  

### 3-1. [Task1] git clone 
git clone에 관한 Task는 Tekton Hub에 있습니다.  
-> [여기](https://hub.tekton.dev/tekton/task/git-clone)  

Task 배포:  
~~~
$ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.4/git-clone.yaml
~~~

이 Task를 사용하는 pipeline은 **TektonHub**의 `git-clone` task description을 참고하여 설계하도록 합니다.  

~~~
- name: clone-repository
  params:
    - name: url
      value: https://github.com/GRuuuuu/tekton-buildah-express
    - name: revision
      value: "master"
  taskRef:
    kind: Task
    name: git-clone
  workspaces:
    - name: output
      workspace: pipeline-shared-data
~~~

`taskRef` : clone-repository라는 task에서 사용할 task의 이름  
`params` : `git-clone` task에서 사용할 파라미터  
`workspaces` : `git-clone` task에서 사용하는 workspace의 이름과 pipelinerun에 정의된 실제 workspace이름

> `params`와 `workspaces`는 사용할 task의 [description](https://hub.tekton.dev/tekton/task/git-clone)을 참고해서 적어야 합니다.  
> ex) `git-clone` 의 workspace이름은 **output**으로 고정되어있음 -> 반드시 workspaces의 name은 output으로 설정해주어야 함  

### 3-2. [Task2] Build(npm install)
이제 클론받은 repository를 빌드할 차례입니다.  
저희의 샘플 app은 Nodejs express app이므로 `npm install`을 해주도록 합시다.  

TektonHub의 `npm` -> [여기](https://hub.tekton.dev/tekton/task/npm)  

`npm` task 배포 :  
~~~
$ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/npm/0.1/npm.yaml
~~~

마찬가지로 npm task의 description을 참고하여 작성하도록 합니다.  

~~~
- name: install-dependencies
  taskRef:
    name: npm
  workspaces:
    - name: source
      workspace: pipeline-shared-data
  params:
    - name: ARGS
      value:
        - clean-install
  runAfter:
    - clone-repository
~~~
`npm` task의 지정된 workspace 이름은 `source`이므로 똑같이 적어주고, npm install할때의 파라미터는 `clean-install`로 정해주었습니다.  

`runAfter`는 앞의 Task가 끝나고 나서 동기적으로 실행하라 라는 파라미터입니다.  
`npm install`을 하려면 먼저 repository가 있어야 가능하니 Task1번의 `clone-repository` 작업이 완료된 후 실행하도록 `runAfter`구문을 추가시켜주었습니다.  

### 3-3. [Task3] Test
그 다음 제대로 app이 작동하는지 test하는 task도 추가해주도록 합시다.
~~~
- name: run-tests
  taskRef:
    name: npm
  workspaces:
    - name: source
      workspace: pipeline-shared-data
  params:
    - name: ARGS
      value:
        - test
  runAfter:
    - install-dependencies
~~~


### 3-4. [Task4] Push to Container Registry (using `Buildah`)

2번, 3번 task에서 빌드하고 작동테스트까지 진행하였으니, 이제 빌드된 app을 컨테이너 이미지로 말아서 컨테이너 레지스트리에 push할 차례입니다.  

TektonHub의 `Buildah` -> [여기](https://hub.tekton.dev/tekton/task/buildah)  

`Buildah` 배포 :  
~~~
$ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/buildah/0.2/buildah.yaml
~~~

~~~
- name: build-image
  params:
    - name: IMAGE
      value: "$(params.image-repo):$(tasks.clone-repository.results.commit)"
  taskRef:
    kind: Task
    name: buildah
  workspaces:
    - name: source
      workspace: pipeline-shared-data
  runAfter:
    - run-tests
~~~
`params`의 `IMAGE`는 생성된 이미지의 이름을 세팅하는 부분입니다.  
이름 그대로 push될것이기때문에, (이미지이름):(태그)의 형식에 맞춰 적어주셔야 합니다.  

예시의 `IMAGE`를 뜯어보면 다음과 같습니다.     
`$(params.image-repo)` : Pipeline에서 제공하는 Params의 image-repo변수값 -> 이미지 이름  
`$(tasks.clone-repository.results.commit)` : clone-repository task의 결과값 중 commit hash값(unique value) -> 이미지 태그

>CI/CD의 기본은 "지속적인 통합/빌드/배포" 이기 때문에 pipeline이 한번만 실행된다는 생각은 하지 않는 것이 좋습니다.  
>**지속적으로 pipeline이 실행되는 것**을 고려하여, Pipeline 이름도 `generateName`으로 설정해주는 것이 좋고  
>이미지를 빌드할 때에도 유니크한 값을 태그로 주어야 합니다.  
>그래서 위의 예시에서는 clone-repository의 task결과값에서 commit hash값을 유니크한 값으로 사용하고 있습니다.  

### 3-5. 전체 Pipeline 예시  

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
  tasks:
    - name: clone-repository
      params:
        - name: url
          value: https://github.com/GRuuuuu/tekton-buildah-express
        - name: revision
          value: "master"
        - name: deleteExisting
          value: "true"
      taskRef:
        kind: Task
        name: git-clone
      workspaces:
        - name: output
          workspace: pipeline-shared-data
    - name: install-dependencies
      taskRef:
        name: npm
      workspaces:
        - name: source
          workspace: pipeline-shared-data
      params:
        - name: ARGS
          value:
            - clean-install
      runAfter:
        - clone-repository
    - name: run-tests
      taskRef:
        name: npm
      workspaces:
        - name: source
          workspace: pipeline-shared-data
      params:
        - name: ARGS
          value:
            - test
      runAfter:
        - install-dependencies
    - name: build-image
      runAfter:
        - run-tests
      params:
        - name: IMAGE
          value: "$(params.image-repo):$(tasks.clone-repository.results.commit)"
      taskRef:
        kind: Task
        name: buildah
      workspaces:
        - name: source
          workspace: pipeline-shared-data
~~~

배포:  
~~~
$ kubectl get pipeline
NAME                              AGE
tekton-buildah-express-pipeline   5s
~~~

### 4. Workspace로 사용할 PV&PVC 생성
pv(nfs) : 
~~~
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv
spec:
  capacity:
    storage: 200Mi
  accessModes:
    - ReadWriteMany
  nfs:
    server: {NFS_SERVER}
    path: /share/etc
~~~

pvc:  
~~~
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Mi
~~~

~~~
$ kubectl get pv,pvc

NAME                  CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM         STORAGECLASS   REASON   AGE
persistentvolume/pv   200Mi      RWX            Retain           Bound    default/pvc                           12s

NAME                        STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/pvc   Bound    pv       200Mi      RWX                           12s
~~~

>이번 실습에서는 모든 노드에서 접근 가능한 `ReadWriteMany`를 사용하여 pipeline의 task 배포 위치가 중요하지 않으나, `ReadWriteOnce`를 사용하는 경우 pipeline의 배포 위치가 pv,pvc와 **동일한 노드**에 올라갈 수 있도록 조치를 취할 것.  

### 5. Service Account 생성
위에서 생성한 pipeline의 task들중에는 DockerHub에 빌드한 이미지를 push하는 단계가 있습니다.  

아시다시피 DockerHub의 본인 registry에 이미지를 push하려면 "본인인증"이 필요합니다.  
이런 역할을 Kubernetes에서는 secret resource로 관리하고 있습니다.  

그러면 Docker secret을 생성하고 이 secret을 pipeline의 서비스 어카운트에 붙여주도록 하겠습니다.  

Docker secret 생성:  
~~~
$ kubectl create secret docker-registry regcred --docker-username={USERNAME} --docker-password={PASSWD} --docker-email={EMAIL} --docker-server={REG_URL/docker hub 사용시 생략가능}
~~~

Service Account 생성:  
~~~
apiVersion: v1
kind: ServiceAccount
metadata:
  name: build-bot
secrets:
  - name: regcred
~~~

### 6. PipelineRun 생성
이제 pipeline을 돌리기위한 모든 준비가 끝났습니다.  

PipelineRun :  
~~~
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  name: tekton-buildah-express-pipeline-run
spec:
  serviceAccountName: build-bot
  pipelineRef:
    name: tekton-buildah-express-pipeline
  workspaces:
    - name: pipeline-shared-data
      persistentvolumeclaim:
        claimName: pvc
~~~

- PipelineRun에서 사용할 `servceAccount`는 **Docker secret**을 가지고 있는 `build-bot`  
- 돌릴 Pipeline은 `tekton-buildah-express-pipeline`  
- pipeline의 workspace는 `pvc`볼륨을 붙인 `pipeline-shared-data`  

### 7. RUN!
PipelineRun을 실행 :  
~~~
$ tkn pr list
NAME                                  STARTED         DURATION   STATUS
tekton-buildah-express-pipeline-run   2 seconds ago   ---        Running
~~~

로그 확인:  
~~~
$ tkn pr logs tekton-buildah-express-pipeline-run -f

[clone-repository : clone] + '[' false '=' true ]
[clone-repository : clone] + '[' false '=' true ]
[clone-repository : clone] + CHECKOUT_DIR=/workspace/output/
[clone-repository : clone] + '[' true '=' true ]
[clone-repository : clone] + cleandir
[clone-repository : clone] + '[' -d /workspace/output/ ]
...
[build-image : push] Copying config sha256:0d11a7ec4b98ec1f4b726f89dd44deafe78c3ad55f7937027f36f80ea5179c46
[build-image : push] Writing manifest to image destination
[build-image : push] Storing signatures

[build-image : digest-to-results] + cat /workspace/source/image-digest
[build-image : digest-to-results] + tee /tekton/results/IMAGE_DIGEST
[build-image : digest-to-results] sha256:affd4db24f6f763236183bb27902e509eb8e29da15476b8164f64a518adfc078
~~~

성공적으로 종료되면, Container Registry에 빌드한 app이 올라가 있는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/122643761-9c019080-d14c-11eb-9171-143b547b8c1d.png)  

### 마치며
이번 포스팅에서는 `buildah`를 이용하여 app을 빌드하고 push하는 방법에 대해서 알아보았습니다.  
다음 포스팅에서는 **tekton trigger**기능을 사용해 git push event을 감지하면 pipeline을 돌려보는 방법에 대해서 보도록 하겠습니다.

----
