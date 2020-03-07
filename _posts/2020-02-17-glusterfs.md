---
title: "GlusterFS basic"
categories: 
  - LINUX
tags:
  - LINUX
  - Cloud
  - GlusterFS
  - NAS
  - FUSE
last_modified_at: 2020-02-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
GlusterFS의 컨셉에 대해 설명하고, 간단한 데모를 보여드리겠습니다.

# What is GlusterFS?
![image](https://user-images.githubusercontent.com/15958325/74626191-469d2400-5192-11ea-9a7d-352d043e1f8d.png)  
클라우드 환경에서 **분산되어 있는 서버의 디스크를 묶어 하나의 분산 파일 시스템으로** 만든다면, 클라우드 구축과 운영에 있어 매우 도움이 될 것입니다.  

**GlusterFS**는 Software Defined Storage로, Scale-Out한 NAS(`Network Attached Storage`)파일 시스템입니다.  

다양한 스토리지 서버를 네트워크(`Ethernet`, `Infiniteband RDMA`)를 통해 하나의 디스크 풀로 묶어 소프트웨어적으로 복제본을 관리하고 자가 복구 및 스냅샷을 관리할 수 있습니다. 이를 통해 클라우드 기반으로 생성된 vm의 볼륨들을 안정적으로 관리할 수 있게 됩니다.  

<img src="https://user-images.githubusercontent.com/15958325/74629567-dc897c80-519b-11ea-9b3e-0e7c6a315070.png" width="600px">  

GlusterFS는 **클라이언트**와 **서버**로 구성되며, 서버는 `Brick` 이라는 형태로 볼륨을 제공합니다.  
각 서버들은 `glusterfsd` 데몬을 통해 Brick을 하나의 Volume Pool로 묶고,    
클라이언트는 `TCP/IP`, `InfiniBand` 등을 통해 Volume에 마운트할 수 있습니다.  

**특징**  
- 파일정보를 각 서버마다 가지고 있음 (metadata server 필요x)
- PB단위로 확장가능 & 다수의 클라이언트 처리가능 (기본NAS는 확장, 처리에 한계가 있음)
- Opensource Software

# GlusterFS Volume Architecture
이제 GlusterFS에서 구성할 수 있는 볼륨들을 설명드리겠습니다.  

> 참고링크 : [Gluster Docs/Architecture](https://docs.gluster.org/en/latest/Quick-Start-Guide/Architecture/)

## Distributed Glusterfs Volume
아무 옵션을 주지 않았을 때 구성되는 기본구조입니다.  

<img src="https://cloud.githubusercontent.com/assets/10970993/7412364/ac0a300c-ef5f-11e4-8599-e7d06de1165c.png" width="600px">  

그림과 같이 **각 파일들이 따로따로 Brick에 저장**됩니다. File1같은 경우는 server1의 Brick에만 저장되기 때문에 만약 server1에 장애가 발생한다면 File1은 사용할 수 없는 상태가 됩니다.  

**목적**   
- 쉽고 싸게 scale-out이 가능

**단점**
- NO data redundancy 
- brick 장애 -> 데이터의 유실을 의미

### Command
생성하려면 :   
~~~sh
$ gluster volume create NEW-VOLNAME [transport [tcp | rdma | tcp,rdma]] NEW-BRICK...
~~~

예시 :   
~~~sh
$ gluster volume create test-volume server1:/exp1 server2:/exp2
~~~

## Replicated Glusterfs Volume
Distributed Volume에서 발생했던 데이터 유실을 막기 위한 구조입니다.  

<img src="https://cloud.githubusercontent.com/assets/10970993/7412379/d75272a6-ef5f-11e4-869a-c355e8505747.png" width="600px">  

File1은 복사되어 server1과 server2 모두에 저장되게 되고, 만약 server1이 장애가 나더라도 server2에서 데이터를 가져와서 사용할 수 있습니다.  
복사할 서버가 존재해야하기 때문에, 최소 2개 이상의 서버가 필요합니다.  

**목적**  
- 데이터의 redundancy와 신뢰성을 높일 수 있음

**단점**  
- 서버 총 용량의 1/2밖에 쓰지 못함

### Command
생성하려면 :   
~~~sh
$ gluster volume create NEW-VOLNAME [replica COUNT] [transport [tcp |rdma | tcp,rdma]] NEW-BRICK...
~~~

예시 :   
~~~sh
$ gluster volume create test-volume replica 2 transport tcp server1:/exp1 server2:/exp2
~~~

## Striped Glusterfs Volume
데이터를 쪼개서 저장하는 방법입니다.  
<img src="https://user-images.githubusercontent.com/15958325/74706908-95fb5700-525b-11ea-9bab-4d7a8cbc6e09.png" width="600px">  

File1을 쪼개서 각각 server에 저장합니다. R/W 속도가 빠릅니다.  
하지만 분산된 데이터 중 하나만 망가져도 전체 데이터를 사용할 수 없습니다.  

### Command
생성하려면 :   
~~~sh
$ gluster volume create NEW-VOLNAME [stripe <COUNT>] [transport [tcp |rdma | tcp,rdma]] NEW-BRICK...
~~~

예시 :   
~~~sh
$ gluster volume create test-volume stripe transport tcp server1:/exp1 server2:/exp2
~~~

## Dispersed Glusterfs Volume
erasure coding을 기반으로한 저장 방법입니다.  
[참고링크 : Erasure Coding](https://m.blog.naver.com/PostView.nhn?blogId=kmk1030&logNo=220690448974&proxyReferer=https%3A%2F%2Fwww.google.com%2F)  

![image](https://user-images.githubusercontent.com/15958325/74707168-5a14c180-525c-11ea-8401-f079ec0d36c9.png)  

Raid 5와 6과 유사하지만 5와 6이 각각 1개와 2개씩밖에 고장을 허용할수 있는데 반해 disperse는 정하는 만큼 고장을 허용할 수 있습니다.  

### Command
생성하려면 :   
~~~sh
$ gluster volume create NEW-VOLNAME [disperse-data COUNT] [redundancy COUNT] [transport tcp | rdma | tcp,rdma] NEW-BRICK...
~~~

Disperse 볼륨을 만드는데 필요한 brick의 개수는 `disperse-data` + `redundancy`로 계산됩니다.  

`disperse-data` : redundancy를 제외한 brick  
`redundancy` : 몇 개 부셔져도 괜찮은지  

`redundancy`만 명시해주면 자동으로 `disperse-data`값이 채워집니다.  
만약 `redundancy`가 명시되어있지 않다면 glusterfs의 cofiguration에 의해 자동 계산되어 들어갑니다. (warnning 발생)

예시 :   
~~~sh
$ gluster volume create test-volume redundancy 2 transport tcp server1:/exp1 server2:/exp2 server3:/exp3 server4:/exp3 server5:/exp3 server6:/exp3 server7:/exp3  
~~~
서버는 총 7대고 redundancy는 2니 disperse-data는 5입니다.  
파일조각 아무거나 5조각만 있으면 원본 파일을 복구할 수 있습니다.  

# Hands-On
지금부터 GlusterFS의 설치, 구성을 해보겠습니다.  

해당 포스팅에서는 1대의 클라이언트, 2대의 서버를 Replica방식으로 구성해보도록 하겠습니다.  

## Prerequisites
**Client**   
`os: CentOS v7.7`  
`arch: x86_64`  

**Server1(gfs01)**   
`os: CentOS v7.7`  
`arch: x86_64`  

**Server2(gfs02)**   
`os: CentOS v7.7`  
`arch: x86_64`  

## Before Installation
설치하기 이전에 모든 인스턴스에 hosts파일 설정을 해줍니다.  
~~~sh
$ vim /etc/hosts

# server의 ip와 hostname
xx.xx.xx.xx gfs01
xx.xx.xx.xx gfs02
~~~

## Installation (for Server)
glusterfs-server를 설치해줍니다.  
~~~sh
$ yum install centos-release-gluster
$ yum install glusterfs-server
~~~

서비스 시작  
~~~sh
$ systemctl start glusterd
~~~

(optional)방화벽 끄기  
~~~sh
$ systemctl stop firewalld
~~~

## Peer 연결
gfs01서버에서 클러스터를 생성해줍니다.  
~~~sh
$ gluster peer probe gfs02
~~~
![image](https://user-images.githubusercontent.com/15958325/74710164-51c08480-5264-11ea-8569-f9a872ed09b7.png)  

클러스터의 상태를 확인합니다.  
~~~sh
$ gluster peer status
~~~
![image](https://user-images.githubusercontent.com/15958325/74710191-63099100-5264-11ea-9bfa-634840533683.png)  

gfs02서버에서 똑같이 상태를 확인해보면 peer에 gfs01이 뜨는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/74710241-79afe800-5264-11ea-9957-fd1da2d785eb.png)  

## Volume 생성
각 서버에서(gfs01, gfs02) 볼륨 디렉토리를 생성해줍니다.  
이 디렉토리들은 brick이 되어, 밑에서 Volume으로 묶어줄 것입니다.  
~~~sh
$ mkdir -p /glusterfs/fs
~~~

이제 볼륨을 생성할 건데, 기본 syntax는 다음과 같습니다.  
~~~sh
$ volume create <NEW-VOLNAME> [stripe <COUNT>] [[replica <COUNT> [arbiter <COUNT>]]|[replica 2 thin-arbiter 1]] [disperse [<COUNT>]] [disperse-data <COUNT>] [redundancy <COUNT>] [transport <tcp|rdma|tcp,rdma>] <NEW-BRICK> <TA-BRICK>... [force]
~~~

세부 내용은 위에서 서술한 **GlusterFS Volume Architecture**를 참고해주세요.  

이번 테스트에서는 replica 옵션을 사용해서 만들어보겠습니다.  
~~~sh
$ gluster volume create vol replica 2 transport tcp gfs01:/glusterfs/fs gfs02:/glusterfs/fs force
~~~

## Volume 시작
생성한 볼륨을 시작시켜줍니다.  
~~~sh
$ gluster volume start vol
~~~
![image](https://user-images.githubusercontent.com/15958325/74710913-0a3af800-5266-11ea-8b06-22054849c7d8.png)  

볼륨 정보를 확인해보면 볼륨을 구성하고 있는 brick들의 정보도 확인할 수 있습니다.     
~~~sh
$ gluster volume info vol
~~~
![image](https://user-images.githubusercontent.com/15958325/74710894-04ddad80-5266-11ea-927a-d96af71466b0.png)  


## Mount Volume to Client
Gluster Volume이 구성되었으니 그 볼륨을 Client에 마운트할 차례입니다.  

glusterfs에서 제공하는 마운트 방법은 `NFS`, `CIFS`, `Gluster Native`(`FUSE`)가 있습니다.   
일반적으로 NFS보다 FUSE로 마운트 할 시, 성능이 더 잘나온다고 합니다.  
단, 작은 파일에서는 NFS의 캐시 영향을 받아서 성능이 더 좋다고 합니다.  
하지만 NFS로 마운트시, 마운트 한 서버가 죽으면 해당 볼륨에 접근할 수 없습니다.  
반면 FUSE로 마운트하면 마운트 한 서버가 죽어도 나머지 사용가능한 서버에 접근하여 사용할 수 있습니다.   

해당 포스팅에서는 FUSE로 마운트해보겠습니다.  

client에서 FUSE를 설치해줍니다.  
~~~sh
$ yum install centos-release-gluster
$ yum install glusterfs glusterfs-fuse
~~~

마운트 하기 위한 적당한 폴더를 만들어줍니다.  
~~~sh
$ mkdir /root/test
~~~

마운트 :  
~~~sh
# mount -t {mount-type} {server ip}:{volume name} {local mount point}
# gfs01또는 02로
$ mount -t glusterfs gfs01:vol /root/test
~~~

그다음 디스크를 확인해보면 :  
~~~sh
$ df /root/test
~~~
![image](https://user-images.githubusercontent.com/15958325/74717359-9a336e80-5273-11ea-9510-b6c54c5c0c97.png)  
제대로 마운트 된 것을 확인해보실 수 있습니다.  

파일을 생성하고, gfs01과 gfs02서버의 brick에가서 보면 똑같은 파일이 생성된 것을 확인할 수 있습니다.  

# Appendix. ERRORs
## 1.  Volume 'vol-utime', line 46: type 'features/utime' is not valid or not found on this machine

Full log :  
~~~sh
[2020-02-14 04:55:02.783542] I [MSGID: 100030] [glusterfsd.c:2646:main] 0-/usr/sbin/glusterfs: Started running /usr/sbin/glusterfs version 3.12.2 (args: /usr/sbin/glusterfs --volfile-server=169.59.4.56 --volfile-id=vol /root/test)
[2020-02-14 04:55:02.816208] W [MSGID: 101002] [options.c:995:xl_opt_validate] 0-glusterfs: option 'address-family' is deprecated, preferred is 'transport.address-family', continuing with correction
[2020-02-14 04:55:02.823615] I [MSGID: 101190] [event-epoll.c:676:event_dispatch_epoll_worker] 0-epoll: Started thread with index 0
[2020-02-14 04:55:02.823700] I [MSGID: 101190] [event-epoll.c:676:event_dispatch_epoll_worker] 0-epoll: Started thread with index 1
[2020-02-14 04:55:02.827634] W [MSGID: 101095] [xlator.c:213:xlator_dynload] 0-xlator: /usr/lib64/glusterfs/3.12.2/xlator/features/utime.so: cannot open shared object file: No such file or directory
[2020-02-14 04:55:02.827665] E [MSGID: 101002] [graph.y:213:volume_type] 0-parser: Volume 'vol-utime', line 46: type 'features/utime' is not valid or not found on this machine
[2020-02-14 04:55:02.827686] E [MSGID: 101019] [graph.y:321:volume_end] 0-parser: "type" not specified for volume vol-utime
[2020-02-14 04:55:02.827824] E [MSGID: 100026] [glusterfsd.c:2473:glusterfs_process_volfp] 0-: failed to construct the graph
[2020-02-14 04:55:02.828117] W [glusterfsd.c:1462:cleanup_and_exit] (-->/usr/sbin/glusterfs(mgmt_getspec_cbk+0x532) [0x55bfeb7dcb02] -->/usr/sbin/glusterfs(glusterfs_process_volfp+0x193) [0x55bfeb7d6633] -->/usr/sbin/glusterfs(cleanup_and_exit+0x6b) [0x55bfeb7d5b2b] ) 0-: received signum (-1), shutting down
[2020-02-14 04:55:02.828192] I [fuse-bridge.c:6611:fini] 0-fuse: Unmounting '/root/test'.
[2020-02-14 04:55:02.831439] I [fuse-bridge.c:6616:fini] 0-fuse: Closing fuse connection to '/root/test'.
~~~

서버와 클라이언트의 버전이 달라서 생기는 문제이다.  
버전을 맞춰주면 해결!  
~~~sh
$ glusterfs --version
~~~

## 2. cannot access test: Transport endpoint is not connected
Full log :  
~~~sh
[root@test ~]# ls
ls: cannot access test: Transport endpoint is not connected
~~~
마운트가 실패하고나서 해당 폴더와 연결이 안되는 문제이다.  
강제로 언마운트 시켜주면 해결!  

~~~sh
$ umount /root/test
~~~

## 3. no subvolumes up
Full log :  
~~~sh
[2020-02-14 07:53:13.347729] I [fuse-bridge.c:5166:fuse_init] 0-glusterfs-fuse: FUSE inited with protocol versions: glusterfs 7.24 kernel 7.23
[2020-02-14 07:53:13.347773] I [fuse-bridge.c:5777:fuse_graph_sync] 0-fuse: switched to graph 0
[2020-02-14 07:53:13.347936] I [MSGID: 108006] [afr-common.c:5710:afr_local_init] 0-vol-replicate-0: no subvolumes up
[2020-02-14 07:53:13.348015] E [fuse-bridge.c:5235:fuse_first_lookup] 0-fuse: first lookup on root failed (Transport endpoint is not connected)
[2020-02-14 07:53:13.348280] W [fuse-bridge.c:1276:fuse_attr_cbk] 0-glusterfs-fuse: 2: LOOKUP() / => -1 (Transport endpoint is not connected)
[2020-02-14 07:53:13.352039] W [fuse-bridge.c:1276:fuse_attr_cbk] 0-glusterfs-fuse: 3: LOOKUP() / => -1 (Transport endpoint is not connected)
[2020-02-14 07:53:13.358373] I [fuse-bridge.c:6083:fuse_thread_proc] 0-fuse: initiating unmount of /root/test
The message "I [MSGID: 108006] [afr-common.c:5710:afr_local_init] 0-vol-replicate-0: no subvolumes up" repeated 2 times between [2020-02-14 07:53:13.347936] and [2020-02-14 07:53:13.352013]
[2020-02-14 07:53:13.358836] W [glusterfsd.c:1596:cleanup_and_exit] (-->/lib64/libpthread.so.0(+0x7e65) [0x7fd367451e65] -->/usr/sbin/glusterfs(glusterfs_sigwaiter+0xe5) [0x55c4e0a22625] -->/usr/sbin/glusterfs(cleanup_and_exit+0x6b) [0x55c4e0a2248b] ) 0-: received signum (15), shutting down
[2020-02-14 07:53:13.358873] I [fuse-bridge.c:6871:fini] 0-fuse: Unmounting '/root/test'.
[2020-02-14 07:53:13.358888] I [fuse-bridge.c:6876:fini] 0-fuse: Closing fuse connection to '/root/test'.
~~~

graph를 확인해보면  
~~~sh
...
Final graph:
+------------------------------------------------------------------------------+
  1: volume vol-client-0
  2:     type protocol/client
  3:     option ping-timeout 42
  4:     option remote-host gfs01
  5:     option remote-subvolume /glusterfs/fs
  6:     option transport-type socket
  7:     option transport.address-family inet
  8:     option transport.socket.ssl-enabled off
  9:     option transport.tcp-user-timeout 0
 10:     option transport.socket.keepalive-time 20
 11:     option transport.socket.keepalive-interval 2
 12:     option transport.socket.keepalive-count 9
 13:     option send-gids true
 14: end-volume
 15:
 16: volume vol-client-1
 17:     type protocol/client
 18:     option ping-timeout 42
 19:     option remote-host gfs02
 20:     option remote-subvolume /glusterfs/fs
 21:     option transport-type socket
 22:     option transport.address-family inet
 23:     option transport.socket.ssl-enabled off
 24:     option transport.tcp-user-timeout 0
 25:     option transport.socket.keepalive-time 20
 26:     option transport.socket.keepalive-interval 2
 27:     option transport.socket.keepalive-count 9
 28:     option send-gids true
 29: end-volume
...
~~~
4, 19번라인을 보면 ip가아니라 hostname으로 찾는 것을 확인할 수 있다.  

/etc/hosts에서 이름 설정을 해주면 해결!   

----