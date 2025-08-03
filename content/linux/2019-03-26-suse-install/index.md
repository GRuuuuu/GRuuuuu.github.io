---
title: "Install SUSE with HMC"
slug: suse-install
tags:
  - SUSE
  - VIOS
  - HMC
date: 2019-03-26T13:00:00+09:00
---

## 1. Overview
이번 문서에서는 SUSE를 Lpar에 HMC를 통해 배포해볼것입니다. 전체적인 flow는 다음과 같습니다.  

![image](https://user-images.githubusercontent.com/15958325/54994383-776aec80-5007-11e9-828e-69c12fae43cd.png)

><b>HMC?</b>  
>Hardware Management Console. 하나 이상의 관리 시스템을 구성하고 제어하기 위해 사용할 수 있는 하드웨어 어플라이언스.  
>![image](https://user-images.githubusercontent.com/15958325/55077274-aaca7b80-50da-11e9-849b-905f56fb875f.png)  

> <b>VIOS?</b>  
> Virtual I/O Server. 다른 파티션들에게 I/O자원을 공급하는 역할을 한다. 가상 I/O서버는 물리적 자원을 소유하면서 다른 파티션들에게 I/O자원의 공유를 허가해준다.  
>특정 OS위에 올라가게 되면 타 App, Service가 같이 올라갈수 없음!

><b>Lpar?</b>  
>Logical partition. 자원을 분할하여 각 자원셋이 독립적으로 동작할 수 있게 하는 것. 쉽게 얘기해서 vm. (이름만 다름)

## 2. Prerequisites

여러개의 Lpar를 하나의 HMC를 통해서 환경을 구성해볼것입니다. HMC를 ssh로 접속해서 사용할 것이므로, putty나 mobaXterm과 같은 터미널툴을 세팅해 둡시다.

> 이 문서에서는 HMC, VIOS, Lpar에 대한 구성은 <b>다루고 있지 않습니다.</b>  

Lpar에 GUI로 접속하기 위해 VNC Viewer를 사용할 것!  
>VNC Viewer: 원격으로 다른곳에 있는 서버에 접속해서 사용가능  
>link- [https://www.realvnc.com/en/connect/download/viewer/](https://www.realvnc.com/en/connect/download/viewer/)


이 문서에서 사용하고 있는 환경의 정보는 다음과 같습니다.  
튜토리얼을 시작하기 전에, 하기 정보들을 전부 체크해두세요.  

### HMC
~~~bash
#HMC의 버전정보
$ lshmc -V
~~~
![image](https://user-images.githubusercontent.com/15958325/54999618-f49c5e80-5013-11e9-921a-6a9ea2e98ead.png)
> HMC Name : pokvhmc28  
> IP Address : 10.8.252.118  
> Id : stud5037_7  

### VIOS
![image](https://user-images.githubusercontent.com/15958325/54999459-9d968980-5013-11e9-9057-75fb5585954f.png)
> Machine Name : sys868  
> IP Address : 10.8.37.100  
> Id : padmin  

### Lpar
~~~
$ lssyscfg -m <machine_name> -r lpar -F name:state
~~~
![image](https://user-images.githubusercontent.com/15958325/54999708-3200ec00-5014-11e9-9190-c76321130c2f.png)  
사진에 보이는 여러개의 Lpar중 `sys8681-lpar7`(이하 lpar7)을 사용할것.
>IP Address : 10.8.37.17  

### 기타정보
>gateway : 10.8.37.254  
>netmask : 255.255.255.0  
>nameserver(DNS) : 10.8.252.11  

## 3. Installation

HMC로 ssh접속  

설치에 들어가기 앞서 `Not Activated`상태인 Lpar를 가동시켜야 합니다. 이 문서에서는 lpar7을 대상으로 하고있으므로 하기 코드의 Lpar name에는 lpar7이 들어가면 될것입니다.    

~~~
$ chsysstate -m <machine_name> -r lpar -o on -f normal -b sms -n <Lpar name>
~~~

>혹시나 중간에 설치과정에 문제가 생겨 Lpar를 초기화 시켜야 되는 일이 발생한다면,
>~~~
>$ chsysstate -m <machine_name> -r lpar -o shutdown --immed -n <Lpar name>
>~~~
>위 코드를 통해 강제로 종료 시키자!

이제 본격적으로 설치를 진행해보자 ^^!  

~~~
$ vtmenu
~~~
![image](https://user-images.githubusercontent.com/15958325/55074745-7489fd80-50d4-11e9-9f2f-e9039a578193.png)  

Machine Name: sys868의 Lpar들의 상태를 확인할 수 있습니다. 방금 켰던 lpar7의 상태가 `Open Firmware`상태가 된 것을 확인할 수 있습니다.  

lpar7을 골라주고 `Select Boot Options`를 선택   
![image](https://user-images.githubusercontent.com/15958325/55074987-1dd0f380-50d5-11e9-9c96-3127490ac452.png)  
 

`Select Install/Boot Device`를 선택  
![image](https://user-images.githubusercontent.com/15958325/55075041-448f2a00-50d5-11e9-86a6-c8c17ef961e0.png)  

`List all Devices`를 선택  
![image](https://user-images.githubusercontent.com/15958325/55075098-6a1c3380-50d5-11e9-9ac8-c15649a3ea56.png)   
VIOS에 저장된 이미지 정보를 불러옵니다. 여기서 실습할 것은 SUSE이므로 4번을 선택  
![image](https://user-images.githubusercontent.com/15958325/55075132-7d2f0380-50d5-11e9-8d42-3b59e666d02b.png)  

`Normal Mode Boot`를 선택   
![image](https://user-images.githubusercontent.com/15958325/55075285-e9aa0280-50d5-11e9-8aaa-f504acd502e3.png)  

부팅을 기다렸다가 GRUB메뉴가 뜨면 e를 눌러서 edit화면으로 들어가야 합니다. 
>이게 타이머 기능이 있는것 같아서 여기서 멍때리다가 제대로 edit을 못하면 첨부터 다시해야되는 고역을 겪을 수 있습니다.  
>
>edit을 하는 이유는 vnc viewer로 접속하기 위함입니다. 

![image](https://user-images.githubusercontent.com/15958325/55075315-fdedff80-50d5-11e9-9a4c-ac2826d8d901.png)  

위 사진에서 e를 연타했다가는 이상한 설정파일로 들어갈수 있습니다. GRUB메뉴에서 `Installation`의 설정을 변경해야 하는데 다른 설정파일로 들어갔다면 `esc`를 누르고 메뉴로 다시 나와서 `Installation`으로 들어가면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55075363-237b0900-50d6-11e9-8099-87d6bbf6ff0f.png)  

`Installation`의 설정파일로 들어왔다면   
~~~
 linux /boot/ppc64le/linux
~~~
위 코드 바로 뒤에 한 줄로 아래와 같이 입력해줍니다.  
~~~
ifcfg=eth*={host(lpar) ip}/24,{gateway},{nameserver} hostname={name} vnc=1 vncpassword={pw}
~~~
정상적으로 입력했다면 다음 사진과 같이 보이게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55075652-dd727500-50d6-11e9-8778-1bb3f8eb29d2.png)  

`Ctrl+x`를 눌러 실행해 줍시다.  
Installing이 끝나면 다음 사진과 같이 보입니다.  
![image](https://user-images.githubusercontent.com/15958325/55075836-4f4abe80-50d7-11e9-8feb-659240c543f8.png)  

그럼 `VNC Viewer`를 켜서 접속해봅시다! Server는 lpar7의 ip값, 뒤의 1은 위의 `Installation`설정에서 입력했던 값, password는 마찬가지로 설정에서 입력했던 password를 입력하시면 됩니다.  
편하게 GUI로 나머지 설정을 해보도록 합시다.  
![image](https://user-images.githubusercontent.com/15958325/55075977-9b95fe80-50d7-11e9-8e44-4557a3dbb1b2.png)  

처음 접속했을때 보이는 화면입니다. 밑의 agree버튼을 클릭하고 다음으로 넘어가 줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55076155-10693880-50d8-11e9-8261-26d0a2042f71.png)  

중간에 multipath설정하겠냐고 뜨는데 no누르고 넘어가겠습니다. >추후에 서술할것<

Registration정보를 입력하고 넘어가면 되지만, 실습용으로 데모를 한것이라서 그냥 스킵하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/55076197-30006100-50d8-11e9-9384-a8209952d9db.png)   

Add On Product도 스킵! 추가로 설치할 프로덕트들이 있다면 마음대로 하시면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55076550-13185d80-50d9-11e9-8d52-4edd2a9a7a2d.png)  

Partition에 관한 정보입니다. Expert Partitioner를 눌러 확인해줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55076564-1dd2f280-50d9-11e9-9d79-eeeecc3445c4.png)  

지금은 /(root)가 sda에 잘 마운트되어있지만 sdb나 다른 디스크에 마운트되어있다면 delete하고 마운트하려는 sda디스크에가서 edit->Mountion Options의 Mount Point를 /로 바꿔주면됩니다.  
![image](https://user-images.githubusercontent.com/15958325/55076649-4eb32780-50d9-11e9-8658-f84a3b7ed2ad.png)    

타임존 설정해주고~!  
![image](https://user-images.githubusercontent.com/15958325/55076702-70acaa00-50d9-11e9-85e5-d37cf7f9636a.png)  

유저의 정보를 입력해줍니다. (테스트이므로) use this password for system administrator도 체크해줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55076722-7dc99900-50d9-11e9-8d13-ddc9da038321.png)  

다음은 방화벽 설정인데, 옵션 중 Firewall will be enabled(disable)을 클릭해서  
![image](https://user-images.githubusercontent.com/15958325/55076773-9c2f9480-50d9-11e9-884d-9ff515fd4e68.png)  

다음 사진과 같이 만들어줍니다.  
![image](https://user-images.githubusercontent.com/15958325/55076778-9e91ee80-50d9-11e9-8968-3a29cb31edec.png)  

빠짐없이 확인한 후, 설치버튼을 눌러줍시다!  
![image](https://user-images.githubusercontent.com/15958325/55076847-c3866180-50d9-11e9-9838-170c19bfcf37.png)  

Details탭을 통해 현재 설치 상황을 볼 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55076854-c5e8bb80-50d9-11e9-9dd1-faeacc01794c.png)  

설치가 끝나면 자동으로 재부팅 됩니다.  
HMC콘솔상에서 재부팅되면서 SUSE에 재로그인하는 화면이 뜨게 되는데, 설치과정에서 지정했던 아이디를 입력해 로그인을 하게 되면 SUSE를 사용할 수 있습니다!  
당연히 lpar7에 os가 깔렸으므로 HMC를 통해서가 아니라 lpar7에 바로 접속해서도 사용할 수 있습니다.  

다음 화면은 설치가 잘 되었는지 확인하는 파트입니다.  
~~~
$ cat /proc/version
$ cat /etc/os-release
~~~
![image](https://user-images.githubusercontent.com/15958325/55076901-e44eb700-50d9-11e9-9576-13905c627e34.png)  
![image](https://user-images.githubusercontent.com/15958325/55076903-e6187a80-50d9-11e9-9862-e4558718a726.png)  

정상적으로 SUSE가 Install되었습니다!! 

----
