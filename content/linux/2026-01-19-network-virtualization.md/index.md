---
title: "호다닥 톺아보는 네트워크 가상화(feat. DPDK, SR-IOV)"
slug: network-virtualization
tags:
  - Linux
  - Network
date: 2026-01-19T13:00:00+09:00
---

## Overview
이번 포스팅에서는 어렵지만!! 한번쯤은 이해하고 넘어가야 할 네트워크 가상화에 대해서 자세히 알아보도록 하겠습니다

## 기본 네트워크
네트워크 가상화에 대해서 알아보기 이전에, 가상화하지 않은 네트워크는 어떤식으로 동작하는지 간단히 살펴보겠습니다.  

매우 간단합니다! 외부 패킷을 받아서 서버로 전달해주는 스위치, 스위치로부터 패킷을 받아서 커널로 넘겨주는 NIC(Network Interface Controller)을 통해서 서버는 네트워크 통신을 할 수 있게 됩니다.   
~~~
Internet - Physical Switch - Physical NIC - Host OS
~~~

리눅스는 메모리공간을 사용자영역(User Space)과 커널영역(Kernel Space)로 구분합니다. 두 공간을 엄격하게 분리하여 한 쪽에서 생기는 문제가 다른 공간에 영향을 주지 않게 하기 위해서 입니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-19-network-virtualization.md/1.png)

그래서 **사용자영역** 에는 Process나 Application같은 사용자 레벨의 프로그램이 실행되는 영역이고,  
**커널영역** 은 시스템의 모든 핵심 기능과 하드웨어 제어를 담당하는 코어 영역이라고 보시면 됩니다.  

만약 CPU가 사용자레벨의 작업을 처리할 경우엔 user space에서 작업을 하다가, 커널 레벨의 권한이 필요한 작업이 필요한 경우엔 User Space -> Kernel Space로 변경을 하게 되는데, 이를 **Context Switch** 라고 부릅니다.  

**Context Switching** 은 시스템의 안정성이나 보안을 유지하는데에는 중요하지만 성능에 있어 **오버헤드** 를 초래할 수도 있는데요.  

바로 이 Context Switching을 일으키는 여러 작업중 하나가 Network packet처리입니다.   

## 가상 네트워크
그러면 이제 KVM에서 네트워크를 처리하는 방식에 대해서 살펴보겠습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-19-network-virtualization.md/2.png)

libvirt는 VM이 시작될 때, TAP 인터페이스를 생성합니다. 이를 Bridge에 붙이고 VM의 가상 NIC의 backend로 연결해 사용하게 됩니다.  

### TAP(Terminal Access Point)/TUN(Tunnel) 이란?
이름에서 알 수 있듯이, TAP과 TUN모두 터널링 목적으로 사용됩니다.    
소프트웨어적으로 구현된 가상 네트워크장치를 제어하는 가상의 네트워크 드라이버라고 보면 되는데요.  
TAP/TUN으로 전달된 패킷들은 TAP/TUN에 연결된 사용자공간(ex. VNIC)으로 전달되고,   
반대는 사용자공간에서 TAP/TUN으로 전달되고 OS네트워크 스택으로 전달됩니다.  

**TAP(Terminal Access Point)**
- L2계층
- 이더넷

**TUN(Tunnel)**
- L3계층
- ip

실제로 KVM을 사용하고 있는 호스트의 네트워크를 확인해보면 :  
~~~
# ip a

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master virbr0 state UP group default qlen 1000
    link/ether d8:bb:c1:74:e6:5a brd ff:ff:ff:ff:ff:ff
3: virbr0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether d8:bb:c1:74:e6:5a brd ff:ff:ff:ff:ff:ff
    inet 10.10.12.10/24 brd 10.10.12.255 scope global noprefixroute virbr0
       valid_lft forever preferred_lft forever
4: vnet0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master virbr0 state UNKNOWN group default qlen 1000
    link/ether fe:54:00:5f:b0:c0 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::fc54:ff:fe5f:b0c0/64 scope link
       valid_lft forever preferred_lft forever
~~~
실제 물리NIC인 `enp3s0`이 보이고, VM들을 위한 가상의 bridge네트워크(`virbr0`)를 확인할 수 있습니다.  
그리고 각 VM의 VNIC과 1대1 매핑이 되는 TAP장치(`vnet0`)도 확인할 수 있습니다.  

