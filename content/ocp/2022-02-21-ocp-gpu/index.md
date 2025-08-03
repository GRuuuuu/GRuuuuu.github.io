---
title: "Openshift GPU노드 추가"
slug: ocp-gpu
tags:
  - Kubernetes
  - Openshift
  - GPU
  - Ndivia
date: 2022-02-21T13:00:00+09:00
---

## Overview
기본적으로 Openshift는 별도의 설정을 해주지 않으면 cpu와 ram을 비롯한 기본적인 하드웨어밖에 사용하지 못합니다.  
하드웨어 운용에 있어 별도의 드라이버가 필요한 GPU의 경우엔 어떻게 Openshift에서 사용할 수 있는지 알아보도록 하겠습니다.  


## Steps

**테스트 환경 :**  
- Openshift v4.9
- GPU : RTX3080 8GB

### 1. GPU 노드 추가
GPU를 사용하려면 실제로 GPU가 탑재되어있는 노드를 클러스터에 추가시켜야 합니다.  

<img width="438" alt="image" src="https://user-images.githubusercontent.com/15958325/154900440-8ad3a63e-7559-4c17-9f56-9917cec5af05.png">  

### 2. NFD(Node Feature Discovery) 배포

NFD는 각 노드가 가지는 기능을 openshift에서 사용할수있게 하는 오퍼레이터 입니다.  

이 오퍼레이터는 레드햇에서 기본적으로 제공하는 오퍼레이터이므로 Operator Hub에서 찾아서 설치해주도록 합니다.  

![image](https://user-images.githubusercontent.com/15958325/154900941-1a29cf62-4bb6-4180-9dc6-193ef434ad1c.png)  
![image](https://user-images.githubusercontent.com/15958325/154900950-c776a089-7a21-4c9e-a90e-57c08d957600.png)  

배포하게되면 매니저 pod가 `openshift-nfd`라는 네임스페이스에서 돌아가고 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/154901035-f338ac61-6198-4f70-a802-635863237466.png)  

Operator 화면에서 `NodeFeatureDiscovery`를 생성해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/155933956-607b0078-4124-48b5-9799-294e14070598.png)  

