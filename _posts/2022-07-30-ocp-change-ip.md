---
title: "Openshift 노드 IP 변경 (feat. NMstate)"
categories:
  - OCP
tags:
  - Kubernetes
  - Openshift
  - Network
  - NMstate
last_modified_at: 2022-07-30T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview
이번 문서에서는 클러스터의 노드 ip를 변경하는 방법에 대해서 알아보겠습니다.  


## Steps

### 1.1 IP수동변경

일단 기본적으로 노드의 ip를 바꾸려면 물리적으로 ip를 변경해주어야 합니다.  

ip를 변경하려는 노드에 접속하여 `nmcli`/`nmtui`로 ip를 변경해줍니다.  

`NetworkManager` restart도 해줍니다.  

### 1.2 NMstate를 통한 IP변경

참고 :  
[Openshift doc/About the Kubernetes NMState Operator](https://docs.openshift.com/container-platform/4.10/networking/k8s_nmstate/k8s-nmstate-about-the-k8s-nmstate-operator.html)  
[Openshift doc/Updating node network configuration](https://docs.openshift.com/container-platform/4.10/networking/k8s_nmstate/k8s-nmstate-updating-node-network-config.html)

`Kubernetes NMstate Operator`는 클러스터의 네트워크 상태를 Kubernetes API를 통해 인프라가아닌 클러스터 위에서 관리할 수 있게 해줍니다.  
`v4.7`에서 처음 등장해 계속 techpreview기능이었지만 `v4.10`에서부터는 정식으로 서포트를 받을 수 있는 기능입니다.  

최대한 외부로부터의 인프라 개입을 막고 로우레벨부터 하이레벨까지 모든영역을 클러스터에서 관리하겠다는 Openshift의 철학에도 어느정도 맞는 부분인것같네요...   

`NMstate`가 가능한 범위는 :  
- Network interface type (`bridge`, `VLAN`, `Bond`, `Ethernet`)
- DNS
- routing  

등등 이고 더 자세한 내용은 문서참고!  


일단 Operator Hub로 이동하여 `Kubernetes NMstate Operator`을 설치합니다.  
![image](https://user-images.githubusercontent.com/15958325/181908646-24db2a17-65ab-48c4-be81-2c52d42788bd.png)  

그다음 `nmstate` 인스턴스 생성  
![image](https://user-images.githubusercontent.com/15958325/181908668-1c0a3a6e-3938-4354-85b6-30ef1fc81cf2.png)  

그리고 조금만 기다리면 `nmstate`가 각 노드의 네트워크 구성정보를 가져옵니다.  
~~~
$ oc get nns
NAME                        AGE
master1.blue.ddd.com   3h2m
master2.blue.ddd.com   3h2m
master3.blue.ddd.com   3h2m
worker1.blue.ddd.com   3h2m
worker2.blue.ddd.com   3h2m
worker3.blue.ddd.com   3h2m
~~~

하나 노드를 골라서 정보를 확인해보면 현재 노드의 `NodeNetworkState`를 확인할 수 있습니다.   
~~~yaml
$ oc get nns master1.blue.ddd.com -oyaml

apiVersion: nmstate.io/v1beta1
kind: NodeNetworkState
metadata:
  creationTimestamp: "2022-07-21T02:12:31Z"
  generation: 1
  name: master1.blue.ddd.com
  ownerReferences:
  - apiVersion: v1
    kind: Node
    name: master1.blue.ddd.com
    uid: 9ec1aca6-045e-4d8c-a834-30e1c01c0792
  resourceVersion: "18258464"
  uid: e5f76655-6959-4e24-b1ee-c27efaa1bf87
status:
  currentState:
    dns-resolver:
      config:
        search: []
        server:
        - 10.10.12.12
  …
  handlerNetworkManagerVersion: 1.30.0-14.el8_4
  handlerNmstateVersion: 1.0.2
  hostNetworkManagerVersion: 1.30.0
  lastSuccessfulUpdateTime: "2022-07-21T02:12:31Z"
~~~

이제 특정 노드의 네트워크 정보를 변경시키려면 `NodeNetworkConfigurationPolicy`를 생성해주어야 합니다.  
~~~yaml
apiVersion: nmstate.io/v1
kind: NodeNetworkConfigurationPolicy
metadata:
  name: master1-nmpolicy
spec:
  nodeSelector:
    kubernetes.io/hostname: master1.blue.ddd.com
  desiredState:
    interfaces:
      - name: enp1s0
        description: change ip
        type: ethernet
        state: up
        ipv4:
          dhcp: true
          enabled: true
          auto-dns: false
~~~
- 새 policy를 적용할 node는 `nodeSelector`로 선택  
- 원하는 네트워크 구성정보는 `desiredState`하위에 작성  

>위의 예시는 기존에 ip를 static으로 부여해주던 노드를 `dhcp`로 변경하는 작업입니다.  

~~~
$ oc get nncp
NAME               STATUS
master1-nmpolicy   Available

$ oc get nnce
NAME                                         STATUS
master1.blue.ddd.com.master2-nmpolicy   Available
~~~
확인해보면 policy가 제대로 배포된 것을 확인할 수 있습니다.  

하지만 노드 리부트 없이 network정보가 변경되진 않더군요...   
강제로 **변경된 노드를 재시작**시켜줍니다.  

재시작하니 ip를 dhcp에서 설정해준 ip(10.10.12.27)로 제대로 받아온 모습을 확인할 수 있습니다.  
~~~
$ oc get node -owide
NAME                        STATUS   ROLES    AGE   VERSION           INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                                                        KERNEL-VERSION                 CONTAINER-RUNTIME
...
master1.blue.ddd.com   Ready    master   29d   v1.23.5+3afdacb   10.10.12.27   <none>        Red Hat Enterprise Linux CoreOS 410.84.202206080346-0 (Ootpa)   4.18.0-305.49.1.el8_4.x86_64   cri-o://1.23.3-3.rhaos4.10.git5fe1720.el8
...
~~~  

### 2. DNS, LB 수정
노드의 ip를 바꿔주었으니 DNS와 LoadBalancer에도 바뀐 ip로 업데이트를 진행해줍니다.  

### 3. csr승인
클러스터의 정보가 일부 변경되어 재시작되었으니 새로 인증을 요청하게 됩니다.  

~~~
$ oc get csr
~~~
위 명령어를 통해서 현재 pending된 요청을 찾고 승인해주도록 합시다.  

~~~
$ oc adm certificate approve <csr>
~~~

### 문제발생!!!
이렇게 잘 마무리되나 싶었는데, etcd에서 계속 에러가 발생합니다.  

<img width="604" alt="image" src="https://user-images.githubusercontent.com/15958325/181909357-52d8dc85-42ed-4f39-8a53-faad889c63fa.png">  

`CrashloopBackOff`가 난 pod의 로그를 까보니  
~~~
$ oc logs etcd-master1.blue.ddd.com etcd
~~~  

<img width="658" alt="image" src="https://user-images.githubusercontent.com/15958325/181909381-a0b2b3ce-a4e3-4494-9da8-b38f28c18113.png">  

etcd의 endpoint가 변경했던 새로운 ip로 바뀌지 않아서 생긴 문제였습니다!  

### 4. ETCD 복구  
참고 : [Openshift doc/Replacing an unhealthy etcd member whose etcd pod is crashlooping](https://docs.openshift.com/container-platform/4.10/backup_and_restore/control_plane_backup_and_restore/replacing-unhealthy-etcd-member.html#restore-replace-crashlooping-etcd-member_replacing-unhealthy-etcd-member)  

etcd는 static pod로 동작하기 때문에 클러스터에서 직접적으로 삭제할 수 없습니다.  

문제의 node로 이동:  
~~~
$ oc debug node/master1.blue.garagekr.com
Starting pod/master1bluegaragekrcom-debug ...
To use host binaries, run `chroot /host`
Pod IP: 10.10.12.27
If you don't see a command prompt, try pressing enter.

sh-4.4# chroot /host
~~~

etcd static pod 지우기(옮기기)
~~~
sh-4.4# mv /etc/kubernetes/manifests/etcd-pod.yaml /var/lib/etcd-backup/

sh-4.4# mv /var/lib/etcd/ /tmp

sh-4.4# exit
exit
~~~

나와서 etcd리스트를 다시 출력해보면 master1의 etcd가 사라진 것을 확인할 수 있습니다  
~~~
$ oc get pods -n openshift-etcd | grep -v etcd-quorum-guard | grep etcd

etcd-master2.blue.ddd.com                 4/4     Running     0          126m
etcd-master3.blue.ddd.com                 4/4     Running     0          122m
~~~

그 다음, 정상적으로 동작하는 etcd pod들 중 아무거나 하나 들어갑니다.  
~~~
$ oc rsh etcd-master2.blue.ddd.com
Defaulted container "etcdctl" out of: etcdctl, etcd, etcd-metrics, etcd-health-monitor, setup (init), etcd-ensure-env-vars (init), etcd-resources-copy (init)

sh-4.4#
~~~

`etcdctl` 명령어를 통해 현재 etcd클러스터의 member리스트를 확인합니다.  
~~~
sh-4.4# etcdctl member list -w table
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
|        ID        | STATUS  |           NAME            |        PEER ADDRS        |       CLIENT ADDRS       | IS LEARNER |
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
| 8d21c67207b6856d | started | master3.blue.ddd.com | https://10.10.12.29:2380 | https://10.10.12.29:2379 |      false |
| ac058e511f9cef66 | started | master2.blue.ddd.com | https://10.10.12.20:2380 | https://10.10.12.20:2379 |      false |
| afb2836827fbb808 | started | master1.blue.ddd.com | https://10.10.12.15:2380 | https://10.10.12.15:2379 |      false |
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
~~~
1번 member의 endpoint가 여전히 안바뀐 상태입니다.  

이녀석을 삭제했다가 다시 join시키도록 하겠습니다.  

~~~
$ etcdctl member remove <ETCD ID>
Member afb2836827fbb808 removed from cluster cbd963f63220137b
~~~

~~~
sh-4.4# etcdctl member list -w table
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
|        ID        | STATUS  |           NAME            |        PEER ADDRS        |       CLIENT ADDRS       | IS LEARNER |
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
| 8d21c67207b6856d | started | master3.blue.ddd.com | https://10.10.12.29:2380 | https://10.10.12.29:2379 |      false |
| ac058e511f9cef66 | started | master2.blue.ddd.com | https://10.10.12.20:2380 | https://10.10.12.20:2379 |      false |
+------------------+---------+---------------------------+--------------------------+--------------------------+------------+
~~~
사라졌다!  

이제 pod밖으로 나와서  
master1번 etcd와 관련된 모든 secret도 삭제해줍니다.  

~~~
$ oc get secret -n openshift-etcd |grep master1
etcd-peer-master1.blue.ddd.com              kubernetes.io/tls                     2      29d
etcd-serving-master1.blue.ddd.com           kubernetes.io/tls                     2      29d
etcd-serving-metrics-master1.blue.ddd.com   kubernetes.io/tls                     2      29d
~~~

삭제:
~~~
$ oc delete secret etcd-peer-master1.blue.ddd.com
secret "etcd-peer-master1.blue.ddd.com" deleted

$ oc delete secret etcd-serving-master1.blue.ddd.com
secret "etcd-serving-master1.blue.ddd.com" deleted

$ oc delete secret etcd-serving-metrics-master1.blue.ddd.com
secret "etcd-serving-metrics-master1.blue.ddd.com" deleted
~~~  

etcd복구:  
~~~
$ oc patch etcd cluster -p='{"spec": {"forceRedeploymentReason": "single-master-recovery-'"$( date --rfc-3339=ns )"'"}}' --type=merge 

etcd.operator.openshift.io/cluster patched
~~~  

좀 기다리면 다시 etcd pod이 뜹니다.  
~~~
$ oc get pod
NAME                                           READY   STATUS      RESTARTS        AGE
etcd-master1.blue.ddd.com                 4/4     Running     1 (5m24s ago)   5m27s
etcd-master2.blue.ddd.com                 4/4     Running     0               3m52s
etcd-master3.blue.ddd.com                 4/4     Running     0               115s
~~~

etcd클러스터 상태도 healthy!!   

<img width="632" alt="image" src="https://user-images.githubusercontent.com/15958325/181909792-11018daf-05ec-459c-85fb-c630478db0aa.png">  

이제 정상적으로 Openshift클러스터를 사용할 수 있습니다!  

----