---
title: "OVN-kubernetes network migration"
categories:
  - OCP
tags:
  - Kubernetes
  - Openshift
last_modified_at: 2024-08-01T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview
오랜만에 작성하는 openshift관련 포스팅입니다.  
최근 관리하는 클러스터(4.15)를 4.16으로 업그레이드 할 일이 생겨서 작업 중 아래와 같은 에러를 만났습니다.  
~~~
Cluster operator network should not be upgraded between minor versions: OpenShiftSDNConfigured: Cluster is configured with OpenShiftSDN, which is not supported in the next version. Please follow the documented steps to migrate from OpenShiftSDN to OVN-Kubernetes in order to be able to upgrade.
~~~

~~하여튼한번에잘되는법이없음~~

무슨일인고 하니 바로 4.14버전부터 `OpenshiftSDN`이 deprecated되어 4.16부터는 사용불가가 되어버린것...  
따라서 Openshift 네트워크 세팅을 `OVN-Kubernetes`로 마이그레이션 해줘야 업그레이드가 가능합니다.  

이번 포스팅에서는 마이그레이션 방법과, 대체 이녀석들이 뭐하는 녀석들인지 간단히 알아보도록 하겠습니다.  

## OpenshiftSDN vs OVN-Kubernetes

**OpenshiftSDN**
- Software-Defined networking(SDN)방식을 사용하여 OpenShift 컨테이너 플랫폼 클러스터에서 파드 간 통신을 가능하게 하는, 통합 클러스터 네트워크를 제공하는 **CNI plugin**
- OpenVSwitch(OVS)기반의 오버레이 네트워크를 구성
- ocp 4.14부터 deprecated되고 4.15 부터는 설치옵션에서 지원하지 않음

>**SDN** : 네트워크 트래픽을 기존의 네트워크 장치가 아닌 별도의 **소프트웨어에 의해 제어되는 네트워크**  
>**OVS** : 오픈소스 가상 스위치로, 물리 스위치와 연결되어 가상 네트워크의 스위칭 스택 및 네트워크 프로토콜을 제공

**OVN-Kubernetes Network**  
- OVN기반의 **CNI plugin**
- OVN(Open Virtual Network)
    - OVS는 하나의 스위치로서의 기능들을 제공하고있고 전체 네트워크 환경을 구성하려면 SDN protocol을 통해 관리해야함
    - 기존 OVS의 기능을 보완, 가상 네트워크 추상화를 제공(논리 스위치, router, security group, L2/L3/L4 ACL 등)
    - OVN이 OVS의 상위개념은 아니고 OVS의 데몬처럼 동작하게 된다
    - OVS와 같은 커뮤니티에서 개발되는 오픈소스
- kubernetes network policy지원
- `VXLAN`기반의 `OpenshiftSDN`과 다르게 `Geneve`(Generic Network Virtualization Encapsulation)프로토콜을 사용

둘 다 이름과 기능만 약간 다르다뿐이지 OVS기반으로 가상 네트워크의 추상화를 제공하는 SDN솔루션입니다.  

그럼 왜 RedHat에선 `OpenshiftSDN`대신 `OVN-Kubernetes`를 default SDN으로 선정한 것일까요?  

>reference : [OpenShiftSDN CNI removal in OCP 4.17](https://access.redhat.com/articles/7065170)  
>  
>**Why has Red Hat chosen to remove the openshift-sdn CNI?**  
>Since the release of OpenShift 4.1, all new SDN feature development has been focused on the ovn-kubernetes CNI plug-in, while the openshift-sdn CNI plug-in has been feature frozen. The focus on ovn-kubernetes development has resulted in a long and growing list of features and advantages of ovn-kubernetes over its predecessor, openshift-sdn

대충 요약하면 `OVN-Kubernetes`에 더 집중하겠다는 뜻입니다.   

>(뇌피셜) Openshift4 초기부터 ovn-kubernetes를 지원하고 있었지만 default network setting으로 쓰지 않았던 이유는 오픈소스였던 ovn이 충분히 성숙하지 않았을 수도 있고,    
>근데 지금은 ovn이 충분히 안정적이 되니 굳이 개발 인력을 openshift sdn으로 돌리지 않았을 수도 있고,  
>오픈소스인 ovn을 씀으로써 벤더락인을 줄이기 위해서일수도? 있지 않을까 생각해봅미다...

두 CNI plugin의 기능 비교표입니다.  
`OVN-Kubernetes`가 IPv6, IPsec, 데이터 처리 오프로딩 등 더 많은 기능을 지원하고 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-08-01-openshift-cni/1.png)  