기본 template으로 생성   
![image](https://user-images.githubusercontent.com/15958325/155933974-71ee9d0c-f45d-4699-8c7e-be77a6a61742.png)  

그러면 각 마스터 및 워커들에 대한 nfd pod이 돌아가기 시작합니다.  
~~~
$ oc get pod -n openshift-nfd

NAME                                      READY   STATUS    RESTARTS   AGE
nfd-controller-manager-788944b976-t599p   2/2     Running   0          8m5s
nfd-master-cvqjg                          1/1     Running   0          51s
nfd-master-rrlcd                          1/1     Running   0          51s
nfd-master-znjxw                          1/1     Running   0          51s
nfd-worker-fcsls                          1/1     Running   0          51s
nfd-worker-npvlh                          1/1     Running   0          51s
nfd-worker-rnf2s                          1/1     Running   0          51s
nfd-worker-zm77p                          1/1     Running   0          51s
~~~

맨 처음 노드들의 label이 아래와 같이 짧았던 반면에,  
~~~
$ oc describe node worker0.ocp-cp4d.xxx.com

Name:               worker0.ocp-cp4d.xxx.com
Roles:              worker
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    cluster.ocs.openshift.io/openshift-storage=
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=worker0.ocp-cp4d.xxx.com
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/worker=
                    node.openshift.io/os_id=rhcos
...
~~~

뭔가 엄청 많아졌습니다.  
~~~
$ oc describe node worker0.ocp-cp4d.xxx.com
Name:               worker0.ocp-cp4d.xxx.com
Roles:              worker
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
...
                    feature.node.kubernetes.io/kernel-version.major=4
                    feature.node.kubernetes.io/kernel-version.minor=18
                    feature.node.kubernetes.io/kernel-version.revision=0
                    feature.node.kubernetes.io/pci-10de.present=true
                    feature.node.kubernetes.io/pci-10ec.present=true
                    feature.node.kubernetes.io/pci-8086.present=true
                    feature.node.kubernetes.io/pci-8086.sriov.capable=true
                    feature.node.kubernetes.io/storage-nonrotationaldisk=true
                    feature.node.kubernetes.io/system-os_release.ID=rhcos
                    feature.node.kubernetes.io/system-os_release.OPENSHIFT_VERSION=4.9
...
~~~

`feature.node.kubernetes.io`라고 라벨링된 부분이 nfd가 감지해낸 부분입니다.  

GPU가 있는 노드는 `pci`라는 prefix를 달고있습니다:  
~~~
$ oc describe node worker0.ocp-cp4d.xxx.com| egrep 'Roles|pci'

Roles:              worker
...
                    feature.node.kubernetes.io/pci-10de.present=true
                    feature.node.kubernetes.io/pci-10ec.present=true
                    feature.node.kubernetes.io/pci-8086.present=true
                    feature.node.kubernetes.io/pci-8086.sriov.capable=true
...
~~~

이제 nfd가 GPU를 찾으면서 openshift scheduler도 GPU를 리소스로 사용할 수 있게되었습니다.  

### 3. NVIDIA GPU Operator 배포
실제로 특수한 하드웨어 리소스(GPU, Infiniband, nic등)를 사용하려면 각 벤더의 드라이버나 다른 라이브러리들이 필요합니다.   

`NVIDIA GPU Operator`는 GPU쓰는데 있어서 필요한 드라이버나 플러그인들, 그리고 nvidia container runtime을 가지고있습니다.  

즉, nfd는 각 노드가 가지는 기능을 openshift에서 감지할 수 있게 하는거고, 실제로 하드웨어단의 기능을 사용하기 위해서는 맞는 드라이버/플러그인이 필요 -> GPU의 경우 "`NVIDIA GPU Operator`"  

설치는 다양한 방법으로 할 수 있습니다.  
1. [Helm chart](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html#install-helm)
2. [Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html)

이 문서에서는 Operator방식으로 설치해보도록 하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/155939413-b00bc60c-2de7-4006-913b-0c7bd3648feb.png)  
![image](https://user-images.githubusercontent.com/15958325/155939419-1026f4e3-7afc-4e8e-97bd-120d2124558b.png)  
아주 쉽게 원클릭으로 설치 성공!  

>기본적으로 모니터링에 대한 라벨링이 붙지 않으므로 프로메테우스 메트릭을 수집하게 하려면, 다음 라벨을 namespace에 붙여주자   
>~~~
>$ oc label ns/nvidia-gpu-operator openshift.io/cluster-monitoring=true
>
>namespace/nvidia-gpu-operator labeled
>~~~

Operator에 대한 `ClusterPolicy` 생성  
![image](https://user-images.githubusercontent.com/15958325/155939638-d10439b5-5114-4f01-a0fd-2a6b5a21f63d.png)  
![image](https://user-images.githubusercontent.com/15958325/155939644-d6f9e302-7d9c-4725-8a81-ccdd59169ca0.png)  

한 10분20분기다리면 Ready가 됩니다.  

> vGPU의 경우, 다른 option을 줘야합니다.  
>->[참고 : Create the ClusterPolicy instance with NVIDIA vGPU¶](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html#create-the-clusterpolicy-instance-with-nvidia-vgpu)  

~~~
$ oc get pod -n nvidia-gpu-operator
NAME                                                 READY   STATUS      RESTARTS   AGE
gpu-feature-discovery-8xdmk                          1/1     Running     0          23m
gpu-feature-discovery-jkdgb                          1/1     Running     0          23m
gpu-feature-discovery-lnb98                          1/1     Running     0          23m
...
nvidia-operator-validator-29jx4                      1/1     Running     0          3m46s
nvidia-operator-validator-72k66                      1/1     Running     0          23m
nvidia-operator-validator-9ccdq                      1/1     Running     0          23m
nvidia-operator-validator-9g6zc                      1/1     Running     0          23m
~~~


`nvidia-driver-daemonset-*`pod에 `nvidia-smi` 명령어를 치면 해당 daemonset이 올라가있는 node의 GPU현황을 볼 수 있습니다.  

~~~
$ oc exec -it nvidia-driver-daemonset-49.84.202111231504-0-2dcxf -- nvidia-smi

Defaulted container "nvidia-driver-ctr" out of: nvidia-driver-ctr, openshift-driver-toolkit-ctr, k8s-driver-manager (init)
Thu Feb 17 07:20:08 2022
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.82.01    Driver Version: 470.82.01    CUDA Version: 11.4     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  On   | 00000000:01:00.0 Off |                  N/A |
| N/A   53C    P0    35W /  N/A |      1MiB /  7982MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
~~~

### 4. TEST!
GPU를 사용하는 pod을 테스트로 돌려서 제대로 GPU 리소스를 사용하는지 확인해보겠습니다.  

~~~
apiVersion: v1
kind: Pod
metadata:
  name: cuda-vectoradd
spec:
 restartPolicy: OnFailure
 containers:
 - name: cuda-vectoradd
   image: "nvidia/samples:vectoradd-cuda11.2.1"
   resources:
     limits:
       nvidia.com/gpu: 1
~~~

배포하고 로그를 보면 다음과 같이 잘 동작하는 것을 확인할 수 있습니다.  
~~~
$ oc logs cuda-vectoradd

[Vector addition of 50000 elements]
Copy input data from the host memory to the CUDA device
CUDA kernel launch with 196 blocks of 256 threads
Copy output data from the CUDA device to the host memory
Test PASSED
Done
~~~

----