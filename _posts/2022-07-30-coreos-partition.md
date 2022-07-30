---
title: "CoreOS partition잡고 설치하기"
categories:
  - OCP
tags:
  - Kubernetes
  - Openshift
  - CoreOS
  - Storage
last_modified_at: 2022-07-30T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview
일반적으로는 크게 쓸 일이 없을지도 모르지만, 내부의 디스크를 파티션을 나눠서 설치해야 할 일이 생길수도 있습니다.  
저같은 경우는 OpenShift의 `DataFoundation`기능을 사용하기 위해서 worker노드의 파티션을 나눌 필요가 있었습니다.  

`DataFoundation`도 NFS나 별도의 스토리지가 없는 환경에서 사용하기 좋은 Software Defined Storage이니 나중에 기회가 되면 다뤄보도록 하겠습니다.  

## 1. 일단은 CoreOS 설치
일단 설치합니다. -> [설치 참고](https://gruuuuu.github.io/ocp/ocp4.7-restricted/#32-coreos-%EC%84%A4%EC%B9%98)  

설치 파라미터를 넣기 전까지 진행해주세요. (그냥 CoreOS부팅)  

>기존에 클러스터로 사용하던 노드는 아예 재설치를 진행해야합니다.  

## 2. fdisk로 partitioning하기  
다음으로 partitioning을 진행합니다.  

![image](https://user-images.githubusercontent.com/15958325/181913714-811b49cb-ef40-4d88-8e60-d058ff86c28c.png)  

목표는 nvme0n1p4파티션을 120GB짜리 4번파티션과 800GB짜리 5번 파티션으로 나누는 것!  

4번 삭제: 
![image](https://user-images.githubusercontent.com/15958325/181913755-c14177f5-ee9d-4e9e-95c1-583fa4a16dbc.png)    

새로 120GB짜리 4번 파티션 생성
![image](https://user-images.githubusercontent.com/15958325/181913794-0ce4eaa4-29f4-4319-9b77-29180d25a1b7.png)  
![image](https://user-images.githubusercontent.com/15958325/181913808-c2ee4666-edcf-4890-8b64-a2a0e170cc34.png)   

5번파티션 생성하고 파티션 변경사항 저장  
![image](https://user-images.githubusercontent.com/15958325/181913858-c07f9f55-7653-4820-9d95-12198c9bc94c.png)  


lsblk로 확인해보면 제대로 4번과 5번이 생성된 것을 확인 가능  
![image](https://user-images.githubusercontent.com/15958325/181913882-0df92751-a608-4f42-af30-d7c843db2291.png)  

## 3. 설치파라미터
이제 (재)설치를 진행하기 위해 설치파라미터를 넣어줍니다.  

공식문서에서 제공하는 기존의 파라미터는 동일하게 가져가되,  
~~~
$ sudo coreos-installer install --copy-network --ignition-url=http://{FILE_SERVER}:8080/bootstrap.ign --insecure-ignition /dev/sda
~~~

마지막에 `--save-partindex`옵션을 추가시켜줍니다.  
설치진행할때 파티션 변동사항을 그대로 가져가는 옵션입니다.  

위에서 새로 5번파티션을 만들었으니, `--save-partindex 5`라고 붙여주면 됩니다.  

설치를 마무리하고 클러스터join까지 마치고나서 확인해보면 제대로 5번파티션이 남아있는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/181914115-6a07371c-049d-402f-8480-edbcd52cc4e9.png)  

----