---
title: "베어메탈2개와 IP2개로 OCP Cluster 만들어보기(feat.VXLAN)"
tags:
  - Openshift
  - Network
date: 2026-01-31T13:00:00+09:00
---

## Overview
때론 가혹한 환경에서 어떻게든 몸을 비틀어야할 때가 있습니다.  
절대적인 물리 리소스가 부족할 수도 있고, ip를 더 할당해달라고 말하기 눈치가 보이는 상황일 수도 있죠.  

이번 포스팅은 베어메탈 2개와, 외부에서 접근 가능한 ip 단 2개를 가지고 Openshift 클러스터를 만들어보려했던 저의 삽질기를 적어보려 합니다.  

## 고려사항
이 글에 관심이 있어 들어오신 분들은 모두 Openshift가 어떤 녀석인지 아실겁니다.  
Kubernetes기반으로 RedHat이 만든 Enterprise용 Container Orchestration Platform이죠.  

노드의 구성이 자유로운 Kubernetes에 비해서 Openshift는 꽤나 구성이 엄격합니다. 기본 Master3대, Worker3대로 클러스터가 구성이 되죠.  

>노드 하나로만 구성되는 SNO(Single Node Openshift)가 있기는 하지만 베어메탈 2대를 모두 사용해야하는 저의 목적에는 맞지 않았기에 고려사항에서 제외했습니다.  


## 첫번째 시도: Proxy사용해보기
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/1.png)
제가 갖고 있는 것은 물리서버2대와, 외부에서 호출가능한 public ip 2개뿐...   
이것들을 사용해서 Master 3대와 Worker 3대를 VM으로 만들어 서로를 호출할 수 있게 해야합니다.  
그러나 VM은 자신에게 할당된 가상 네트워크의 ip만을 가지고 있고 그 밖으로는 나갈수가 없습니다.  
어떻게 해야 다른 물리 서버에 도달할 수 있을까요?  

가장 먼저 생각이 들었던 것은, VM 네트워크를 **Bridge**모드로 생성(NAT는 vm간의 통신이 불가능하기 때문)하고, 호스트 네트워크를 통해 **Packet Forwarding**, **IP Masquerade**를 하는 방법이었습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/2.png)  

이를 통해, VM이 Host1를 통해 다른 Host2에 도달할 수 있게됩니다.  
그러나 Host2에 도달했더라도 내부 VM까지는 들어갈 수가 없습니다. 패킷의 destination은 Host2의 ip이기 때문입니다.  

그래서 각 Host에 LB(Proxy)를 두는 방법을 생각했습니다.  
Openshift는 특정 포트들이 갖는 역할들이 있어 원래도 앞단에 LB를 뒀었습니다.  
예를 들면 :    
- 80(`http`), 443(`https`) -> worker pool
- 6443(`api`), 22623(`mc`) -> master pool  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/3.png)  

Kubernetes는 기본적으로 ip통신이 아닌 http통신을 하기 때문에 이걸로 충분할거라 생각했습니다.  

>시나리오 하나를 예시로 들면,    
>1. master0에서 etcd heartbeat든 무언가를 위해 master2를 호출한다고 가정      
>2. 등록된 DNS에 따라 master2 노드의 ip, 즉 Baremetal 2의 ip를 resolving
>3. 그럼 source가 master0(`12.12.139.10`)이고 destination이 Baremetal 2(`192.168.0.24:22623`)인 패킷이 생성  
>4. Packet Forwarding과 Masquerade 설정에 의해 source가 baremetal 1(`192.168.0.23`)이 되어 route를 타고 baremetal 2로 도착 
>5. baremetal 2에 도착한 패킷은 포트가 `22623`이라 LB설정에 의해 master1과 2중 하나에 패킷을 보내게 됨  

### 문제 발생
어쨌든 생각했던대로 Openshift 설치는 잘 되어가는 것처럼 보였으나... 설치 도중 특정 pod들이 http통신이 아닌 pod의 ip로 통신을 시도하는 것을 발견했습니다.  

destination이 baremetal 2의 ip여서 loadbalancing을 통해 아무 노드에 들어가기만 하면 되는것이아니라, 특정 노드의 ip를 직접 호출하기 때문에 패킷이 제대로 원하는 노드에 가지 못하고 있었죠.  

## 두번째 시도 : VXLAN
직접 Master0(Baremetal 1) -> Master2(Baremetal 2)의 ip를 호출할 수 있게, 즉 한 vm에서 다른 호스트에 있는 vm을 직접 호출할 수 있게 만들어줘야 했습니다.  

