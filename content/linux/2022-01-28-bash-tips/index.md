---
title: "내가 보려고 만든 Bash Tips"
slug: bash-tips
tags:
  - bash
  - Tips
date: 2022-01-28T13:00:00+09:00
---

## Overview
개발 및 인프라 작업을 하다보면 이제는 필수적으로 만날 수 밖에 없는 리눅스 쉘 환경!   
그 중에 알면 쓸모있는 몇가지 팁을 기록해두려 합니다.  

-이 문서는 주인장이 새로운 팁을 배우는 족족 업데이트 될 예정입니다-  

# VIM
# 예쁜 vim 만들기
vimrc설정과 각 항목에 대한 설명 : 
[예쁜 vim 만들기 (Arcy’s vim)](https://gruuuuu.github.io/linux/arcy-vim/)  

# Command Line
## 커서 이동 / 편집
`Ctrl+A` / `Ctrl+E` : 줄의 맨 앞/뒤 이동   
`Ctrl+F` / `Ctrl+B` : 한 칸 앞으로/뒤로   
`Alt+F` / `Alt+B` : 단어 단위로 앞으로/뒤로   

`Alt+D` : 현재 커서에서 단어 끝까지 지우기   
`Alt+Backspace` : 단어단위로 지우기  
`Ctrl+K` / `Ctrl+U` : 커서 뒤로/앞으로 잘라내기  
`Ctrl+W` : 커서 앞으로 한 단어 잘라내기   
`Ctrl+Y` : 붙여넣기  


## 그 외 기능  
`Tab` : 자동완성  
`Ctrl+R` : 이전 명령어 검색   
`Ctrl+C` : 중단 (`SIGINT`)  

# ETC
## bash history
기본 bash history 사이즈는 1000개  
늘릴려면  
~~~sh
$ vi ~/.bash_profile
->HISTSIZE를 조절  
~~~
`HISTSIZE` 값이 비워져 있으면 무한대  

## 파이프라인   
~~~
$ grep abcd || useradd ddd
~~~
`||`는 앞의 명령이 실패할때에만 뒤의 명령어를 실행하게 함   

~~~
$ grep abcd; useradd ddd
~~~
`;`는 앞의 명령어가 실패하든 성공하든 무조건 뒤의 명령어까지 실행하게 함   


