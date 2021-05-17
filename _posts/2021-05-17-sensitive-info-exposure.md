---
title: "Think Like a Hacker! : 민감한 정보 유출(Sensitive Information Exposure)"
categories: 
  - Security
tags:
  - Security
  - Developer
  - Vulnerability
last_modified_at: 2021-05-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
![image](https://user-images.githubusercontent.com/15958325/118351417-e795ad00-b596-11eb-9fba-8e42b66e3381.png)   

이번 포스팅에서는 2013 6등에서 2017 3등으로 급등한 **민감한 정보 유출(Sensitive Information Exposure)**에 대해서 설명해보도록 하겠습니다.  

# 민감 정보 유출이란?
**권한이 없는 사용자에게 중요한 정보가 유출**되는 것을 뜻합니다.  
공격자는 이러한 정보를 사용하여 시스템, 사용자 또는 관리자에게 추가적인 공격을 가할 수 있습니다.  

예를 들어 :   
1. Error message로부터 Internal server의 **IP 또는 name** 노출
2. HTTP헤더나 file확장자로부터 server/service/technology에 사용된 패키지 **버전 정보** 노출
3. HTTP Request나 Query에서 secret정보를 그대로 사용하는 경우
    ex) `GET /userinfo/hololy?access_token=fjdksalfvnk223j3kncdk33`  
4. Javascript코드의 제작자가 지워지지 않고 노출됨  
ex)
    ~~~
    /**
    * @author hololy@mail.com
    * @memberOf hololys
    * @function getUsers
    * @description get User Info
    * @return {JSON}
    */
    ~~~

# 예방 방법
## 1. 너무 자세한 Error message, API call은 지양하라
너무 자세한 Error Message나 API call은 민감한 정보를 노출시킬 수 있습니다.  
하지만 너무 정보가 없어도 사용자들은 불편함을 느낄 것입니다.  
그래서 적당히 균형을 잡는 것이 중요합니다.  

- default 서버 에러 페이지를 custom 에러 페이지로 변경할 것
- Error msg에 파일경로, IP, server이름, stack trace 등을 포함시키지 말 것
- HTTP응답 또는 API에서 버전정보를 노출시키지 말 것
- API사용 시, 민감한 정보(Email, Account정보, Secret 등)를 plain text로 넘기지 말 것
- Error msg에서 end user에게 필요없는 구현정보를 노출시키는 것 보다 Error 상황 시 어떻게 해야하는지를 적을 것

## 2. 계정관리에 관한 몇가지 팁들
- 사용자가 잘못된 id를 입력했을 경우, **General한 경고문구를 사용** ("잘못된 계정 또는 암호")
    - 만약 "없는 id이므로 계정을 생성하세요"와 같은 경고문구라면 해커는 손쉽게 계정의 등록 여부를 확인할 수 있습니다.  
- 해시 알고리즘을 사용하여 해시된 암호를 저장하는 경우, 잘못된 비밀번호를 입력하였을 때 **너무 빨리 결과를 반환하지 말 것**
    - 만약 너무 빨리 결과를 반환하였을 경우, 공격자는 이 시간 간격을 통해 비밀번호를 유추할 수 있습니다. 
- 비밀번호 재설정은 id의 등록여부를 떠나서 **동일하게 동작**해야 합니다.  
    - 등록되지 않은 id 비밀번호 재설정 -> "등록된 메일로 재설정 링크보냄!" ->메일안옴  
    - 등록된 id 비밀번호 재설정 -> "등록된 메일로 재설정 링크보냄!" ->재설정메일 받고 변경

## 3. secret을 하드코딩하지 말 것
가끔 소스코드에 민감한 정보들(접속정보, wifi비밀번호, 토큰, API Key값)을 Github이나 공개된 페이지에 올리는 경우가 있습니다.  

반드시 이런 경우가 없도록 신경써서 코딩하여야 합니다.  

>**Github에서 민감한 데이터 없애기**  
> [Removing sensitive data from a repository](https://docs.github.com/en/github/authenticating-to-github/removing-sensitive-data-from-a-repository)  


----