>참고 : [About the OVN-Kubernetes network plugin](https://docs.openshift.com/container-platform/4.16/networking/ovn_kubernetes_network_provider/about-ovn-kubernetes.html)   


## OpenshiftSDN to OVN-Kubernetes
그럼 이제 OVN-Kubernetes로 마이그레이션 하는 방법에 대해서 알아보겠습니다.  

**본문에서는 가장 기본적인 마이그레이션 방법에 대해서만 서술하오니, 주의사항과 더 자세한 설명은 아래 공식문서 링크를 참고해주시기 바랍니다.**  

[Migrating from the OpenShift SDN network plugin](https://docs.openshift.com/container-platform/4.16/networking/ovn_kubernetes_network_provider/migrate-from-openshift-sdn.html)  

1. 네트워크 기존 설정 백업   

~~~
$ oc get Network.config.openshift.io cluster -o yaml > cluster-openshift-sdn.yaml

apiVersion: config.openshift.io/v1
kind: Network
metadata:
    creationTimestamp: "2023-09-22T05:37:59Z"
    generation: 2
    name: cluster
    resourceVersion: "10880"
    uid: 02803a48-aefe-4bfd-bd72-9190bbe9a98a
spec:
    clusterNetwork:
    - cidr: 10.254.0.0/16
    hostPrefix: 24
    externalIP:
    policy: {}
    networkType: OpenShiftSDN
    serviceNetwork:
    - 172.30.0.0/16
status:
    clusterNetwork:
    - cidr: 10.254.0.0/16
    hostPrefix: 24
    clusterNetworkMTU: 1450
    networkType: OpenShiftSDN
    serviceNetwork:
- 172.30.0.0/16
~~~

2. `Network.operator.openshift.io` CR의 migration필드를 `OVNKubernetes`로 변경    
~~~
$ oc patch Network.operator.openshift.io cluster --type='merge' --patch '{ "spec": { "migration": { "networkType": "OVNKubernetes" } } }'
network.operator.openshift.io/cluster patched
~~~

3. 노드들이 재시작 될 때까지 대기     

4. 아래 명령어로 configuration이 적용되었는지 확인     
~~~
$ oc describe node | egrep "hostname|machineconfig"
~~~

>일단 이 단계까지만 와도 pending되었던 cluster upgrade가 진행이 됩니다.  
>cluster upgrade 도중에 migration을 진행하고 있었다면 모든 작업이 종료된 이후에 마저 migration을 진행하는 것이 좋을 것 같습니다.     
>~~~
>$ oc describe node | egrep "hostname|Done"
>    kubernetes.io/hostname=master0.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=master1.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=master2.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker0.red01.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker1.red02.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker2.blue02.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker3.blue03.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker4.blue04.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker5.green01.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>    kubernetes.io/hostname=worker6.green04.wxai.garagekr.com
>    machineconfiguration.openshift.io/state: Done
>~~~

5. migration 스타트   
~~~
$ oc patch Network.config.openshift.io cluster --type='merge' --patch '{ "spec": { "networkType": "OVNKubernetes" } }'
network.config.openshift.io/cluster patched
~~~

6. 끝나면 모든 노드 리부트(수동)   

7. 확인    

~~~
$ oc get network.config/cluster -o jsonpath='{.status.networkType}{"\n"}'
OVNKubernetes

$oc get co ->에러없어야함
~~~

8. 뒷정리      

migration 끄기
~~~
$ oc patch Network.operator.openshift.io cluster --type='merge' --patch '{ "spec": { "migration": null } }'
network.operator.openshift.io/cluster patched
~~~

`SDNConfig`를 null로 바꾸기   
~~~
$ oc patch Network.operator.openshift.io cluster --type='merge' --patch '{ "spec": { "defaultNetwork": { "openshiftSDNConfig": null } } }'
network.operator.openshift.io/cluster patched (no change)
~~~

`openshift-sdn` namespace 지우기
~~~
$ oc delete namespace openshift-sdn
namespace "openshift-sdn" deleted
~~~

----