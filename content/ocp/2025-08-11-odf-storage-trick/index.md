---
title: "ODF Storage trick"
tags:
  - Kubernetes
  - Openshift
  - Ceph
  - Rook
date: 2025-08-11T13:00:00+09:00
---

## Overview
언제부턴가 ODF(Openshift Data Foundation)를 구성할 때 강제로 `SSD/NVMe` 디스크를 사용하게 바뀌었습니다.  
즉 `HDD`를 사용하는 장비의 경우 조건이 맞지 않아서 ODF용 디스크로 사용할 수 없게된다는 뜻입니다.  

근데 성능 포기하고 기능만 체크하고 싶은데 `HDD`만 있다면 난감한 상황이 발생할 것입니다...   

이번 포스팅에서는 workaround로 HDD를 SSD처럼 보이게 만들어주는 방법에 대해서 작성하겠습니다.  

### No SSD/NVMe Disks detected
HDD를 사용중이라면 아래와 같이 ODF용 디스크로 사용할 수 없다고 에러가 발생하게 됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2025/2025-08-11-odf-storage-trick.md/1.png)  

이 체크를 어떻게 하느냐~  
디스크의 **ROTA**정보를 읽어서 이 디스크가 SSD인지 HDD인지 파악하게 됩니다.  
~~~
[core@worker03 ~]$ lsblk -o "NAME,MAJ:MIN,RM,SIZE,RO,TYPE,ROTA" |grep vd[bc]
vdb    252:16   0     6T  0 disk    1
~~~

`ROTA`는 **ROTAtional device**의 약칭으로, 디스크가 물리적으로 회전(rotating)하는지 여부를 나타냅니다.  
`HDD`는 플래터가 물리적으로 회전하면서 데이터를 읽고 쓰기 때문에 **ROTA가 1**이고,  
`SSD/NVMe`는 반도체 기반 저장장치로 물리적으로 회전하지 않기 때문에 **ROTA가 0**입니다.  

이제 우리가 해줄 일은 HDD가 붙어있는 노드의 udev정보를 ROTA 1->0 으로 덮어씌워줄겁니다.  

### machineconfig 작성하기

~~~yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: worker-udev-configuration
spec:
  config:
    ignition:
      config: {}
      security:
        tls: {}
      timeouts: {}
      version: 2.2.0
    networkd: {}
    passwd: {}
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,QUNUSU9OPT0iYWRkfGNoYW5nZSIsIFNVQlNZU1RFTT09ImJsb2NrIiwgS0VSTkVMPT0idmRbYi16XSIsICBBVFRSe3F1ZXVlL3JvdGF0aW9uYWx9PSIwIgo=
          verification: {}
        filesystem: root
        mode: 420
        path: /etc/udev/rules.d/99-ibm.rules
  osImageURL: ""
~~~

각 coreos노드에 적용해 줄 것이기 때문에 MachineConfig로 정의해주겠습니다.  
content의 source에는 아래와 같은 내용이 base64로 인코딩 되어있습니다.  
~~~
ACTION=="add|change", SUBSYSTEM=="block", KERNEL=="vd[b-z]",  ATTR{queue/rotational}="0"
~~~
> 만약 바꾸고자 하는 disk의 이름이 vd~로 시작하지 않는다면 KERNEL의 변수를 바꿔주고 base64로 다시 인코딩 해주면 됩니다.  

배포!  
~~~
# oc apply -f storagetrick.yaml
machineconfig.machineconfiguration.openshift.io/worker-udev-configuration created

# oc get mc |grep udev
worker-udev-configuration                                                                                2.2.0             50s
~~~

잠시 기다리고, 적용된 노드로 들어가서 확인해보면 아래와 같이 ROTA가 0으로 바뀐 것을 확인할 수 있습니다.  
~~~
[core@worker01 ~]$ lsblk -o "NAME,MAJ:MIN,RM,SIZE,RO,TYPE,ROTA" |grep vd[bc]
vdb    252:16   0     6T  0 disk    0
~~~

ODF작성 페이지로 넘어가보면 에러가 사라진 것도 확인할 수 있습니다!  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2025/2025-08-11-odf-storage-trick.md/2.png)   

{{< alert icon="fire" cardColor="#e63946" iconColor="#1d3557" textColor="#f1faee" >}}
반드시 테스트 목적으로만 사용해주세요!
{{< /alert >}}

