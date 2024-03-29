---
title: "Openshift4 OperatorHub 구성"
categories: 
  - OCP
tags:
  - Kubernetes
  - RHCOS
  - Openshift
last_modified_at: 2021-07-18T13:00:00+09:00
toc : true
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
OperatorHub는 RedHat에서 Openshift사용자들이 편하게 app을 배포&관리할 수 있도록 패키징해둔 App(Operator)들의 집합입니다.  

이 Operator는 OLM(Operator Lifecycle Manager)에 의해 관리됩니다. 여기에 대한 내용은 추후에 더 자세히 다뤄보기로 하고...  

Online환경에서 Openshift클러스터를 구성하게 되면 자동으로 OperatorHub를 구성해서 Openshift의 web console에서 카탈로그를 확인하실 수 있습니다.  
하지만 [이전 포스팅](https://gruuuuu.github.io/ocp/ocp-restricted-network/)과 같이 폐쇄망에서 구성하게 되면 자동으로 OperatorHub를 구축해주지 않습니다.  

이번 포스팅에서는 폐쇄망에서 Openshift클러스터를 구성했을 시, OperatorHub를 구축하는 방법을 기술하겠습니다.  

**참고** : 
- openshift4.3 document - [Using Operator Lifecycle Manager on restricted networks](https://docs.openshift.com/container-platform/4.3/operators/olm-restricted-networks.html)  
- openshift4.7 document - [Using Operator Lifecycle Manager on restricted networks](https://docs.openshift.com/container-platform/4.7/operators/admin/olm-restricted-networks.html)


## Prerequisites
이전 포스팅([v4.3](https://gruuuuu.github.io/ocp/ocp-restricted-network/), [v4.7](https://gruuuuu.github.io/ocp/ocp4.7-restricted/))을 기반으로 설명할 것이니, 이쪽 게시글을 참고하면서 봐주시면 될 것 같습니다.  

간단히 현재 클러스터 구조를 나타내면 다음과 같습니다.   
![2](https://user-images.githubusercontent.com/15958325/95017685-c8947b80-0695-11eb-86d3-a5daa04c577b.PNG)   

온라인과 다르게 오프라인에서는 OperatorHub에서 다양한 카탈로그이미지들을 가지고 있어야 하므로 미러할 이미지 레지스트리가 클러스터 외부에 있어야 합니다.   
해당 실습에서는 클러스터를 생성할때 사용했던 이미지 레지스트리(Infra1)를 그대로 사용하도록 하겠습니다.  

-> [podman registry구축하기](https://gruuuuu.github.io/ocp/ocp-restricted-network/#mirrorregistry)  


## Building an Operator catalog image
카탈로그 이미지들을 quay등에서 받아 로컬 레지스트리에 추가해주겠습니다.  

> **권장사항)**  
>ocp 4.7라면 `podman` v1.9.3+, [`grpcurl`](https://github.com/fullstorydev/grpcurl), `opm` v1.12.3+ 

### 1. podman credential
podman registry의 credential정보가 있는 파일 경로를 환경설정으로 추가해줍니다.  
~~~sh
$ REG_CREDS=${XDG_RUNTIME_DIR}/containers/auth.json
~~~

`XDG_RUNTIME_DIR`을 출력해보면 다음과 같은 경로를 가지고 있습니다.  
~~~sh
$ echo $XDG_RUNTIME_DIR
/run/user/0
~~~

그리고 auth.json에는 레지스트리 호스트와 인증정보가 들어있습니다.  
~~~sh
$ cat $REG_CREDS
{
        "auths": {
                "registry.test.hololy.net:5000": {
                        "auth": "YWRtaW46cGFzc3cwcmQ="
                }
        }
}
~~~

### 2. auth token생성(Optional)
만약에 private quay registry를 사용하여 미러링을 할거라면 Quay authentication 토큰을 생성해두어야 합니다.  


jq설치
~~~sh
$ yum install -y jq
~~~

~~~sh
$ AUTH_TOKEN=$(curl -sH "Content-Type: application/json" \
    -XPOST https://quay.io/cnr/api/v1/users/login -d '
    {
        "user": {
            "username": "'"{quay_id}"'",
            "password": "'"{quay_pwd}"'"
        }
    }' | jq -r '.token')
~~~

### 3. podman login
**로컬 레지스트리**와 `registry.redhat.io` 모두 podman으로 로그인을 해둬야 합니다.  

~~~sh
$ podman login -u admin -p passw0rd registry.test.hololy.net:5000
Login Succeeded!
~~~

`registry.redhat.io`에 로그인할때는 레드햇 계정을 사용하도록 합니다.  
~~~sh
$  podman login -u '{redhat_id}' -p '{redhat_pwd}' registry.redhat.io
Login Succeeded!
~~~
>[registry.redhat.io](https://registry.redhat.io/)로 접속해보면 사용할 수 있는 카탈로그들을 볼 수 있습니다.  
>![image](https://user-images.githubusercontent.com/15958325/125875778-2ee90da7-c285-45e2-8256-f47f498d0fa5.png)  


### 4. [Optional] Pruning Catalog Images
RH에서 제공하는 카탈로그 이미지가 꽤 많기 때문에 필요한 이미지만 미러링하고 싶을 수 있습니다.  
크게 두가지 방법이 있습니다.  

#### 4.1 opm index prune
`opm`은 소프트웨어 저장소와 유사한 index라고 하는 번들 목록에서 카탈로그를 만들고 유지 및 관리할 수 있는 커맨드입니다.  
Index 이미지에는 카탈로그의 컨테이너화된 스냅샷(containerized snapshot of a catalog)이 들어있으며 Operator의 manifest를 포함하고 있습니다.  

Openshift 4.6 부터 Image Registry 카탈로그를 인덱스 이미지로 제공하고 있어 전체 카탈로그의 subset을 mirror하려면 `opm`커맨들을 사용하여 수정하여야 합니다.  

미러할 index이미지를 컨테이너로 띄웁니다.  
~~~sh
$ podman run -p50051:50051 -it registry.redhat.io/redhat/redhat-operator-index:v4.7

WARN[0000] unable to set termination log path            error="open /dev/termination-log: permission denied"
INFO[0000] Keeping server open for infinite seconds      database=/database/index.db port=50051
INFO[0000] serving registry                              database=/database/index.db port=50051
~~~

다른 터미널 하나를 띄워서 `grpcurl` 커맨드로 컨테이너에 포함된 패키지 리스트를 가져옵니다.  
~~~sh
$ grpcurl -plaintext localhost:50051 api.Registry/ListPackages > packages.out
~~~

packages.out에는 다음과 같이 패키지 리스트가 json형식으로 포함되어 있습니다.  
~~~json
{
  "name": "3scale-operator"
}
{
  "name": "advanced-cluster-management"
}
{
  "name": "amq-broker"
}
{
  "name": "amq-broker-lts"
}
{
  "name": "amq-broker-rhel8"
}
{
  "name": "amq-online"
}
{
  "name": "amq-streams"
}
{
  "name": "amq7-interconnect-operator"
}
{
  "name": "ansible-automation-platform-operator"
}
{
...
~~~

여기서 필요한 이미지만 골라서 `opm index prune`의 `-p` 파라미터의 인자로 넣어주면 됩니다.  
~~~sh
$ opm index prune \
    -f registry.redhat.io/redhat/redhat-operator-index:v4.7 \
    -p serverless-operator,openshift-pipelines-operator-rh,codeready-workspaces \
    [-i registry.redhat.io/openshift4/ose-operator-registry:v4.7] \
    -t <target_registry>:<port>/<namespace>/redhat-operator-index:v4.7
~~~
- `-f` : 원본 이미지
- `-p` : 필요한 이미지
- `-i` : Operator Registry base image (only for IBM Power & Z)
- `-t` : 필요한이미지만 뽑은 이미지 태그(ex. `registry.test.hololy.net:5000/namespace/red~:v4.7`)

실행 후 아래와 같이 이미지가 생긴 것을 확인 가능:  
~~~sh
$ podman images
REPOSITORY                                           TAG     IMAGE ID      CREATED             SIZE
registry.test.hololy.net:5000/test/redhat-operator-index  v4.7    7c5c915cbdd0  About a minute ago  112 MB
~~~

local registry에 push
~~~sh
$ podman push registry.test.hololy.net:5000/test/redhat-operator-index:v4.7
Getting image source signatures
Copying blob 88d2b1b8a4ca done
Copying blob 094d78802b07 done
Copying blob 1899390adebc done
Copying blob 55dfd992c4eb done
Copying blob 72e830a4dff5 done
Copying blob 06888ef1f8b7 done
Copying config 7c5c915cbd done
Writing manifest to image destination
Storing signatures
~~~


#### 4.2 oc adm catalog mirror (Advanced)
위의 `opm index prune`은 image index의 번들로만 관리할 수 있지 더 세부적인 사항(버전 등)은 관리할 수 없습니다.  
더 세부적으로 관리하고 싶다면 `oc adm catalog mirror`의 `--manifests-only` 옵션을 통해 index파일의 manifest파일을 받아 관리할 수 있습니다.  

~~~sh
$ oc adm catalog mirror \
    <index_image> \
    <registry_host_name>:<port> \
    [-a ${REG_CREDS}] \
    [--insecure] \
    [--filter-by-os="<os>/<arch>"] \
    --manifests-only 
~~~
`--manifests-only`옵션을 붙이고 실행하게 되면 mirror하지 않고 manifest파일만 생성한 뒤 마치게 됩니다.  
~~~sh
registry.redhat.io/container-native-virtualization/virt-cdi-uploadproxy@sha256:f16adea054c67f128d462a0e971cd3b420dc824bbe9af17718bd1825fc4dd0be=registry.test.hololy.net:5000/container-native-virtualization/virt-cdi-uploadproxy:8b077e25
registry.redhat.io/codeready-workspaces/plugin-java11-rhel8@sha256:641e223f5efbc32bab3461aa000e3a50a5dcca063331322158d1c959129ffd99=registry.test.hololy.net:5000/codeready-workspaces/plugin-java11-rhel8:2d365aad
registry.redhat.io/quay/quay-builder-rhel8@sha256:f85122b9e13c4f1b30fc5957d832c48adf0ee9f508ac8c9651e1533a201f5372=registry.test.hololy.net:5000/quay/quay-builder-rhel8:e58c0a76
registry.redhat.io/ocs4/ocs-must-gather-rhel8@sha256:1949179411885858ec719ab052868c734b98b49787498a8297f1a4ace0283eae=registry.test.hololy.net:5000/ocs4/ocs-must-gather-rhel8:7186dd14
registry.redhat.io/openshift-service-mesh/kiali-rhel7:1.0.8=registry.test.hololy.net:5000/openshift-service-mesh/kiali-rhel7:1.0.8
...
~~~
이렇게 미러할 소스이미지안에 어떠한 패키지가 버전별로 포함되어있는지 알 수 있고, 이를 수정하여 원하는 이미지 만을 미러할 수 있습니다.  

근데 저도 테스트는 안해봤기에 참고할 수 있는 링크를 첨부하도록 하겠습니다.  
->[Configuring OperatorHub for restricted networks](https://docs.openshift.com/container-platform/4.3/operators/olm-restricted-networks.html#olm-restricted-networks-operatorhub_olm-restricted-networks)  


## 2. Configuring OperatorHub for restricted networks

### [OCP 4.5이하만!] oc adm catalog build
OCP 4.5 이하에서는 image catalog를 먼저 빌드해주어야 합니다.  

~~~sh
$ oc adm catalog build \
    --appregistry-org redhat-operators \
    --from=registry.redhat.io/openshift4/ose-operator-registry:v4.3 \
    --filter-by-os="linux/amd64" \
    --to=<registry_host_name>:<port>/olm/redhat-operators:v1 \
    [-a ${REG_CREDS}] \
    [--insecure] \
    [--auth-token "${AUTH_TOKEN}"] 
~~~
- `from` : `ose-operator-registry` 레포지토리에서 가져올 이미지들의 태그. 맨 뒤의 태그는 openshift의 버전을 의미(ex. `4.3`, `4.4`, `4.5`)  
- `filter-by-os` : 시스템의 아키텍처에 따라서 선택가능 (`linux/amd64`, `linux/ppc64le`, `linux/s390x` 중 1)  
- `to` : 이미지를 넣을 로컬 레지스트리와 이미지의 태그를 명시(ex. `v1`)  
- (Optional) `a` : 로컬 레지스트리의 credential file  
- (Optional) `insecure` : 타겟 레지스트리와 trust연결을 하고싶지 않을때 명시  
- (Optional) `auth-token` : from에 사용한 레지스트리가 퍼블릭이아닌 프라이빗일 경우 사용  

빌드는 빨리 끝납니다.  
다 되고나서 curl로 확인해보면 아래와 같이 레포지토리가 새로 생긴 것을 확인할 수 있습니다.    
~~~sh
$ curl -u admin:passw0rd -k https://registry.test.hololy.net:5000/v2/_catalog
{"repositories":["ocp4.3.8-x86","olm/redhat-operators"]}
~~~

>**끌어올 catalog 정보** -> [registry.redhat.io/openshift4/ose-operator-registry](https://catalog.redhat.com/software/containers/search?q=openshift4%2Fose-operator-registry&p=1&architecture=amd64)
>![image](https://user-images.githubusercontent.com/15958325/125880078-8ec47958-2da0-40f1-9e91-bcbace1ab076.png)  

### 2.1 disable default operator source
설치할때 생긴 default source를 disable 시켜줍니다.  
~~~sh
$ oc patch OperatorHub cluster --type json \
    -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
~~~

### 2.2 catalog mirror
이제 로컬레지스트리로 이미지들을 미러링을 해야합니다.  

>**주의!**  
>이 과정은 여유 용량이 대략 460G는 있어야 합니다. 생각보다 많은 용량을 잡아먹기 때문에 사전에 루트폴더가 충분한 용량을 가지고 있는지 살펴보아야 합니다.  
>만약 460G보다 적은 유휴용량을 지니고 있다면 아래 링크를 통해서 root폴더 용량을 늘려주세요.  
>참고링크 : [[CentOS] LVM /home 용량을 줄이고 / 용량을 늘리기](https://knoow.tistory.com/179)

~~~sh
$ oc adm catalog mirror \
    <index_image> \
    <registry_host_name>:<port> \
    [-a ${REG_CREDS}] \
    [--insecure] \
    [--filter-by-os="<os>/<arch>"] \
    [--manifests-only]
~~~

각 파라미터는 위에서 설명한 것과 동일하고, `manifests-only`같은 경우, 명시하게 되면 미러할 이미지들의 manifest 파일을 얻게 됩니다.(원하는 이미지만 잘라낼 때 사용)

~~~sh
...
sha256:26eeac0dbd0370e022035ad1d7c561915067d7f5948208eecf5cfcd24e3dc0bf registry.test.hololy.net:5000/codeready-workspaces/stacks-cpp-rhel8:dec0995c
sha256:56543cfeeeac030821557ac4937db40f6845e874193c79c30267a680f9b2cbe7 registry.test.hololy.net:5000/codeready-workspaces/stacks-cpp-rhel8:5a87a277
sha256:bbd5dc16e3065a6b8cb7f8776176a84cd8f47049945f06fb62ad043ba73a87ca registry.test.hololy.net:5000/codeready-workspaces/stacks-cpp-rhel8:3e0842ed
sha256:bee42929090b7361c009aa6376d1272096b0a718ef13be72b2f52163403ba3ac registry.test.hololy.net:5000/codeready-workspaces/stacks-cpp-rhel8:7b9c099c
info: Mirroring completed in 3h33m59.1s (37.37MB/s)
~~~

>보이시나요 전체 미러하는데 3시간 반이 소요되었습니다.(v4.7기준)  
>용량도 무려 450GB나 잡아먹습니다!
>![image](https://user-images.githubusercontent.com/15958325/126107682-0fb3a242-a732-4c0d-b04a-d2dc1da5db0b.png)  



`oc adm catalog mirror` 커맨드가 끝나게되면 두가지 파일이 생깁니다.  
- `imageContentSourcePolicy.yaml` : 매니페스트파일에 담겨있는 이미지 레퍼런스들과 미러된 레지스트리간의 규칙을 정의
- `mapping.txt` : 레지스트리에 담긴 모든 이미지소스가 담겨있음. 미러링할때 여기담긴 리스트를 커스텀해서 원하는 구성을 적용가능

### 2.3 imageContentSourcePolicy & catalogSource
imageContentSourcePolicy와 catalogSource를 생성합니다.  

~~~sh
$ oc apply -f imageContentSourcePolicy.yaml
~~~

~~~sh
$ vim catalogsource.yaml

apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-operator-catalog
  namespace: openshift-marketplace
spec:
  sourceType: grpc
  image: registry.test.hololy.net:5000/olm/redhat-operators:v1
  displayName: My Operator Catalog
  publisher: grpc
~~~

~~~sh
$ oc create -f catalogsource.yaml
~~~

#### 5. 확인
허브가 제대로 올라갈때까지 시간이 꽤 많이 걸립니다.  
저같은경우 30분정도 걸렸고 그때까지 계속 `CrashLoopBackOff`에러가 뜨면서 pod이 죽었다 살아났다 했습니다.  
describe로 pod을 살펴보면 OOM이던데... 이 pod에게 충분히 메모리를 주는 방법은 아직 모르겠습니다.  

>중간에 제대로 된 로그도 볼 수가 없어서 진행이 되고 있는지 안되고 있는지 알수가없어서 pod을 내릴까말까 엄청 고민했었습니다ㅋㅋ 화나서 밥먹고 왔더니 멀쩡히 돌아가고있는 operatorhub...ㅎ

Pod확인:  
~~~sh
$ oc get pods -n openshift-marketplace
~~~
![image](https://user-images.githubusercontent.com/15958325/95081011-e88a7480-0753-11eb-8657-e57aa99b7551.png)

pakagemanifest 확인:  
~~~sh
$ oc get packagemanifest -n openshift-marketplace
~~~
![image](https://user-images.githubusercontent.com/15958325/126107877-0186fd79-a8fc-4770-9488-447e2bfee98d.png)  


웹 콘솔로 확인해보면 아래와 같이 사용할 수 있는 오퍼레이터가 생긴 것을 보실 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/126107911-d641b586-3ef6-4e2a-91b3-c27944b94cae.png)  


## 나올 수 있는 에러들
my catalog pod이 정상적으로 뜨지 않고 아래와 비슷한 에러인 경우:  
![image](https://user-images.githubusercontent.com/15958325/95082021-6733e180-0755-11eb-9575-66f743734485.png)  

클러스터 설치를 마무리하고 image registry설정을 안해줘서 그렇습니다.  
아래와 같이 `managementState`를 `Managed`로 바꾸고 `storage`를 `pvc`나 `emptyDir`로 설정해주시면 됩니다.  
~~~sh
$ oc edit configs.imageregistry.operator.openshift.io
~~~
![image](https://user-images.githubusercontent.com/15958325/95082143-921e3580-0755-11eb-9ff8-9e894c011563.png)  


----
