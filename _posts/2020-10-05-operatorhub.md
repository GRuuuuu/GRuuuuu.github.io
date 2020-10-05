---
title: "Openshift4 OperatorHub 구성"
categories: 
  - OCP
tags:
  - Kubernetes
  - RHCOS
  - Openshift
last_modified_at: 2020-10-05T13:00:00+09:00
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

**참고 : openshift document - [Using Operator Lifecycle Manager on restricted networks](https://docs.openshift.com/container-platform/4.3/operators/olm-restricted-networks.html)**  

## Prerequisites
[이전 포스팅](https://gruuuuu.github.io/ocp/ocp-restricted-network/)을 기반으로 설명할 것이니, 이쪽 게시글을 참고하면서 봐주시면 될 것 같습니다.  

간단히 현재 클러스터 구조를 나타내면 다음과 같습니다.   
![2](https://user-images.githubusercontent.com/15958325/95017685-c8947b80-0695-11eb-86d3-a5daa04c577b.PNG)   

온라인과 다르게 오프라인에서는 OperatorHub에서 다양한 카탈로그이미지들을 가지고 있어야 하므로 미러할 이미지 레지스트리가 클러스터 외부에 있어야 합니다.   
해당 실습에서는 클러스터를 생성할때 사용했던 이미지 레지스트리(Infra1)를 그대로 사용하도록 하겠습니다.  

-> [podman registry구축하기](https://gruuuuu.github.io/ocp/ocp-restricted-network/#mirrorregistry)  


## 1. Building an Operator catalog image
카탈로그 이미지들을 quay등에서 받아 로컬 레지스트리에 추가해주겠습니다.  

### Steps
#### 1. podman credential
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
                "registry.gru.hololy-dev.com:5000": {
                        "auth": "YWRtaW46cGFzc3cwcmQ="
                }
        }
}
~~~

#### 2. auth token생성(Optional)
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

#### 3. podman login
로컬 레지스트리와 `registry.redhat.io` 모두 podman으로 로그인을 해둬야 합니다.  

~~~sh
$ podman login -u admin -p passw0rd registry.gru.hololy-dev.com:5000
Login Succeeded!
~~~

`registry.redhat.io`에 로그인할때는 레드햇 계정을 사용하도록 합니다.  
~~~sh
$  podman login -u '{redhat_id}' -p '{redhat_pwd}' registry.redhat.io
Login Succeeded!
~~~

#### 4. catalog build
이제 카탈로그들을 빌드해줍니다.  
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
$ curl -u admin:passw0rd -k https://registry.gru.hololy-dev.com:5000/v2/_catalog
{"repositories":["ocp4.3.8-x86","olm/redhat-operators"]}
~~~

## 2. Configuring OperatorHub for restricted networks

### Steps
#### 1. disable default operator source
설치할때 생긴 default source를 disable 시켜줍니다.  
~~~sh
$ oc patch OperatorHub cluster --type json \
    -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
~~~

#### 2. catalog mirror
이제 로컬레지스트리로 이미지들을 미러링을 해야합니다.  

>**주의!**  
>이 과정은 여유 용량이 대략 80G는 있어야 합니다. 생각보다 많은 용량을 잡아먹기 때문에 사전에 루트폴더가 충분한 용량을 가지고 있는지 살펴보아야 합니다.  
>만약 80G보다 적은 유휴용량을 지니고 있다면 아래 링크를 통해서 root폴더 용량을 늘려주세요.  
>참고링크 : [[CentOS] LVM /home 용량을 줄이고 / 용량을 늘리기](https://knoow.tistory.com/179)

미러를 뜰때는 두가지 방법을 사용해서 미러를 할 수 있습니다.  
1. 모든 이미지들을 미러
2. 미러링에 필요한 manifest파일을 출력, 이후 원하는 이미지만 manifest파일에서 골라서 미러링을 할 수 있다

~~~sh
$ oc adm catalog mirror \
    <registry_host_name>:<port>/olm/redhat-operators:v1 \
    <registry_host_name>:<port> \
    [-a ${REG_CREDS}] \
    [--insecure] \
    [--filter-by-os="<os>/<arch>"] \
    [--manifests-only] 
~~~

각 파라미터는 위에서 설명한 것과 동일하고, `manifests-only`같은 경우, 명시하게 되면 위의 두가지 미러링 방법중 2번방법으로 진행하게 하는 옵션입니다.  

>(2020.10.05)시간이 없어서 manifests-only는 제대로 테스트하지 못했습니다. 추후에 수정예정

저는 manifests-only옵션을 사용하지 않고 바로 전체 이미지를 미러링하였는데 시간이 거의 7시간가까이 걸렸습니다.

~~~sh
...
info: Planning completed in 1.23s
uploading: registry.gru.hololy-dev.com:5000/container-native-virtualization/virt-cdi-cloner sha256:41ae95b593e0eabd584b11216673daee2d1d5e28e3dd8598beb763b76e24c35f 51.89MiB
uploading: registry.gru.hololy-dev.com:5000/container-native-virtualization/virt-cdi-cloner sha256:ba8d0d463156b9bea87fb7e67c11594870044d1b3c88162aca5d9826e2b2e79b 82.53MiB
sha256:e1c7f258d39c85bde00c72e0f18b1663103e51237c8cc2627b2bc300b1823934 registry.gru.hololy-dev.com:5000/container-native-virtualization/virt-cdi-cloner
sha256:33ea406a226d34a4a7920957a45c296b1d68df0faf74b8f698ec78a39caff395 registry.gru.hololy-dev.com:5000/container-native-virtualization/virt-cdi-cloner
info: Mirroring completed in 3.89s (36.14MB/s)
W0929 03:53:33.605621    1441 mirror.go:258] errors during mirroring. the full contents of the catalog may not have been mirrored: couldn't parse image for mirroring (), skipping mirror: invalid reference fort
I0929 03:53:33.835391    1441 mirror.go:329] wrote mirroring manifests to redhat-operators-manifests
~~~
>출력된 로그를 보시면 전체 이미지를 제대로 미러링하지 못했다고 뜹니다.  
>이때의 원인은 참조하는 DB(eg. /tmp/132891387/bundles.db)의 각 operator값이 name:xx image:xx로 되어있어야 하는데 에러나는 operator들은 name:xx value:xx로 되어있습니다.  
>
>이부분은 아직 제대로 해결하지 못했으므로 추후에 다시 기술하겠습니다.  

몇가지 이미지가 제대로 parsing되지 않아서 미러링되지 않았지만 일단 일부 이미지라도 미러링에 성공하였습니다.  

두가지 방법 모두, `catalog mirror` 커맨드가 끝나게되면 두가지 파일이 생깁니다.  
- `imageContentSourcePolicy.yaml` : 매니페스트파일에 담겨있는 이미지 레퍼런스들과 미러된 레지스트리간의 규칙을 정의
- `mapping.txt` : 레지스트리에 담긴 모든 이미지소스가 담겨있음. 미러링할때 여기담긴 리스트를 커스텀해서 원하는 구성을 적용가능

#### 4. imageContentSourcePolicy & catalogSource
imageContentSourcePolicy와 catalogSource를 생성합니다.  

~~~sh
$ oc apply -f ./redhat-operators-manifests/imageContentSourcePolicy.yaml
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
  image: registry.gru.hololy-dev.com:5000/olm/redhat-operators:v1
  displayName: My Operator Catalog
  publisher: grpc
~~~

~~~sh
$ oc create -f catalogsource.yaml
~~~

### 5. 확인
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
![image](https://user-images.githubusercontent.com/15958325/95081174-212a4e00-0754-11eb-9b84-db5e4a44b466.png)  

웹 콘솔로 확인해보면 아래와 같이 사용할 수 있는 오퍼레이터가 생긴 것을 보실 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/95081192-28e9f280-0754-11eb-94a6-47047f3ee2b7.png)

비록 현재는 모든 오퍼레이터들을 정상적으로 받지 못하였지만 추후에 parsing문제들을 해결하고 나면 포스팅을 수정하도록 하겠습니다.  



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