그래서 생각한 두번째 방법이 바로 VXLAN을 이용해 L2터널을 만들어주자! 였습니다.  

### VXLAN이란?
**VXLAN(Virtual eXtensible Local Area Network)** 는 UDP 프로토콜을 사용해 장치가 L3네트워크로 분리가 되어있더라도 동일한 L2네트워크에서 통신할 수 있도록 만들어주는 기술입니다.  
즉, 기존 네트워크 망이 어떻게 구성되어있던지, IP기반 물리 Network를 넘어 통신할 수 있게 만드는 **Network Overlay**기술 중 하나입니다.    

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/4.png)  

위 그림을 보면 VM이 원래 보내려던 L2패킷이 있고, 그것을 UDP로 감싸고 있는 캡슐형태를 보실 수 있습니다.  
- **Outer Header** : 물리 네트워크에서 라우팅하기 위한 정보
- **UDP Header** : Inner 패킷의 해시값+ VXLAN포트(4789고정- 수신측에서 VXLAN이라는 것을 알게함)
- **VXLAN Header** : VNI(VXLAN Network Identifier)정보가 있음, 같은 id값의 VXLAN끼리만 통신가능

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/5.png)  

패킷이 전달되는 흐름을 보겠습니다.  
1. Master0(12.12.139.10)에서 Master2(12.12.139.12)로 가는 패킷 생성
2. Baremetal 1의 VTEP(VXLAN Tunnel End-Point)에서 패킷을 가로챔 -> destination이 원격노드에 있음을 인지
3. VTEP에서 패킷을 캡슐화
~~~
Outer IP Src = Baremetal 1 IP
Outer IP Dst = Baremetal 2 IP
UDP dst port = 4789
VNI = 10010
~~~
4. 물리 네트워크를 통해 Baremetal 2로 전달
5. Baremetal 2의 VTEP이 캡슐을 받아 VXLAN헤더를 제거하고 내부 L2프레임을 복원시킴
6. Master2로 패킷 전달!

> **VTEP(VXLAN Tunnel End-Point) 이란?**  
>VXLAN segment와 tenant 장비들을 매핑하고, 캡슐화&캡슐해제 역할을 수행


### VXLAN 네트워크 구성하기
그럼 이제 실제 VXLAN 네트워크를 구성해보겠습니다.  

VM의 네트워크로 Bridge네트워크(`br-vm`)를 구성해주고, VXLAN을 생성해줍니다.  

**Baremetal 1 :**  
~~~
# ip link add vxlan0 type vxlan id 39 dev ens34f0 remote 192.168.0.24 dstport 4789
# ip link set vxlan0 master br0
# ip link set vxlan0 up
~~~

**Baremetal 2:**  
~~~
# ip link add vxlan0 type vxlan id 39 dev ens34f0 remote 192.168.0.23 dstport 4789
# ip link set vxlan0 master br0
# ip link set vxlan0 up
~~~
`id` : VNI (두 개의 장치가 동일한 id를 갖고 있어야 함)  
`ens34f0` : underlay NIC  
`remote` : 터널연결할 상대장치의 ip  

만약 값을 수정하려면 삭제하고 다시만들면 됩니다.  
~~~
# ip link set vxlan0 down
# ip link del vxlan0
~~~

> 현재 구성은 두 개의 장치를 가지고 vxlan 네트워크를 구성하는 방법을 설명하고 있습니다.  
>장치가 세개 이상이면 `remote`를 사용하지 못하고 다른 방법으로 구성하여야 합니다.  

다음으로 `rp_filter`를 비활성화 시켜주겠습니다.  

`rp_filter`는 reverse path filtering에 대한 설정입니다.   
패킷이 도착한 인터페이스와 실제 라우팅 경로가 일치하는지 검사하여 보안을 강화하고 잘못된 경로로 들어오는 패킷을 차단하는 기능인데, 여기서는 패킷 드랍을 방지하기 위해 0으로 비활성화 시키겠습니다.  
~~~
# cat <<EOF >/etc/sysctl.d/98-rpfilter.conf
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
net.ipv4.conf.ens34f0.rp_filter=0
net.ipv4.conf.br-vm.rp_filter=0
net.ipv4.conf.vxlan0.rp_filter=0
EOF

# sysctl --system
~~~

