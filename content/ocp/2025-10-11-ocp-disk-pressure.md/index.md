---
title: "OCP disk pressure 해결기"
tags:
  - Kubernetes
  - Openshift
date: 2025-10-11T13:00:00+09:00
---

## Overview
노드를 운영하다보면 캐시가 쌓이고 사용하지 않는 이미지들이나 기타 등등의 이유로 노드에 `Disk Pressure`경고가 뜨는 경우가 있습니다.  
특히 cpu나 ram에 비해 root partition이 작으면 더 자주 발생하게 되죠.  

`Disk Pressure`가 뜬다고 당장 무언가 문제가 생기지는 않지만, pod들이 evicted되거나 장기적으로 운영하는데 있어서 좋지는 않습니다.  

이번 문서에서는 이 문제를 해결하기 위한 몇가지 방법을 살펴보겠습니다.  

>참고링크)   
> - [Disk pressure alarm remains on a drained node on Openshift Container Platform 4](https://access.redhat.com/solutions/6738851)  
> - [How to clean CRI-O storage in Red Hat OpenShift 4](https://access.redhat.com/solutions/5350721)  


### ISSUE
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2025/2025-10-11-ocp-disk-pressure.md/1.png)  

~~~
$ oc describe node worker4-xxx-kr.com
...
  Normal   NodeHasDiskPressure      21m (x7 over 21m)     kubelet          Node worker4-xxx-kr.com status is now: NodeHasDiskPressure
  Warning  FreeDiskSpaceFailed      17m                   kubelet          Failed to garbage collect required amount of images. Attempted to free 12962711961 bytes, but only found 0 bytes eligible to free.
  Warning  FreeDiskSpaceFailed      12m                   kubelet          Failed to garbage collect required amount of images. Attempted to free 12970498457 bytes, but only found 0 bytes eligible to free.
  Warning  FreeDiskSpaceFailed      7m8s                  kubelet          Failed to garbage collect required amount of images. Attempted to free 12973664665 bytes, but only found 0 bytes eligible to free.
  Normal   RegisteredNode           7m                    node-controller  Node worker4-xxx-kr.com event: Registered Node worker4-xxx-kr.com in Controller
  Normal   RegisteredNode           2m13s                 node-controller  Node worker4-xxx-kr.com event: Registered Node worker4-xxx-kr.com in Controller
  Warning  EvictionThresholdMet     70s (x119 over 21m)   kubelet          Attempting to reclaim ephemeral-storage
~~~
일반적인 경우엔 Garbage Collector가 주기적으로 돌면서 free space를 만들어내는데, 그 시도가 실패하게되면  
노드의 free space가 점점 줄어들게되고 결국엔 kubelet이 ephemeral storage를 claim하는데 실패하면서 새로운 pod들이 뜨지 못하게되는 악순환이 일어나게 됩니다.  

### 상태 확인하기

`Disk Pressure`확인
~~~
# curl -k -s -H "Authorization: Bearer $(oc whoami -t)" $(oc whoami --show-server)/api/v1/nodes/${node}/proxy/stats/summary | jq -r '"Used:\(.node.fs.usedBytes) Capacity:\(.node.fs.capacityBytes) Available:\(.node.fs.availableBytes)",  "imagefs:\(.node.runtime.imageFs.usedBytes)"'

Used:185915506688 Capacity:215857758208 Available:29942251520
imagefs:948400
~~~

Ephemeral Storage를 가장 많이 사용하는 pod 리스트업  
~~~
# curl -k -s -H "Authorization: Bearer $(oc whoami -t)" $(oc whoami --show-server)/api/v1/nodes/${node}/proxy/stats/summary | jq -r '.pods|.[]|"\(.["ephemeral-storage"].usedBytes) \(.podRef.namespace)/\(.podRef.name)"' | sort -n -r
~~~

### TRY 1. 오래된 이미지 삭제
노드에 접속해서 정리안된(exited상태이거나 not ready상태) pod들의 이미지를 수동으로 삭제해줍니다.  

문제 노드에 접속  
~~~
# ssh core@nodename 
~~~

Exited 상태인 컨테이너 삭제   
~~~
# crictl rm `crictl ps -q --state Exited`
~~~

Not Ready상태의 pod 삭제
~~~
# crictl rmp `crictl pods -q -s NotReady`
~~~

사용하지 않는 이미지 삭제
~~~
# crictl rmi --prune
~~~

### TRY 2. CRI-O ephemeral storage 강제로 깨끗하게 만들기(주의*)
> 이 방법은 아래의 error 케이스의 경우에만 시도해보세요! `Error reserving ctr name %s for id %s: name is reserved`와 같은 노드의 병목현상때문에 발생하는 에러에는 도움이 안됩니다.  
> - `Failed to create pod sandbox: rpc error: code = Unknown desc = failed to mount container XXX: error recreating the missing symlinks: error reading name of symlink for XXX: open /var/lib/containers/storage/overlay/XXX/link: no such file or directory`  
> - `can't stat lower layer ...  because it does not exist.  Going through storage to recreate the missing symlinks.`
> - `Failed to remove storage directory: unlinkat /var/lib/containers/storage/overlay-containers/...c8/userdata/shm: device or resource busy`  
> - `Failed to pull image "registry.redhat.io/ocs4/cephcsi-rhel8@xxx": rpc error: code = Unknown desc = Error committing the finished image: error adding layer with blob "sha256:2c...5": error creating layer with ID "a5a1f5...1": Stat /var/lib/containers/storage/overlay/0c51f...1: no such file or directory`
> - CRI-O가 계속 `SIG ABRT`로 죽는 경우

우선 문제가 되는 노드에 cordon을 걸어둡니다.  
~~~
# oc adm drain worker4-blue04.xxx-kr.com --ignore-daemonsets --delete-emptydir-data --disable-eviction --force

node/worker4-blue04.xxx-kr.com cordoned
~~~

노드에 접속해서 kubelet disable상태로 바꾸기  
~~~
[core@worker4-blue04 ~]$ sudo su
[root@worker4-blue04 core]# systemctl disable kubelet.service
Removed "/etc/systemd/system/multi-user.target.wants/kubelet.service".
~~~

노드 재부팅
~~~
# systemctl reboot
~~~

재부팅하고나서 container밑에있는 파일들을 모두 날려줍니다.  
~~~
# rm -rvf /var/lib/containers/*
~~~

다음으로 crio wipe
~~~
# crio wipe -f
INFO[2025-09-08 07:17:52.759605490Z] Updating config from single file: /etc/crio/crio.conf
INFO[2025-09-08 07:17:52.759664012Z] Updating config from drop-in file: /etc/crio/crio.conf
INFO[2025-09-08 07:17:52.760477155Z] Updating config from path: /etc/crio/crio.conf.d
INFO[2025-09-08 07:17:52.760508577Z] Updating config from drop-in file: /etc/crio/crio.conf.d/00-default
INFO[2025-09-08 07:17:52.798690781Z] Internal wipe not set, meaning crio wipe will wipe. In the future, all wipes after reboot will happen when starting the crio server.
~~~

그러고나면 파일시스템이 아주 깔끔해진 모습을 볼 수 있습니다.  
~~~
# df -h
Filesystem      Size  Used Avail Use% Mounted on
devtmpfs        4.0M     0  4.0M   0% /dev
tmpfs            32G     0   32G   0% /dev/shm
tmpfs            13G  9.1M   13G   1% /run
/dev/nvme0n1p4  202G   11G  191G   6% /sysroot
tmpfs            32G  4.0K   32G   1% /tmp
/dev/nvme0n1p3  350M  113M  214M  35% /boot
tmpfs           6.3G     0  6.3G   0% /run/user/1000
~~~

마지막으로 kubelet을 enable상태로 바꿔주고 시작시켜줍니다.  
~~~
# systemctl enable --now kubelet.service
~~~

노드 밖으로 나와서 노드가 ready 상태가 될 때까지 기다려줍니다.
~~~
# oc get node
NAME                                 STATUS                     ROLES                  AGE   VERSION
...
worker4-blue04.xxx-kr.com    Ready,SchedulingDisabled   worker                 87d   v1.31.8
~~~

ready되고나면 cordoned 상태를 해제시켜주고 상태를 지켜보면 됩니다!  
~~~
# oc adm uncordon worker4-blue04.xxx-kr.com
node/worker4-blue04.xxx-kr.com uncordoned
~~~

---