리눅스에서 TAP인터페이스는 TUN드라이버로 동작하기 때문에 driver는 `tun`으로 보이지만,  
네트워크 인터페이스가 시스템 버스에 연결된 위치정보를 나타내는 `bus-info`에서는 `tap`장치로 보입니다.  
~~~
# ethtool -i vnet0

driver: tun
version: 1.6
firmware-version:
expansion-rom-version:
bus-info: tap
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
~~~

실제 물리 NIC와 비교해보면, 물리NIC에서는 `bus-info`가 pci주소로 보입니다.  
~~~
# ethtool -i enp3s0

driver: r8169
version: 5.14.0-162.6.1.el9_1.x86_64
firmware-version: rtl8125b-2_0.0.2 07/13/20
expansion-rom-version:
bus-info: 0000:03:00.0
supports-statistics: yes
supports-test: no
supports-eeprom-access: no
supports-register-dump: yes
supports-priv-flags: no
~~~

그러면 이제 가상머신의 네트워크가 어떤식으로 동작하는지 감이 오셨을 겁니다.  
기존 베어메탈에서의 흐름을 기저에 깔고 Bridge-TAP-VNIC의 단계가 추가되었습니다.   

Internet - Physical Switch - Physical NIC - Host OS - **Linux Bridge (또는 OVS) - TAP - QEMU/KVM - virtual NIC** - VM OS  

### CPU Overhead
네트워크 패킷은 다수의 소프트웨어 스택을 통해 VM으로 전달되게 되고, 이로인해 CPU Overhead, 지연, 변동성 등이 발생하게 됩니다.  

- bridge, iptables, conntrack등의 처리에 CPU가 사용됨
- Context Switch (User space - Kernel space)
- QEMU - Kernel - Guest 간의 데이터 복사
- 패킷 도착 시, CPU interrupt 발생

위의 현상은 가상화와 무관하게 리눅스 네트워크 스택의 구조적 문제이지만, 가상화를 함으로써 소프트웨어 스택이 복잡해지고 이로인해 문제점들이 베어메탈보다 부각된다고 보시면 됩니다.  

여튼 이런 오버헤드를 해결하고 최신 고속 네트워크의 요구사항을 충족시키기 위해 몇가지 기술이 개발되었는데요!  

## DPDK(Data Plane Development Kit)

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-19-network-virtualization.md/3.png)  

Network Interface Controller(NIC)들의 처리속도가 급격하게 증가하는데에 비해 운영체제에서의 패킷 처리 속도는 그 속도를 따라가지 못하는 상황이 발생하고,  
이를 극복하고자 기존 운영체제의 패킷 처리 방식을 바꾸고자 하는 것이 DPDK의 목적입니다.  

Kernel Space에서 이뤄지던 패킷프로세싱을 User Space에서 처리하게 하여 CPU overhead를 크게 줄인 것이 특징입니다.  
DPDK를 사용하면 OS의 도움 없이 사용자 Application이 직접 하드웨어를 독점적으로 제어할 수 있게되는데,  
즉 **커널을 우회(Kernel Bypass)해서 처리량을 높이고 레이턴시를 줄일 수 있게 됩니다.**  

그러나 커널을 우회하기때문에 NIC에서 받은 모든 이더넷 프레임들을 유저 Application이 처리해야하는 복잡성이 있어   
초당 수백~수천만개의 패킷을 처리해야하는, 극한의 성능을 요구하는 라우터나 스위치, 네트워크 모니터링 시스템 등을 소프트웨어로 구현할때 많이 사용됩니다.  

### DPDK기반 가상화 네트워크
이제 가상화 영역으로 넘어와서 생각해봅시다.  

위의 가상 네트워크 흐름을 간략화시키면 :  
~~~
NIC
 ↓
Host kernel net stack
 ↓
TAP (vnetX)
 ↓
QEMU / KVM
 ↓
Guest kernel net stack
 ↓
Guest user app
~~~

네트워크 패킷이 유저 APP까지 도달하기 위해 두번의 커널 스택을 지나야하고, 이는 Context Switch와 Copy, Interrupt가 다중으로 발생한다는 것을 의미합니다.  

