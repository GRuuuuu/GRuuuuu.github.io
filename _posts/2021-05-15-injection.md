---
title: "Think Like a Hacker! : Injection이란?"
categories: 
  - Security
tags:
  - Security
  - Developer
  - Vulnerability
last_modified_at: 2021-05-15T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
이번 포스팅에서는 **Injection**공격에 대해서 설명해보도록 하겠습니다.  

# Injection?
![image](https://user-images.githubusercontent.com/15958325/118351417-e795ad00-b596-11eb-9fba-8e42b66e3381.png)   
OWASP top10에서 2013, 2017 연속으로 1위를 차지한 만큼 굉장히 위험한 공격기법입니다.  
쉬운 공격 난이도에 비해 파괴력이 어마어마하기 때문에 보안에 손을 한번이라도 담궈본 사람들은 무조건 들어봤을겁니다.  

**Code Injection**은 공격자에 의해서 취약한 컴퓨터 프로그램 코드를 삽입하고 실행을 변경하는 방식으로 이용되고, 어플리케이션이 인터프리터에 신뢰할 수 없는 데이터를 보낼 때 발생합니다.  

Code Injection에는 여러 종류가 있는데 오늘은 `OS Command Injection`과 `SQL Injection`에 대해서 알아보겠습니다.  

