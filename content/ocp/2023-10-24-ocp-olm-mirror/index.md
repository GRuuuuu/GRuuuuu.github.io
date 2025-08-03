---
title: "OperatorHub를 위한 Custom Catalog만들기 (feat. Restricted Network)"
slug: ocp-olm-mirror
tags:
  - Kubernetes
  - Openshift
date: 2023-10-24T13:00:00+09:00
---

## Overview
대략 2년전 비슷한 내용으로 포스팅을 한 적이 있었는데, 내용에 변경이 있어서 업데이트된 내용으로 다시 작성하고자 합니다.  

옛날 글 -> [Openshift4 OperatorHub 구성](https://gruuuuu.github.io/ocp/operatorhub/)  

OperatorHub는 쉽게 말해 사용자들이 편하게 app을 배포&관리할 수 있도록 패키징해둔 App(Operator)들의 집합입니다.  

원래는 RedHat에서 기본적으로 제공하는 Operator들과 Community버전의 Operator들이 제공되지만, 폐쇄망설치를 하게되면 외부 레지스트리에서 이미지들을 따로 끌고오지 못하기 때문에 구성이 안되죠.  
또 기존의 카탈로그외에 새로운 Operator들을 사용하고싶을때도 있을겁니다.  

이번 포스팅에서는 **OperatorHub를 위한 Custom Catalog제작과 폐쇄망에서의 이미지 미러링**에 대해서 알아보도록 하겠습니다.  

>**수정)**  
>231118) `oc-mirror`로 mirror하는 방법 추가

