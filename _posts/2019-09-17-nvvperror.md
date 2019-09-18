---
title: "[Solved] Nvidia Visual Profiler : GC Overhead"
categories: 
  - ERROR
tags:
  - NVIDIA
  - JAVA
last_modified_at: 2019-09-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


## Environment
`Arch : ppc64le(Power9)`   
`OS : GNU/Linux`   
`CUDA : v10.1`   
`GPU : Tesla V100-SXM2-16GB`

## Purpose
machine learning python코드를 돌려 GPU와 CPU간의 memcopy를 nvvp로 시각화 해보고자 함

## Problem
파이썬 코드를 돌리면서 nvprof로 정보 수집 시작
~~~
$ nvprof --log-file /tmp/tensorlogs/nvprof/nvprof1.%p.txt --export-profile /tmp/tensorlogs/nvprof/nvprof1.%p.nvvp --print-gpu-trace --profile-child-processes python tf_cnn_benchmarks.py
~~~

파일 생성까지 **정상적**으로 이루어짐
![image](https://user-images.githubusercontent.com/15958325/65101799-2828d600-da04-11e9-8904-8e183576dfaf.png)

Nvidia Visual Profiler를 오픈함과 동시에 생성했던 nvprof파일을 profiling  
~~~
$ nvvp nvprof1.129182.nvvp
~~~   

## ERROR
로딩 중에 다음과 같은 에러가 발생  
~~~
Exception in thread "LoadPdm" java.lang.OutOfMemoryError: GC overhead limit exceeded
...

Exception in thread "LoadPdm" java.lang.OutOfMemoryError: Java heap space
...
~~~

# Solution

## Caused by : Java OutOfMemoryError
출력된 오류 메세지와 같이 **메모리가 초과**되어 발생되는 에러.  
메모리가 부족하여 Garbage Collection이 이루어졌으나 확보된 메모리가 전체 메모리의 2%에 불과할 경우에 발생함.  

앞선 nvprof파일을 보면 수집시간이 굉장히 짧음에도 불구하고 크기가 굉장히 큰 것을 확인할 수 있음. (여담으로 1시간짜리는 2GB가 넘었음..)  

[[Nvidia Developer Blog](https://devblogs.nvidia.com/cuda-pro-tip-improve-nvvp-loading-large-profiles/)]  

위 링크에 따르면 NVVP에서 OOM이 발생하는 이유는 CUDA 툴킷 설치의 libnvvp / nvvp.ini 파일에 지정된 Java **최대 힙 크기 설정** 때문임.   
default로 힙 크기를 1GB로 제한하도록 Java VM을 구성하게됨.  


## How to solve?
힙크기떄문에 문제가 생기는 거니 힙크기를 늘려주면 된다!  

- 최소 힙 크기(-Xms)를 2GB로 늘리자 
- 최대 힙 크기(-Xmx)는 돌리고자 하는 파일의 5~6배정도 크기면 적당
- 기본 32 비트 모드 대신 64 비트 모드로 실행하도록 Java에 지시 (힙 크기> 4GB를 원하는 경우에 필요함.) (-d64)
- Java의 병렬 가비지 수집 시스템을 사용하면 지정된 입력 크기에 필요한 메모리 공간을 줄이고 메모리 오류를보다 효과적으로 잡아낼 수 있음. (-XX : + UseConcMarkSweepGC -XX : + CMSIncrementalMode)  

**결론 :**  
~~~
$ nvvp -vm -d64 -vmargs -Xms2g -Xmx22g -XX:+UseConcMarkSweepGC -XX:+CMSIncrementalMode
~~~  
이렇게 실행하자!  

성공!@@@@@@@@!!!!  
![image](https://user-images.githubusercontent.com/15958325/65113946-00476b80-da20-11e9-9119-cada0e5c1396.png)
