---
title: "Kubernetes Cluster Upgrade"
slug: k8s-upgrade
tags:
  - Kubernetes
date: 2021-05-24T13:00:00+09:00
---

## Overview
Kubernetes 내용을 포스팅하는게 되게 오랜만이네요...ㅎㅎ  
오늘 포스팅에서는 쿠버네티스 클러스터의 버전을 업그레이드 하는 방법을 기술하겠습니다.  

기본적인 업데이트 순서는 다음과 같습니다.  
1. 기본 컨트롤플레인 노드를 업그레이드
2. (있다면) 다른 컨트롤플레인 노드를 업그레이드
3. 워커 업그레이드  

>참고 : [kubeadm 클러스터 업그레이드](https://kubernetes.io/ko/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)

# Prerequisites
- 모든 노드가 Ready상태
- swap 비활성화
- (필요 시) 클러스터 백업
- Node draining 필요
> 모든 노드의 pod은 업그레이드가 진행된 후, 버전 해시값을 업데이트하기위해 재시작됩니다.  

# Upgrade
## Version 선택
업그레이드는 메이저버전의 경우 1단계씩 진행해야 합니다. (1.17->1.18 가능, 1.17->1.20 불가능)  

현재 저의 cluster 버전은 1.20.5입니다.  
![image](https://user-images.githubusercontent.com/15958325/119349174-d0626800-bcd8-11eb-89b3-5bf97c2eb3e0.png)   

이 클러스터를 1.21.1로 업그레이드 해보도록 하겠습니다.  

## 설치 가능한 리스트 확인
yum list를 통해 설치 가능한 `kubeadm`의 버전을 확인합니다.(타os는 위의 참고 링크 확인)  
~~~
$ yum list --showduplicates kubeadm --disableexcludes=kubernetes
~~~

![image](https://user-images.githubusercontent.com/15958325/119349291-f851cb80-bcd8-11eb-8652-fa22b9a4a986.png)  

현재 설치 가능한 리스트는 `1.20.6`, `1.20.7`, `1.21.0`, `1.21.1` 이고  
이번 포스팅에서는 `1.21.1`로 업그레이드 해보도록 하겠습니다.  

## ControlPlane Upgrade
### kubeadm upgrade 
먼저 컨트롤 플레인 노드부터 업그레이드를 진행시켜주도록 하겠습니다.  
~~~sh
# yum install -y kubeadm-{version}-0 --disableexcludes=kubernetes
$ yum install -y kubeadm-1.21.1-0 --disableexcludes=kubernetes
~~~

~~~
$ kubeadm version

kubeadm version: &version.Info{Major:"1", Minor:"21", GitVersion:"v1.21.1", GitCommit:"5e58841cce77d4bc13713ad2b91fa0d961e69192", GitTreeState:"clean", BuildDate:"2021-05-12T14:17:27Z", GoVersion:"go1.16.4", Compiler:"gc", Platform:"linux/amd64"}
~~~
> **만약 Nothing to do 메세지가 뜬다면**, 설치하려는 kubeadm 버전보다 높거나 같은 버전이 이미 설치되어 있기 때문입니다.  
>보통 클러스터를 운영하면서 **yum update**를 했을때 자동으로 kubeadm이 업그레이드 된 경우가 그런데요...   
>kubeadm을 `yum remove`로 삭제하고 다시 설치를 진행하시면 됩니다.  

### Upgrade plan 확인 
이제 업그레이드한 `kubeadm`으로 upgrade plan을 확인합니다.  
출력되는 문구에는 현재 클러스터의 각 노드들의 버전이 몇이고, 지금 가진 `kubeadm`의 버전으로 업그레이드가 가능한지 여부를 확인할 수 있습니다.  
~~~
$ kubeadm upgrade plan

[upgrade/config] Making sure the configuration is correct:
[upgrade/config] Reading configuration from the cluster...
[upgrade/config] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -o yaml'
[preflight] Running pre-flight checks.
[upgrade] Running cluster health checks
[upgrade] Fetching available versions to upgrade to
[upgrade/versions] Cluster version: v1.20.7
[upgrade/versions] kubeadm version: v1.21.1
[upgrade/versions] Target version: v1.21.1
[upgrade/versions] Latest version in the v1.20 series: v1.20.7

Components that must be upgraded manually after you have upgraded the control plane with 'kubeadm upgrade apply':
COMPONENT   CURRENT       TARGET
kubelet     3 x v1.20.5   v1.21.1

Upgrade to the latest stable version:

COMPONENT                 CURRENT    TARGET
kube-apiserver            v1.20.7    v1.21.1
kube-controller-manager   v1.20.7    v1.21.1
kube-scheduler            v1.20.7    v1.21.1
kube-proxy                v1.20.7    v1.21.1
CoreDNS                   1.7.0      v1.8.0
etcd                      3.4.13-0   3.4.13-0

You can now apply the upgrade by executing the following command:

        kubeadm upgrade apply v1.21.1

_____________________________________________________________________


The table below shows the current state of component configs as understood by this version of kubeadm.
Configs that have a "yes" mark in the "MANUAL UPGRADE REQUIRED" column require manual config upgrade or
resetting to kubeadm defaults before a successful upgrade can be performed. The version to manually
upgrade to is denoted in the "PREFERRED VERSION" column.

API GROUP                 CURRENT VERSION   PREFERRED VERSION   MANUAL UPGRADE REQUIRED
kubeproxy.config.k8s.io   v1alpha1          v1alpha1            no
kubelet.config.k8s.io     v1beta1           v1beta1             no
_____________________________________________________________________
~~~

### Upgrade! 
이제 업그레이드 할 버전을 선택하고 업그레이드를 진행해줍니다.  

~~~
$ kubeadm upgrade apply v1.21.1

[upgrade/config] Making sure the configuration is correct:
[upgrade/config] Reading configuration from the cluster...
[upgrade/config] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -o yaml'
[preflight] Running pre-flight checks.
[upgrade] Running cluster health checks
[upgrade/version] You have chosen to change the cluster version to "v1.21.1"
[upgrade/versions] Cluster version: v1.20.7
[upgrade/versions] kubeadm version: v1.21.1
[upgrade/confirm] Are you sure you want to proceed with the upgrade? [y/N]: y
…
[upgrade/successful] SUCCESS! Your cluster was upgraded to "v1.21.1". Enjoy!

[upgrade/kubelet] Now that your control plane is upgraded, please proceed with upgrading your kubelets if you haven't already done so.
~~~
위와 비슷하게 SUCCESS메세지가 떨어지면 현재 컨트롤플레인의 업그레이드를 성공적으로 마친겁니다.  

### CNI plugin 수동 업그레이드 
CNI plugin은 3rd party제공자가 주는 가이드대로 업그레이드를 해주어야 합니다.  
> k8s에서 사용할 수 있는 [CNI plugin list](https://kubernetes.io/ko/docs/concepts/cluster-administration/addons/)  

저는 calico를 사용하고 있어서 calico를 기준으로 설명드리도록 하겠습니다.  

calico upgrade 공식가이드 -> [Upgrading an installation that uses the Kubernetes API datastore](https://docs.projectcalico.org/maintenance/kubernetes-upgrade#upgrading-an-installation-that-uses-the-kubernetes-api-datastore)  
요약하면 최신 manifest파일 다시받아서 apply하자는 것입니다.  
~~~
$ kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml  
~~~
그리고 `calicoctl`도 사용하고 있다면 업그레이드 할 버전으로 설치하여야 합니다.  

모든 `calico-node`가 **Running** 상태가 되면 다음 단계로 넘어가셔도 됩니다.
~~~
$ watch kubectl get pods -n kube-system
~~~
![image](https://user-images.githubusercontent.com/15958325/119352035-21c02680-bcdc-11eb-87a0-3588cab36e12.png)  


### (Optional) 다른 컨트롤플레인 Upgrade 
맨 처음 업그레이드 한 controlplane 노드와 동일하게 `kubeadm`을 업그레이드 한 뒤, 아래 커맨드로 업그레이드를 진행합니다.  
~~~
$ kubeadm upgrade node
~~~
이미 첫 번째 노드의 업그레이드를 진행했다면, `kubeadm upgrade plan`과 **CNI plugin 업그레이드**를 진행할 필요가 없습니다.  

### kubelet, kubectl 업그레이드 
**"모든"** 컨트롤플레인 노드에서 `kubelet`과 `kubectl` 업그레이드  
~~~
$ yum install -y kubelet-1.21.1-0 kubectl-1.21.1-0 --disableexcludes=kubernetes
~~~

`kubelet` 재시작
~~~
$ sudo systemctl daemon-reload
$ sudo systemctl restart kubelet
~~~

### (Optional) ControlPlane 노드 Online상태로 변환 
draining되어 `ScheduleDisabled`상태가 된 ControlPlane 노드들을 온라인 상태로 변환시킵니다.  
~~~
$ kubectl uncordon <node-to-drain>
~~~
## Worker Node Upgrade
### Worker Node 업그레이드 
ControlPlane노드와 비슷하게 Worker노드도 `kubeadm` 부터 업그레이드 시켜줍니다.  

~~~
$ yum install -y kubeadm-1.21.1-0 --disableexcludes=kubernetes
~~~

로컬 `kubelet` 구성을 업그레이드 합니다.
~~~
$ kubeadm upgrade node

[upgrade] Reading configuration from the cluster...
[upgrade] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -o yaml'
[preflight] Running pre-flight checks
[preflight] Skipping prepull. Not a control plane node.
[upgrade] Skipping phase. Not a control plane node.
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[upgrade] The configuration for this node was successfully updated!
[upgrade] Now you should go ahead and upgrade the kubelet package using your package manager.
~~~

### 노드 drain
`kubelet` 업그레이드 하기 전에 (업그레이드 후 서비스를 재시작해야 하므로) 각 worker노드들을 `ScheduleDisabled`상태로 만들어야 합니다.  

~~~
$ kubectl drain <node-to-drain> --ignore-daemonsets
~~~

![image](https://user-images.githubusercontent.com/15958325/119353049-60a2ac00-bcdd-11eb-9daa-23090fe00448.png)  

### kubelet, kubectl 업그레이드 

~~~
$ yum install -y kubelet-1.21.1-0 kubectl-1.21.1-0 --disableexcludes=kubernetes
~~~

`kubelet` 재시작
~~~
$ sudo systemctl daemon-reload
$ sudo systemctl restart kubelet
~~~

### Worker 노드 Online상태로 변환 
draining되어 `ScheduleDisabled`상태가 된 Worker 노드들을 온라인 상태로 변환시킵니다.  
~~~
$ kubectl uncordon <node-to-drain>
~~~
## 클러스터 업그레이드 확인
모든 업그레이드 프로세스가 끝나고 나면, `kubectl get node`를 통해 모든 노드가 **Ready**상태로 올라왔는지 확인합니다.  
![image](https://user-images.githubusercontent.com/15958325/119353705-300f4200-bcde-11eb-812b-9fb5029e44c3.png)  

끝!

----