## 1. Managing Custom Catalog
>참고 : [Managing custom catalogs](https://docs.openshift.com/container-platform/4.13/operators/admin/olm-managing-custom-catalogs.html)  

우선 4.11부터 바뀐 가장 큰 변경점!  

4.6~4.10버전까지는 **SQLite database format**으로 카탈로그를 릴리즈했었는데 4.11부터는 **file-based format**으로 바뀌었습니다.  
따라서 기존 4.6~4.10까지는 `opm` 커맨드를 사용하여 prunning등을 하였는데 앞으로는 file-based포맷으로 바뀜에 따라 `opm`의 `SQLite`용 subcommand들은 deprecated될 것 이라고 합니다.  

>**file-based format의 catalog특징**  
> - plain text-based임(JSON or YAML)
> - 쉬운 편집 가능(기존엔 버전별 이미지 선택이나 이미지 프루닝이 쉽지 않았음... opm사용)
> - 이미지 보기도 쉬워짐 (jq로 pretty하게 볼수있음)
> - 카탈로그끼리 합치기도 가능  

4.10이하의 카탈로그 구성에 대해서는 옛날 글을 참고 -> [Openshift4 OperatorHub 구성](https://gruuuuu.github.io/ocp/operatorhub/)  

### 1.1 file-based catlalog image 생성하기

>**Requirements :**  
>`opm` -> [Installing the opm CLI](https://docs.openshift.com/container-platform/4.13/cli_reference/opm/cli-opm-install.html#cli-opm-install)  
>`podman` v1.9.3+  
>local registry : supports Docker v2-2( https://docs.docker.com/registry/)   

catalog만들기 위한 폴더 생성
~~~
$ mkdir test-catalog
~~~

catalog 이미지빌드를위한 도커파일생성  
기본적으로는 `quay.io/operator-framework/opm:latest`가 사용되는데, 카탈로그에 RedHat 공식 image를 넣으려면 `ose-operator-registry`를 사용을 권장합니다.  
~~~
$ opm generate dockerfile <catalog_dir> -i registry.redhat.io/openshift4/ose-operator-registry:v4.13 
~~~

그러면 이렇게 Dockerfile이 생성됩니다  
~~~
$ ls
<catalog_dir>  <catalog_dir>.Dockerfile
~~~

custom catalog용 description과 icon 생성  
~~~
$ vim README.md
~~~

샘플용 operator 아이콘이미지 다운로드  
-> https://www.svgrepo.com/   


catalog configuration용 `index.yaml`파일 생성
~~~
$ opm init <operator_name> --default-channel=preview --description=./README.md --icon=./operator-icon.svg --output yaml > <catalog_dir>/index.yaml 
~~~
`default-channel`은 operator설치할때 기본적으로 설정되는 채널의 이름, 뒤의 index.yaml에서 사용되니 기억해둬야 합니다.  

### 1.2. bundle 이미지 추가하기

이제 기본으로 사용할 index이미지에 대한 설정이 끝났으니, 여기에 추가할 Operator들을 넣어줘야합니다.  

>RedHat Ecosystem Catalog -> https://catalog.redhat.com/  

저는 여기에 minio라는 object storage operator를 추가해보도록 하겠습니다.  

주의해야할 점은 "bundle"이미지를 사용해야한다는 점입니다!(kubernetes manifests와 metadata들이 담겨져있음)  

`opm render`를 통해 index.yaml에 bundle이미지의 상세를 추가해줍니다.  
~~~
$ opm render <registry>/<namespace>/<bundle_image_name>:<tag> --output=yaml >> <catalog_dir>/index.yaml
~~~

실행하고나면 아래와 같이 추가가 됩니다.  
~~~
----
image: registry.connect.redhat.com/minio/minio-operator1-marketplace@sha256:3ee1d6a9a4cc3d743c839eed82a92bf935fbc9cdf9c23af5515b4c97f5f3dcb8
name: minio-operator-rhmp.v5.0.10
package: minio-operator-rhmp
properties:
- type: olm.gvk
....
~~~

다음으로는 이 operator의 channel정보도 추가해주도록 합니다. (`opm init`할때 넣었던 default channel 이름이 빠지면 안됨)  
~~~
---
schema: olm.channel
package: <operator_name>
name: preview
entries:
  - name: <operator_name>.v0.1.0
~~~

그다음 카탈로그 폴더가 제대로 구성되었는지 확인해봅니다.  
~~~
$ opm validate <catalog_dir> 
~~~
아무 출력값이 없어야 성공!

>**Troubleshooting**  
>error1)    
>~~~
>$ opm validate <catalog_dir>
>
>FATA[0000] unknown package "minio-operator" for bundle "minio-operator.v5.0.10"
>~~~
>
>-> opm init할때 넣었던 operatorname 즉 olm.package의 name이 package이름과 일치해야함
>
>
>error2)  
>~~~
>$ opm validate <catalog_dir>
>
>FATA[0000] package "example-operator", bundle "example-operator.v0.1.0" not found in any channel entries
>~~~
>bundle만 추가하고 channel을 추가하지 않아서 발생하는 에러 (name은 꼭 .v버전을 명시할것)

최종 형태는 아래와 같은 형태가 됩니다.  
예시)  
~~~
---
defaultChannel: preview
description: |
  test operator!!!!
icon:
  base64data: PD94bWwg...
  mediatype: image/svg+xml
name: minio-operator
schema: olm.package
---
entries:
  - name: minio-operator.v5.0.10
name: preview
package: minio-operator
schema: olm.channel
---
image: registry.connect.redhat.com/minio/minio-operator1:latest
name: minio-operator.v5.0.10
package: minio-operator
properties:
- type: olm.gvk
  value:
    group: minio.min.io
    kind: Tenant
    version: v2
- type: olm.gvk
  value:
    group: sts.min.io
    kind: PolicyBinding
    version: v1alpha1
- type: olm.package
  value:
    packageName: minio-operator
    version: 5.0.10
- type: olm.bundle.object
  value:
    data: eyJh...
...
relatedImages:
- image: quay.io/minio/minio@sha256:7e697b900f60d68e9edd2e8fc0dccd158e98938d924298612c5bbd294f2a1e65
  name: minio-7e697b900f60d68e9edd2e8fc0dccd158e98938d924298612c5bbd294f2a1e65-annotation
- image: quay.io/minio/operator@sha256:58c5114003fdc38877db2dc6ca45bc4b16572cc3e40c2fcc20702c5ccaa01caa
  name: console
- image: quay.io/minio/operator@sha256:58c5114003fdc38877db2dc6ca45bc4b16572cc3e40c2fcc20702c5ccaa01caa
  name: minio-operator
- image: registry.connect.redhat.com/minio/minio-operator1:latest
  name: ""
schema: olm.bundle
~~~

`index.yaml`이 완성되었다면 카탈로그 이미지를 빌드해주도록 하겠습니다.  
~~~
$ podman build . -f <catalog_dir>.Dockerfile -t <registry>/<namespace>/<catalog_image_name>:<tag>
~~~

빌드된 이미지를 registry에 push해줍니다.  
~~~
$ podman login <registry>
Login Succeeded!

$ podman push <registry>/<namespace>/<catalog_image_name>:<tag>
~~~

### 1.3 CatalogSource 만들기
이제 OpenShift의 OperatorHub에서 위에서 만든 custom catalog를 인식할 수 있도록 catalog source를 만들어주도록 하겠습니다.  

우선 private registry를 사용해서 image pulling을 하는데 secret이 필요하다면 아래와 같이 생성해줍니다.  
~~~
oc create secret docker-registry <secret-name> \
  -n openshift-marketplace \
  --docker-server=<registry> --docker-username=<id> \
  --docker-password=<password> --docker-email=<email>
~~~

그 다음 Catalog Source를 만들어줍니다.  
~~~yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-operator-catalog
  namespace: openshift-marketplace 
spec:
  sourceType: grpc
  secrets:
  - "<secret-name>"
  grpcPodConfig:
    securityContextConfig: restricted 
  image: <registry>/<namespace>/<catalog_image_name>:<tag> 
  displayName: My Operator Catalog
  publisher: <publisher-name> 
  updateStrategy:
    registryPoll: 
      interval: 30m
~~~

클러스터에 배포해주면 :  
~~~
# oc apply -f catalogSourcetest.yaml
catalogsource.operators.coreos.com/my-operator-catalog created
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-24-ocp-olm-mirror.md/1.png)  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-24-ocp-olm-mirror.md/2.png)

