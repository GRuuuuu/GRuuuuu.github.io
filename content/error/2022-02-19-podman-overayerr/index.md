---
title: "[CRI-O] creating read-write layer with ID... no such file or directory"
slug: podman-overayerr
tags:
  - Kubernetes
  - Podman
  - Container
date: 2022-02-19T13:00:00+09:00
---


## Environment
`OS : RedHat CoreOS 4.9`   
`Openshift : 4.9`  
`Kubernetes : v1.22.3+4dd1b5a`  
`Cri-O : 1.22`  


## ERROR
(에러 났을때 기록해둔 로그가 없어서.... 해결하는데 참고했던 github issue의 에러로그를 그대로 복사해둡니다.)  

Solution : [creating read-write layer with ID No such file or directory - crio reading from overlay instead of overlay2?](https://github.com/cri-o/cri-o/issues/3768)  

~~~
Warning  FailedCreatePodSandBox  2s (x4 over 43s)  kubelet, kube6     (combined from similar events): Failed create pod sandbox: rpc error: code = Unknown desc = error creating pod sandbox with name "some-sandbox-name": error creating read-write layer with ID "a5021e65186da551b712f7dd743d712833e5f75fc727c6f937d421897d2eb9d6": Stat /var/lib/containers/storage/overlay/e17133b79956ad6f69ae7f775badd1c11bad2fc64f0529cab863b9d12fbaa5c4: no such file or directory
~~~

Kubernetes 클러스터를 운영하다보면 노드를 추가할때도 있고 뺄 때도 있습니다.  
원인을 모르겠지만 어느 순간 무언가가 잘 안돌아갈 때가 있는데요...

잘 돌아가는 것처럼 보이지만 문제가 되는 노드에 pod이 배포되면 Image를 제대로 pulling하지 못하는 이슈가 발생할 때가 있습니다.  

저도 이 에러가 왜 일어나는지, 무엇이 문제인지 잘 모르겠습니다.  
어떤 분이 올려주신 github issue를 참고해서 해결했던 과정을 적어두도록 하겠습니다  

## Solution
#### 1. 문제가 되는 노드에 ssh 접속  
#### 2. crio 서비스 다운
~~~
$ systemctl stop crio
~~~
#### 3. crio 버전 삭제/백업
저 issue에서는 삭제하라는데 저는 혹시 몰라서 백업해뒀습니다  

이렇게 version파일을 없애는 이유는 `crio wipe` 명령어 실행시 version 파일이 없거나 만료되었으면 crio의 컨테이너들과 이미지 스토리지를 모두 지워버리게 하기 위해서입니다.  
~~~
$ mv /var/lib/crio/version /home/core/
~~~

#### 4. crio wipe

> crio wipe : [manpage](https://man.archlinux.org/man/community/cri-o/crio.8.en#wipe)  

crio의 컨테이너들과 이미지 저장소를 전부 날려버립니다.  

~~~
$ crio wipe
~~~

#### 5. lib/container와 run/container 삭제
~~~
$ rm -rf /var/{run,lib}/containers
~~~

#### 6. reboot
~~~
$ sudo reboot
~~~
#### 7. kubelet 재시작
재부팅되고나서 kubelet을 재구동시켜줍니다  
~~~
$ systemctl restart kubelet
~~~

이렇게 하면 문제가 되던 노드의 모든 이미지 및 컨테이너를 날려버리고 초기화시키게 되고,  
kubelet이 재기동되면서 kubernetes의 etcd클러스터에 의해 필요한 pod들을 알아서 복원하게 됩니다.  

복원하는데 시간은 걸리긴하지만 기본적인 kubernetes서비스 pod들은 빠른 시간 내에 복원하는 편이고 다른 서비스 pod들은 시간이 좀 걸립니다.  

----