여기까지 했다면 VXLAN네트워크 구성은 끝입니다. 이제 VM들끼리는 통신이 가능하지만,  
추가로 패킷이 public으로 나가야 한다면 NAT설정이 필요한데요.(폐쇄망이 아닌 경우..)   

먼저 MASQUERADE설정을 해줍니다.  
~~~
# iptables -t nat -A POSTROUTING \
  -s 12.12.139.0/24 \
  -o ens34f0 \
  -j MASQUERADE
~~~
`-t nat -A POSTROUTING` : Route 결정 이후   
`-s 12.12.139.0/24` : source ip가 12.12.139.0/24인 경우  
`-o ens34f0` : 패킷이 ens34f0으로 나갈때만 적용  
`-j MASQUERADE` : SNAT, 패킷의 출발지(source) 주소를 변경  

마지막으로 포워딩 규칙을 정의하면 됩니다.  
~~~
# iptables -A FORWARD -i br-vm -o ens34f0 -j ACCEPT
# iptables -A FORWARD -i ens34f0 -o br-vm -m state --state RELATED,ESTABLISHED -j ACCEPT
# sysctl net.ipv4.ip_forward=1
~~~

`-i` : 입력 인터페이스   
`-o` : 출력 인터페이스   
`-m state --state RELATED,ESTABLISHED` : 이미 존재하는 연결에 속한 패킷만 허용함  
`-j ACCEPT` : 조건 만족 시 허용  

그래서 규칙을 정리하면,  
- `br-vm`에서 들어와 `ens34f0`로 나가는 연결은 모두 허용
- `ens34f0`에서 들어와 `br-vm`으로 돌아오는 응답 트래픽은 기존 연결에 한해서만 허용   

내부->외부 는 자유롭게 가능하지만 외부->내부는 응답만 허용한다는 규칙입니다.   

### 문제 발생
VXLAN으로 vm들끼리 직접 통신은 가능해졌지만, 새로운 문제가 생겼습니다.  
바로... MTU값 불일치로 tls handshake timeout이 발생한다는 것인데요.  
정말미치고팔짝뛸뻔했지만, 차분히 들여다 보겠습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-31-ocp-vxlan.md/6.png)  

아마 vm간의 통신이면 잘 되었겠지만, 문제는 우리가 설치하고 있는게 Openshift라는 것입니다.  
Openshift의 네트워크구조를 보면, 이녀석도 VXLAN같은 오버레이 네트워크위에서 pod들이 동작하고있습니다.(Default는 `OVN-Kubernetes`)  
생각해보면 pod들의 ip가 물리네트워크랑 다른것도 그렇고, 통신할때 물리 네트워크신경안쓰는걸 보면 당연한건데 말이죠.  

하여튼 문제는 여기서 발생합니다. Overlay Network들은 기존 패킷에 추가 정보를 더해 캡슐화를 하기때문에 물리 네트워크의 MTU한계 안에 넣으려면 원래 패킷을 줄일 수 밖에 없습니다.  

여기서 **MTU**는 Maximum Transmission Unit으로, 한번에 보낼 수 있는 프레임의 최대 크기를 의미합니다.  

실제 물리장치의 이더넷 MTU값이 1500이라고 해 봅시다.  
이 안에 모든 헤더와 데이터가 들어가야 합니다. 그래서 기존패킷 + 최소50byte가 필요하게 되죠.  
그래서 Overlay Network위에 있는 VM들의 패킷은 1450이상이 넘으면 안됩니다..!  

Overlay Network위 VM들의 MTU를 줄이지 않으면 작은 패킷인 ping은 갈테지만 대용량 패킷을 날려야하는 tls handshake같은 연결은 timeout이 발생하게 되는것이죠.  

하지만 우리의 구성은 무려 Overlay Network가 두개... Timeout이 발생하는건 어찌보면 당연한 현상입니다.  

## 세번째 시도 : MTU줄이기
이 문제는 간단하게 고칠 수 있었습니다.  

물리장비의 MTU값을 확인하고,  
VM만들때 메인 NIC의 MTU를 100 줄여서 세팅해주고 Openshift를 설치했습니다.  

그러면 Openshift설치할때 OVN이 올라가면서 알아서 MTU를 100 줄여서 OVN네트워크를 구성해주게됩니다.  

설치 완료~  

>**주의!!!!**  
>해당 구성은 반드시 테스트용도, 제한적 환경에서만 시도하세요!

---

