---
title: "Error: Failed Installation Linux on VirtualBox"
categories: 
  - ERROR
tags:
  - VM
  - Virtualbox
  - LINUX
last_modified_at: 2019-10-15T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


## Environment
`Arch : amd64`   
`OS kernel : Window10 pro`  
`Virtualbox : v6.1`  
`CentOS : v7`

## Purpose
virtualbox에 centos7 vm을 생성하려고 함

## Problem

설치 전, 이미지 체크 부분에서 해당 에러 발생 :  
~~~sh
    Checking: 004.5%

The media check is completed, the result is: Fail

It is not recommended to use this media.
[Failed] Failed to start Media Check on /dev/sr0
See ´systemctl status checkisomd5@-dev-sr0.service´for details.
[ 191.018148 ] dracut-initqueue[540]: Job for checkisomod5@-dev-sr0.service failed because the control process exited with error code. See "systemctl status checkisomd5@-dev-sr0.service" and "journalctl -xe" for details.
[ 191.552636 ] dracut : FATAL: CD Check failed!
[ 191.554295 ] dracut: Refusing to continue
[191.874800 ] System halted.
~~~

무시하고 설치를 진행해도 결국 알 수 없는 에러를 뿜으며 제대로 설치되지 않음.

> ubuntu 18.04도 동일한 문제 발생(제대로 설치 안됨)


# Solution

## 1. 이미지 문제
먼저 이미지를 다운받는 과정에서 이미지가 깨졌을 수 있다.  

다시한번 다운로드 받아보자

## 2. Hyper-v
인터넷에 `Failed to start Media Check on /dev/sr0` 를 검색해보면 1번으로 해결했다는 얘기가 대다수이다.  

근데 1번을 했는데도 안되는 경우면, Hyper-V가 켜져있는지를 확인해봐야한다.  

> 예전엔 Hyper-V가 켜져있으면 virtual box가 작동하지 않았던것 같은데, 최근 들어서 바뀐모양이다. 그래서 Hyper-V가 꺼져있는줄 알고... 한참동안 삽질을 했다는ㅜㅜ 


window cmd창을 켜서 다음 커맨드로 Hyper-V를 off시키고 다시 vm을 실행시켜보면 정상적으로 실행되는 모습을 확인할 수 있을 것이다.  
~~~sh
$ bcdedit /set hypervisorlaunchtype auto
~~~

----