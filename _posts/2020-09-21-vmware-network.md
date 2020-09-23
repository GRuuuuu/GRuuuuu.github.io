---
title: "Openshift Network를 위한 몇가지 설정"
categories: 
  - OCP
tags:
  - Network
  - Vmware
  - Openshift
  - CentOS
last_modified_at: 2020-09-21T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
(2020.09.21)  

<img src="https://user-images.githubusercontent.com/15958325/93962990-ff65ba00-fd96-11ea-8c4c-179e2d8577e3.PNG" width="800px">  


위 사진과 같은 Openshift 클러스터 구성을 위한 네트워크 설정에 대해서 서술하겠습니다.  

1. **VMware**사용
2. Openshift 클러스터는 **Private Network** 구성 
3. 각 클러스터의 Public 통신은 **Bastion**을 통해 이뤄짐


# 1. VMware에서 2개의 NIC 셋업
vmware에서 vm들을 생성할때에는 필요한 네트워크 어댑터들을 수동으로 생성해서 부여해줘야합니다.   

이 챕터에서는 Public NIC와 Private NIC를 가지고 네트워크 어댑터를 만든 다음,   
bastion노드에 두개의 어댑터를 추가해주겠습니다.  

### 물리적 NIC 확인
제가 사용한 vmware에는 4개의 물리적NIC가 있다는 점과 현재는 두개의 NIC만 VLAN과 연결되어있다는 것을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/93732089-b680fa80-fc0a-11ea-8ee4-3c97e72c480b.png)    
첫 번째는 Private VLAN과 연결된 인터페이스이고  
두 번째는 Public VLAN과 연결된 인터페이스 입니다.  

> 이부분은 GUI상으로 어떻게 연결되어있는지 확인하는 방법을 몰라서, 실제로 네트워크인터페이스를 연결해보고 ping을 날려봐서 확인했습니다.  
>더 좋은 방법을 찾으면 업데이트하겠습니다...  

### 가상 스위치 생성
활성화된 NIC들을 각각의 가상스위치를 생성해 연결해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/93732414-2b086900-fc0c-11ea-8291-05403ec0ab3f.png)  