DPDK는 Kernel networking stack을 우회하고 Kernel Copy를 제거(zero-copy)하지만, 가상화 환경에서 vSwitch/virtio 기반으로 사용할 경우 메모리간 복사가 여전히 필요하고 이는 CPU overhead의 원인이 될 수 있습니다.  

**DPDK를 가상화 중간계층으로 사용한다면 :**  
~~~
NIC
 ↓ DMA
Host DPDK
 ↓ copy!!!
Guest virtio-net (Guest Memory)
 ↓
Guest kernel net stack
 ↓ copy (Guest에서도 DPDK쓰면 copy안함)
Guest user app
~~~

이런식으로 Host kernel net stack을 우회하여 직접 **Guest Memory에 패킷데이터를 복사**하게 됩니다.   
물리 NIC은 Guest memory와 서로 다른 공간에 존재하고 있기 때문에 직접 DMA할 수 없습니다.  
그래서 Host에서 DPDK를 쓰게 되어도 Guest쪽으로 데이터를 넘기려면 메모리 복사가 필요한 것이죠.   

## SR-IOV(Single Root I/O Virtualization)

SR-IOV는 다수의 가상머신이 하나의 I/O PCIe장치를 공유해 마치 직접 NIC에 연결된 것처럼 동작하게 해 서버의 I/O성능을 향상시키는 기술입니다.  

**PF(Physical Function)** : 물리 PCIe 장치  
**VF(Virtual Function)** : 가상 PCIe 장치, 생성할 수 있는 VF의 개수는 PF의 spec에 따름

여러개의 VF가 하나의 PF 위에서 동작하기 위해 내부적으로 큐를 사용해 요청을 제어하는데, 하나의 큐를 사용한다면 Single Root(SR)이고 다수의 큐면 MR-IOV(Multi Root IOV)라고 부릅니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-19-network-virtualization.md/4.png)  
>이미지 출처 : [SR-IOV, PCI Passthrough, and OVS-DPDK](https://study-ccnp.com/sr-iov-pci-passthrough-ovs-dpdk/)  

위에서 언급했듯이, 일반적인 가상화 시스템에서 물리 NIC과 연결되어 통신하기 위해서는 여러 레이어를 통해야합니다.    

DPDK를 사용한다 쳐도, Host에서 Guest로의 메모리 복사가 필요하기 때문에 그만큼의 오버헤드가 존재하지만,  
SR-IOV를 사용해 VF를 직접 VM에 연결한다면, **NIC이 VM에 직접 할당**되어 NIC에서 VM의 memory에 **DMA**를 할 수 있게됩니다.  

PCIe장치가 직접 메모리에 액세스(DMA)하는게 위험하지 않나? 싶을 수 있지만 이것을 안전하게 가능하게 하는것이 바로 IOMMU입니다.  
참고 -> [MMU(Memory Management Unit) & IOMMU(Input Output Memory Management Unit)](https://gruuuuu.hololy.org/linux/kvm-gpu-passthrough/#mmumemory-management-unit--iommuinput-output-memory-management-unit)   

VF마다 접근 가능한 address만 매핑하여 다른 VM이나 Host메모리는 접근을 불가하게 만드는 것이죠! 그래서 안전하게 DMA를 할 수 있습니다.  

### vs PCI Passthrough
참고 : [PCI Passthrough](https://gruuuuu.hololy.org/linux/kvm-gpu-passthrough/#pci-passthrough)  

PCI Passthrough도 Host를 통하지 않고 vm에 직접 PCI장치를 할당하는 기능이죠.  
SR-IOV와 얼핏 보면 비슷한 느낌입니다.  
**만약 SR-IOV의 VF가 1개라면 PCI Passthrough와 동일한걸까요?**  

정답은 아닙니다.  

PCI Passthrough는 PCI의 전체 기능을 **통째로 Guest에 넘기는** 기술입니다. 그래서 Host는 Passthrough된 장치에 대해서는 제어하거나 관리할 수 없습니다.  

반면에 SR-IOV는 Host가 PF를 그대로 보유함과 동시에 **VF만 Guest에 전달**합니다. 여전히 Host는 PCI장치에 대한 제어를 할 수 있죠.  

정리하면 VF는 가상화 계층 안에서 할당된 논리포트이고, PF는 여전히 존재하며 Host에서 관리합니다. 반면 PCI Passthrough는 장치 전체를 게스트가 통째로 통제하죠.  

----