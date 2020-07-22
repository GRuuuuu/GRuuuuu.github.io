---
title: "The Watson Beat Workshop"
categories: 
  - Simple-Tutorial
tags:
  - ML
  - Watson
last_modified_at: 2020-07-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
MIDI파일을 input으로 여러 분위기의 음악으로 재구성시켜주는 Watson Beat를 실습해보겠습니다.  

**"[The Watson Beat Workshop](https://github.com/watson-music/watson-beat)"를 따라서 진행한 문서입니다.**

# Prerequisites
- Python2  

튜토리얼 진행에 python2점대 버전이 필요합니다. Python3을 쓰고 계시는 분들은 아래 블로그를 참조해서 Python2를 설치해주세요.  

[python 2, 3 동시에 사용하기 (Windows)](https://http2.tistory.com/19)  

주의하셔야 할 점은 default python버전이 2점대여야하기 때문에, 환경변수세팅을 python2가 위로 오게 설정해주시기 바랍니다.  
![image](https://user-images.githubusercontent.com/15958325/88148803-1e7e8900-cc3a-11ea-8f4d-fb334e74a9c5.png)  

~~~sh
$ python -V
Python 2.7.18

$ pip -V
pip 19.2.3 from c:\python\python27\lib\site-packages\pip (python 2.7)
~~~

>해당 문서는 Window를 기반으로 작성되었습니다. 타 os를 쓰시는 분들은 원본문서를 참조해주세요.  

# Steps
## 1. Download the Watson Beat Project
~~~sh
$ git clone https://github.com/watson-music/watson-beat
~~~
또는 ZIP파일로 다운로드

## 2. Set up for development
클론받은 폴더로 이동
~~~sh
$ pwd

Path
----
C:\Users\GRu\Downloads\watson-beat-master

~~~

dependency들 설치
~~~
$ pip install -r requirements.txt
~~~
![image](https://user-images.githubusercontent.com/15958325/88150633-9b126700-cc3c-11ea-84f8-2989f5b21bb8.png)  

## 3. Choose a song (`MIDI` file)
src폴더로 이동하면 Midi폴더가 있고 폴더 안에는 여러 샘플 Midi파일이 있습니다.  

> **MIDI파일이란?**  
>연주를 위한 악보데이터라고 할 수 있습니다.  
>`MP3`가 연주를 단순히 녹음한 것이라면 `MIDI`에는 연주할 때 무슨 음으로 피아노를 치고, 드럼을 몇 박자로 쳐라 등의 명령어만이 적혀있습니다.  
>때문에 `MP3`보다 용량이 훨씬 작습니다. (커도 100kb를 안넘는 경우가 많음)

이제 아래 실습에서 사용할 midi파일을 골라주도록 하겠습니다.  

pc에 적절한 편집프로그램이 없다면 midi를 재생시킬 수 없으니 외부 app을 이용해서 플레이하겠습니다.  

해당 포스팅에서 사용하는 편집프로그램은 `SoundTrap`입니다.  
이메일로 가입할 수 있으며 1달 무료 사용이 가능한 오디오 에디터입니다.  

SoundTrap -> [https://www.soundtrap.com/](https://www.soundtrap.com/)  

가입을 완료했으면 새로운 프로젝트를 만들고,  
![image](https://user-images.githubusercontent.com/15958325/88151622-e4af8180-cc3d-11ea-95a9-f7bca9bf6129.png)  

테스트하고싶은 midi파일을 드래그 앤 드롭으로 실행시킬 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/88151630-e711db80-cc3d-11ea-80d9-4493a28a97e6.png)  

테스트해보고 마음에 드는 midi파일을 하나 골라줍니다.  
저는 `hungarian_dance`의 멜로디가 마음에 들어서 이 midi파일을 골랐습니다.  

## 4. Choose how Watson interpretes your song (`ini` file)
Watson Beat로 멜로디를 생성하려면 두가지 재료가 필요합니다.  

첫번째는 `midi`파일, 원작자에 따르면 midi파일이 10초미만일때 가장 괜찮은 결과를 낸다고 합니다.  

두번째는 `ini`파일입니다. 이런저런 설정들이 담겨있는 파일입니다. 해당 프로젝트에는 기본적으로 13개의 ini파일들이 있고, 원본 멜로디에 분위기와 템포를 꾸며줄 설정들이 담겨있습니다.  

저는 EDM노래를 좋아하니 `EDM.ini`파일을 고르겠습니다.  

## 5. Create a folder for music and run terminal command with MIDI and ini selected
src 폴더로 이동
~~~sh
$ cd src
~~~

작업용 폴더와 Watson Beat에 의해 새로 생성될 파일들을 위한 폴더를 생성해줍니다.  
~~~sh
$ mkdir music
$ cd music
$ mkdir song1
~~~

Watson Beat를 사용하는 커맨드는 다음과 같습니다.  
~~~sh
$ pwd

Path
----
C:\Users\GRu\Downloads\watson-beat-master\src


# python wbDev.py -i {ini file} -m {midi file} -o {output path}
$ python wbDev.py -i .\Ini\EDM.ini -m .\Midi\hungarian_dance_no5.mid -o .\music\song1\
~~~

윈도우 사용자들은 다음과 같은에러가 반복적으로 뜰 것 입니다.  
~~~
'rm'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는
배치 파일이 아닙니다.
'rm'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는
배치 파일이 아닙니다.
'rm'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는
배치 파일이 아닙니다.
~~~
윈도우에서의 파일 삭제 커맨드는 `del`이기 때문에 나는 에러입니다. 그냥 무시하셔도 문제 없습니다.  

정상적으로 끝나게 되면 작업용 폴더 밑에 다음과 같이 파일들이 생성됩니다.  
![image](https://user-images.githubusercontent.com/15958325/88160175-45908700-cc49-11ea-86a0-93acb89d8876.png)  

각 midi파일의 역할은 다음 이미지를 참고해주세요.  
![](https://camo.githubusercontent.com/23eb85af1ff030de126608add1605be0ea25a6be/68747470733a2f2f692e696d6775722e636f6d2f426b6846544a472e706e67)  

## 6. Import MIDI files from Watson to audio editor
이제 생성한 파일들로 어떤식으로 음악이 바뀌었는지 확인해보겠습니다.  
SoundTrap으로 이동해서, 원곡+(sec0으로 마크된)midi파일들을 전부 import해줍니다.  

![image](https://user-images.githubusercontent.com/15958325/88160390-87213200-cc49-11ea-836a-c1acebba87e1.png)  

한번 플레이 해보면 쿵짝쿵짝 드럼소리도 들리고 원본 피아노소리 말고도 반주소리같은게 들립니다.  
의외로 잘 어울리는것 같습니다.   

## 7. Export the file
File > Export > Export project to mp3 file 를 선택하면 mix한 멜로디를 다운받을 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/88160631-dff0ca80-cc49-11ea-9528-6e2932efcd3d.png)  

![image](https://user-images.githubusercontent.com/15958325/88160636-e1ba8e00-cc49-11ea-8429-5a5e16a5521c.png)  


## Appendix
- [Watson Beat란?](https://medium.com/@anna_seg/the-watson-beat-d7497406a202)   
- [How to Customize Modds Part1](https://youtu.be/OUDXpJJhoK8)
- [How to Customize Modds Part2](https://youtu.be/PSqLVEJexrU)

----