### 포트그룹 생성
그 다음, vm에서 사용할 포트그룹을 생성해줍니다. (`VM PrivateNetwork`, `VM PublicNetwork`)  
![image](https://user-images.githubusercontent.com/15958325/93732441-4ffcdc00-fc0c-11ea-8c40-473faa87b38a.png)   

### bastion에 어댑터 추가
Bastion vm을 만들 때 생성한 두 개의 네트워크 어댑터를 추가해줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/93735868-6c534580-fc19-11ea-9504-a57540139a18.png" width="800px">   

### bastion 네트워크 설정

* CentOS기준 위치  
    `/etc/sysconfig/network-script`

자동으로 생성된 네트워크 인터페이스인 (ex)ens192와 ens224를 수정  

#### Public Network
![image](https://user-images.githubusercontent.com/15958325/93736183-788bd280-fc1a-11ea-9b20-c7957caa9244.png)  
`BOOTPROTO` : `static`으로 변경  
`ONBOOT` : network시작할때 변경점이 적용되게 `yes`로 변경  
`IPADDR` : 해당 vm에 부여할 ip (연결해줬던 vlan의 subnet범위를 확인)  
`GATEWAY` : 연결한 vlan의 gateway를 확인  
`NETMASK` : "  
`DNS1` : dns1이 자기 자신인 이유는 ocp클러스터의 dns서버가 bastion이기 때문. 만약 dns서버가 다른곳이라면 해당 ip를 적을 것  

#### Private Network

![image](https://user-images.githubusercontent.com/15958325/93736186-7a559600-fc1a-11ea-96ef-eb67a279c120.png)

public과 마찬가지로 `BOOTPROTO`, `ONBOOT`, `IPADDR`, `NETMASK` 설정을 해줍니다.  

`GATEWAY`를 적지 않는 이유는 bastion에서는 public쪽 게이트웨이만 사용할 예정이고 지정된 subnet밖으로 나가지 않을것이기 때문입니다.  

네트워크 재시작:  
~~~sh
$ systemctl restart network
~~~

그리고 bastion의 네트워크를 다시 살펴보면 두개의 네트워크 인터페이스를 포함하고 있다는 것을 확인할 수 있습니다.   
~~~sh
$ ip a
~~~
![image](https://user-images.githubusercontent.com/15958325/93736520-96a60280-fc1b-11ea-9fa0-fa53c105a0e8.png)   


라우터 정보도 보면 default gateway로 public gateway가 설정되어 공인통신을 하는데 문제없습니다.  
~~~sh
$ ip r
~~~

![image](https://user-images.githubusercontent.com/15958325/93736603-d66cea00-fc1b-11ea-9a6c-a7c2e221cc8c.png)  

private gateway가 설정되어있지 않아서 할당된 private vlan밖으로 나갈 순 없지만 openshift클러스터는 할당된 vlan의 subnet 내에서 사용할 것이기 때문에 문제 없습니다.   


# 2. bastion의 gateway설정 (iptables)
ocp 클러스터의 게이트웨이가 되어줄 bastion의 네트워크 설정은 마쳤습니다.  
이제 각 노드에서 나올 네트워크 패킷들을 bastion에서 포워딩해주는 설정을 해주도록 하겠습니다.  

### iptables 규칙 설정
**1. ens로 나가는 패킷 포워딩을 허가**
~~~sh
$ iptables -A FORWARD -o ens192 -j ACCEPT
$ iptables -A FORWARD -o ens224 -j ACCEPT
~~~

**2. ip forward설정**  
~~~sh
$ sysctl -w net.ipv4.ip_forward=1
$ sysctl -a | grep ip_forward
~~~
![image](https://user-images.githubusercontent.com/15958325/93737152-60698280-fc1d-11ea-8640-7e27f56d554e.png)  

**3. MASQUERADE**  
위 단계까지 거치고 나면 LAN상의 시스템들끼리 통신할 수 있습니다.  
그러나 인터넷과 같은 외부 시스템과의 통신은 허용되지 않습니다.  
LAN 상의 시스템이 가상 IP 주소를 가지고 외부 public 네트워크와 통신할 수 있도록 허용하려면, LAN 시스템에서 외부로 향하는 요청이 방화벽 외부 장치(이 예시에서는 ens192)의 IP 주소로 나가도록 방화벽에 IP **masquerading** 기능을 설정해야합니다.
~~~sh
$ iptables -t nat -A POSTROUTING -o ens192 -j MASQUERADE
~~~

### 테스트용 노드 생성

아래와 같이 사설망에 vm을 생성해줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/93739563-8db92f00-fc23-11ea-8dc3-9a552e79ceae.png" width="800px">   

네트워크 설정은 위와 비슷하게 설정해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/93739662-c78a3580-fc23-11ea-909b-a2553c175191.png)   
**GATEWAY**정보는 패킷포워딩을 bastion노드로 보낼 것이므로 bastion노드의 private ip를 기입해줍니다.  

네트워크를 재시작하고나면 다음과 같이 private ip가 할당된 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/93739735-f30d2000-fc23-11ea-90e9-2c60d6febec7.png)  

default gateway도 bastion으로 잘 설정되었습니다.  
![image](https://user-images.githubusercontent.com/15958325/93739830-2ea7ea00-fc24-11ea-82c0-221c1b025242.png)  

원래대로라면 10.x대역의 ip는 공인 ip가 아니기때문에 인터넷 연결이 되지 않아야 하지만, 위의 포워딩 설정을 통해서 bastion을 지나 공인통신이 되는 것을 확인할 수 있습니다.   
![image](https://user-images.githubusercontent.com/15958325/93739855-3ff0f680-fc24-11ea-8914-dd1710989cce.png)   

bastion이 게이트웨이역할을 잘 수행한다는 것을 확인하였으니, 이제 openshift cluster를 구성하시면 됩니다.  

주의하셔야 할 점은, CoreOS를 설치할때 ip파라미터 정도 입니다.    
`static ip`: 할당할 private ip    
`gateway` : bastion private ip  
`netmask` : private subnet의 netmask   


끝!  

----