위와 같이 클러스터에서 custom catalog의 operator들을 사용할 수 있게 됩니다!  

## 2. 폐쇄망을 위한 Operator mirroring  

>참고 : [Mirroring images for a disconnected installation](https://docs.openshift.com/container-platform/4.13/installing/disconnected_install/installing-mirroring-installation-images.html)  

폐쇄망에서의 설치는 아시다시피 까다롭습니다.  
이미지를 다 준비해야 내부에서 사용할 수 있죠. 그래서 oc command는 쉽게 mirroring할 수 있게 기능들을 제공하고 있습니다.  

registry to registry로 mirror하는 방법은 옛날 글을 참조 -> [호롤리/Configuring OperatorHub for restricted networksPermalink](https://gruuuuu.github.io/ocp/operatorhub/#2-configuring-operatorhub-for-restricted-networks)  

이 포스팅에서는 registry에서 로컬에 file로 mirror하는 두가지 방법을 알아보도록 하겠습니다!  

### 2.1 oc adm catalog mirror로 미러하기

요 방법은 위에서 작업했던 custom index image가 반드시 필요합니다.  
혹은 전체 index이미지를 다운받기 위해 redhat 공식 index이미지들을 사용하여도 괜찮습니다.  
>Openshift에서 기본으로 제공하는 catalog index image list:
>- `registry.redhat.io/redhat/redhat-operator-index:v4.12`
>- `registry.redhat.io/redhat/community-operator-index:v4.12`
>- `registry.redhat.io/redhat/certified-operator-index:v4.12`
>- `registry.redhat.io/redhat/redhat-marketplace-index:v4.12`

#### 2.1.1 mirroring registry to file

podman auth.json을 환경변수로 세팅
~~~
$ REG_CREDS=${XDG_RUNTIME_DIR}/containers/auth.json
~~~

현재 폴더로 미러링하기  
~~~
$ oc adm catalog mirror <index_image> file:///local/index -a ${REG_CREDS} <--insecure> --index-filter-by-os='<platform>/<arch>' 

...
info: Mirroring completed in 1m7.36s (15.58MB/s)
wrote mirroring manifests to manifests-test-operator-1697976637

To upload local images to a registry, run:

        oc adm catalog mirror file://local/index/test-catalog/test-operator:v0.1 REGISTRY/REPOSITORY
deleted dir /tmp/861189190
~~~

그러면 폴더 두개가 생깁니다  
~~~
$ ls -al
total 44
drwxr-xr-x. 5 gru  gru  4096 Oct 22 21:10 .
drwxr-xr-x. 9 root root 4096 Oct 20 15:50 ..
drwxr-xr-x. 2 gru  gru  4096 Oct 22 21:12 manifests-test-operator-1697976637
drwxr-xr-x. 3 gru  gru  4096 Oct 22 21:10 v2
~~~

v2를 usb에 복사하고 요걸 폐쇄망 시스템에 복사해둡니다.  

#### 2.1.2 mirroring file to local registry
그리고 이걸 폐쇄망의 로컬 레지스트리에 밀어넣어야 합니다.  
아래 커맨드는 v2폴더의 부모 폴더에서 실행하시면 됩니다.    
~~~
$ oc adm catalog mirror file://local/index/<repository>/<index_image>:<tag> <mirror_registry>:<port>[/<repository>] -a ${REG_CREDS} --insecure --index-filter-by-os='<platform>/<arch>' 
~~~

제대로 들어갔는지 확인  
~~~
$ curl -u <id>:<password> <registry>/v2/_catalog     {"repositories":["restricted/local-index-test-catalog-test-operator","restricted/minio-minio","restricted/minio-minio-operator1","restricted/minio-operator","test-catalog/test-operator"]}
~~~

#### 2.1.3 `catalogSource`와 `imageContentSourcePolicy` 배포

이제 필요한 이미지들이 전부 local registry로 push되었으니 `catalogSource`와 `imageContentSourcePolicy`(Quay나 dockerHub같은 외부 레지스트리가 아닌 local registry에서 pull하기 위한 policy정의파일) 을 만들어서 배포해야 합니다.  

위에서 사용했던 `oc adm catalog mirror`를 다시 사용해서 manifests파일들을 생성해주도록 합니다.  
~~~
$ oc adm catalog mirror <mirror_registry>:<port>/<index_image> <mirror_registry>:<port>[/<repository>] --manifests-only [-a ${REG_CREDS}] [--insecure]

src image has index label for declarative configs path: /configs/
using index path mapping: /configs/:/tmp/3025038578
wrote declarative configs to /tmp/3025038578
using declarative configs at: /tmp/3025038578
no digest mapping available for registry.connect.redhat.com/minio/minio-operator1:latest, skip writing to ImageContentSourcePolicy
no digest mapping available for <registry>/restricted/local-index-test-catalog-test-operator:v0.1, skip writing to ImageContentSourcePolicy
wrote mirroring manifests to manifests-local-index-test-catalog-test-operator-1698040027
deleted dir /tmp/3025038578
~~~

`--manifests-only`를 사용해서 다시 mirror하지 않고 manifests파일만 얻을 수 있습니다.  

생성된 manifest 폴더에 가보면 아래와 같이 두개의 파일이 생긴 것을 확인하실 수 있습니다.  
~~~
$ ls
catalogSource.yaml  imageContentSourcePolicy.yaml  mapping.txt
~~~

위에서 custom catalog배포했을 때처럼 registry pull에 secret이 필요하다면 catalogSource에 `secrets`블럭을 추가해주고 배포해줍니다.  

~~~
# oc get pod
NAME                                           READY   STATUS    RESTARTS   AGE
local-index-test-catalog-test-operator-z8t5c   1/1     Running   0          81s
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-10-24-ocp-olm-mirror.md/3.png)

### 2.2 oc mirror로 미러하기
위의 방법은 일부 이미지만 따로 빼서 파일로 떨구기 여러모로 귀찮은 점이 있습니다.  
index 이미지의 전체가 아닌 일부 이미지만 미러하려면 따로 커스텀 카탈로그 이미지를 만들어야 하기 때문입니다(1번참고).

#### 2.2.1 `oc-mirror` 설치
더 편하게 mirror를 할 수 있게, `oc-mirror`라는 플러그인을 따로 제공합니다.  
-> [download](https://console.redhat.com/openshift/downloads)  

**Openshift disconnected installation tools**섹션에 oc mirror plugin을 다운받고, 압축을 해제한 뒤에 `oc-mirror`를 `$PATH`중 어딘가에 옮겨두면 됩니다.  

`oc mirror help`로 제대로 설치가 되었는지 확인하면 끝  

#### 2.2.2 ImageSetConfiguration 작성하기
그런 다음 index이미지에서 어떤 이미지들을 가져올건지 정의하는 `ImageSetConfiguration`을 작성해줍니다.  

>(참고) Openshift에서 기본으로 제공하는 catalog index image list:
>- `registry.redhat.io/redhat/redhat-operator-index:v4.12`
>- `registry.redhat.io/redhat/community-operator-index:v4.12`
>- `registry.redhat.io/redhat/certified-operator-index:v4.12`
>- `registry.redhat.io/redhat/redhat-marketplace-index:v4.12`

index이미지에 어떤 이미지들이 있는지 확인하려면 :  
~~~
$ oc mirror list operators --catalog=registry.redhat.io/redhat/community-operator-index:v4.12
~~~

어떤 index이미지를 사용할건지, 어떤 operator이미지들을 가져올건지 정했다면 아래와 같이 `ImageSetConfiguration`을 작성해줍니다.  
~~~yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v1alpha2
archiveSize: 4                                                      
storageConfig:                                                      
  #local registry에 바로 mirror하려면
  #registry:
  #  imageURL: example.com/mirror/oc-mirror-metadata                 
  #  skipTLS: false
  #file로떨구려면
  local:
    path: /local/path
mirror:
  platform:
    channels:
    - name: stable-4.12                                             
      type: ocp
    graph: true                                                     
  operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14  
    packages:
    - name: serverless-operator                                     
      channels:
      - name: stable                                                
  additionalImages:
  - name: registry.redhat.io/ubi9/ubi:latest                        
  helm: {}
~~~

local registry로 mirror하는 경우:  
~~~
$ oc mirror --config=./imageset-config.yaml docker://registry.example:5000    
~~~

파일로 mirror하는 경우:  
~~~
$oc mirror --config=./imageset-config.yaml file://<path_to_output_directory> 
~~~

이렇게 local registry에 원하는 operator 이미지만 mirror하거나, 파일로 떨굴 수 있습니다.  

mirror하고 나면 output파일들에 대한 폴더가 생성되고 그 안에는 tar파일이 생깁니다.  
이걸 usb같은 저장장치에 담아서 폐쇄망에 꽂고 local registry에 load하면 됩니다.  

같은 폴더에 있는 `oc-mirror-workspace`에는 `ImageContentSourcePolicy` 와 `CatalogSource` Yaml파일이 있고, 이녀석들을 클러스터에 배포해주면 완료입니다!  

끝!

----