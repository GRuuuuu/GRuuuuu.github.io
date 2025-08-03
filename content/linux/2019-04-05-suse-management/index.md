---
title: "SUSE Management -YaST, iSCSI"
slug: suse-management
tags:
  - SUSE
  - YaST
  - iSCSI
date: 2019-04-05T13:00:00+09:00
---

## 1. Overview
`SUSE`에서의 `YaST`와 `iSCSI` 설정에 대해 다루도록 하겠습니다.

## 2. Prerequisites

이 문서는 [Install SUSE with HMC](https://gruuuuu.github.io/suse/suse-install/) 이후를 다루고 있습니다.  

## 3. System Management

`VNC Viewer`를 통해 SUSE환경에 접속합시다.  
![image](https://user-images.githubusercontent.com/15958325/55599557-5b97e100-5793-11e9-96ab-9d769de2a2f0.png)  

>터미널은 오른쪽마우스 메뉴를 통해 접근할 수 있습니다.  
>![image](https://user-images.githubusercontent.com/15958325/55599105-1a9ecd00-5791-11e9-8def-a75444f53f6c.png)  


왼쪽 하단의 Application을 눌러 시스템 메뉴를 살펴봅시다.  
![image](https://user-images.githubusercontent.com/15958325/55599695-e24cbe00-5793-11e9-962c-8b7eb1ef5dc4.png)  

시스템을 관리할 수 있는 다양한 메뉴들이 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55599696-e5e04500-5793-11e9-9002-0650c431472d.png)  

메뉴 중, Utilities의 System Monitor를 클릭해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/55599714-027c7d00-5794-11e9-816a-af2b9d0b6df6.png)  

System Monitor항목에서는 현재 시스템에서 돌아가는 프로세서들, 자원, 저장공간의 상태를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55599715-04ded700-5794-11e9-8054-1c01426e1c12.png)   
![image](https://user-images.githubusercontent.com/15958325/55599720-08725e00-5794-11e9-8507-4a9226e32bd9.png)    
![image](https://user-images.githubusercontent.com/15958325/55599782-44a5be80-5794-11e9-9367-e3dedfef717a.png)  

## 4. YaST
### YaST- Yet another Setup Tool
SUSE Linux를 위한 패키지 설치 및 환경 설정 도구. 시스템 관리자가 쉽고 빠르게 시스템 전체를 관리하도록 도와주는 통합 관리자도구입니다.  
크게 Text Mode와 GUI Mode로 나뉩니다.  

### GUI Mode
System Tool -> YaST로 접근

### Text Mode

터미널 열어서 커맨드 입력 (루트권한이 있어야함)
~~~bash
$ yast
~~~

![image](https://user-images.githubusercontent.com/15958325/55607790-04583780-57b8-11e9-8ebe-574949c32d4c.png)  

커맨드를 입력하면 다음과 같이 창이 뜨게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55607865-2b166e00-57b8-11e9-97ff-595663b535ae.png)  

Support > Release Notes로 들어가면 os정보가 뜨게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55607925-51d4a480-57b8-11e9-9a40-7447e6ea9fb8.png)  
![image](https://user-images.githubusercontent.com/15958325/55607930-5436fe80-57b8-11e9-8d4b-8ac4a1e4e742.png)   

### 그외기능
- 온라인업데이트
- sw 설치/제거
- 보조장치 관리
- 시스템 백업/복구
- 네트워크 설정
- 서버 설정
- 방화벽
- 사용자 관리 
- ...  

그냥 명령어 뚱땅뚱땅치는것보다 훨-씬 쉽고 빠르게 작업할 수 있습니다.  
자세한 정보는 [이곳](https://en.opensuse.org/YaST_Software_Management)  

## 5. iSCSI
### iSCSI- Internet Small Computer System Interface
컴퓨팅 환경에서 데이터 스토리지 시설을 이어주는 IP기반의 스토리지 네트워킹입니다. IP망을 통해 데이터 전송, 원거리의 스토리지 관리에 쓰입니다.  
특수한 케이블링을 요구하는 fibre채널과 달리 기존의 네트워크 인프라를 사용해 운영이 가능합니다.   
![image](https://user-images.githubusercontent.com/15958325/55609368-79793c00-57bb-11e9-89bf-4401bc8f1df2.png)  

> <b>LUN</b>   
> 물리적 SCSI 장치("Target"이라고 함)에 속하는 개별적으로 주소 지정이 가능한(논리적) SCSI 장치를 나타냅니다.  
> 
> <b>iSCSI Target</b>  
> iSCSI환경에서는 가상화 방식으로 SCSI하드디스크로의 연결이 구현됩니다. iSCSI Target 은 연결 인터페이스와 유사합니다.  
>
> 따라서 클라이언트에서 iSCSI Target에 연결이 되면, iSCSI Target에 연결된 LUN들은 클라이언트에서 접근할 수 있게 됩니다.

### iSCSI Configuration

먼저 연결할 iSCSI장치의 이름을 제대로 명시해주어야 합니다. 디폴트로 설정되어있는 이름을 바꿔줍시다.  
~~~bash
$ sudo su
$ cd /etc/iscsi/
$ ls
  > ifaces initiatorname.iscsi iscsid.conf
$ vim initiatorname.iscsi
~~~  
![image](https://user-images.githubusercontent.com/15958325/55609570-f2789380-57bb-11e9-8790-2776b86b3822.png)  
밑줄친 부분이 iSCSI Qualified Name(IQN)으로 변경되어야 합니다. (사진은 이미 변경됨)  

이제 YaST에서 설정을 마저 해줄겁니다. Text모드이던 GUI모드이건 YaST를 실행시킵시다.  
저는 GUI모드에서 진행해보겠습니다.  

Network Services > iSCSI Initiator  
![image](https://user-images.githubusercontent.com/15958325/55609852-a7ab4b80-57bc-11e9-8596-262589726127.png)  

Discovered Targets > Discovery  
![image](https://user-images.githubusercontent.com/15958325/55609896-bdb90c00-57bc-11e9-9792-661ffeed6503.png)  

접근하고자하는 iSCSI의 주소와 포트정보를 기입  
![image](https://user-images.githubusercontent.com/15958325/55609959-ed681400-57bc-11e9-83fc-d726eb34615a.png)  
![image](https://user-images.githubusercontent.com/15958325/55609965-ef31d780-57bc-11e9-9219-9d9ad6e62ed3.png)  

Connected Targets > Add 
![image](https://user-images.githubusercontent.com/15958325/55610083-2902de00-57bd-11e9-8fd2-42b26bfb33c5.png)  
그다음 Next > Connect   
 
automatic을 고릅니다.  
![image](https://user-images.githubusercontent.com/15958325/55610102-2f915580-57bd-11e9-8a9b-0465751e3658.png)  

제대로 따라오셨다면 다음과 같은 화면을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55610238-7a12d200-57bd-11e9-8edb-c3bad5fee761.png)  

이제 SUSE 터미널로 돌아와서 다음 커맨드를 입력합니다.  
기존에 정의했던 iSCSI정보로 세션을 시작시킬것입니다.  
~~~bash
$ iscsiadm -m session -P 3
~~~
![image](https://user-images.githubusercontent.com/15958325/55610276-8f87fc00-57bd-11e9-93b9-1ab080cb5403.png)  

정상적으로 SCSI디스크가 붙은것을확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55610290-94e54680-57bd-11e9-9c22-f69ebac2113a.png)  

다음 명령어를 통해 iSCSI디스크가 어떤 path로 접근할 수 있는지 확인할 수 있습니다.  
~~~bash
$ ls -al /dev/disk/by-path
~~~  
![image](https://user-images.githubusercontent.com/15958325/55611131-9c0d5400-57bf-11e9-9599-ebfa3bf46796.png)  

sdt에서 SCSI디스크 정보를 확인할 수 있습니다.  
~~~bash
$ lscfg -vl sdt
~~~
![image](https://user-images.githubusercontent.com/15958325/55611419-67e66300-57c0-11e9-847c-4c204de2726f.png)  

iSCSI 설정 완료!

----