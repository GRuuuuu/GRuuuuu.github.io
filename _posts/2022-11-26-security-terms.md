---
title: "보안 용어 정리! (IAM,PAM,Federated SSO)"
categories: 
  - Security
tags:
  - IAM
  - PAM
  - Authentication
  - Authorization
last_modified_at: 2022-11-28T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## IAM (Identity and Access Management)
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022-11-28-security-terms/1.png)  
- 디지털 ID를 소유한 유저 혹은 application에게 **리소스에 접근할 수 있는 적절한 권한**을 제공하는 방식
- 암호/MFA/지문 등의 인증 절차를 거치면 리소스권한을 부여
- IAM솔루션마다 조금씩 기능은 다르지만 대부분 아래 기능을 제공
    - `MFA` : 사용자 id/pwd외에도 SMS,통화,이메일 등의 방법으로 추가 인증
    - `SSO` : 한번의 시스템 인증을 통해 다른 서비스에 재인증 절차없이 접근할 수 있게 함
	- `Federated SSO` : 신뢰관계인 다른 IdP에 인증
    - `RBAC` : 조직내 역할과 업무에 따라 리소스에 대한 액세스를 제한


## PAM (Privileged Access Management)

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022-11-28-security-terms/2.png)  
- IAM은 단순히 계정의 권한을 제어하는 역할
- IAM만으론 권한있는 사용자의 접근을 통제하지 못한다. 
- 예를들어 권한있는 사용자의 계정이 탈취당하거나 그사람이 나쁜마음을 품었을 경우 속수무책으로 당하는것


- PAM은 이런 특권을 가진 계정의 접근관리를 한다
- 기능들 :
    - 세션 모니터링
    - 액세스 권한 승격 및 위임
    - 주기적인 암호 변경(password rotation)
    - 자격증명 잠금(credential vaulting) : 계정의 모든 암호는 PAM에서 관리(사용자가 진짜 비밀번호를 모름)
- **특권 계정의 액세스 오남용을 차단하고 자산을 안전하게 관리하는것이 목표**

## Federated Identity Management (Federated SSO)
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022-11-28-security-terms/3.png)  

- 신뢰관계에 있는 다른 조직이나 3rd party 업체에 인증을 맡기는 것
- `SSO`가 **하나의 도메인** 하에서의 서비스간 인증을 간편하게 하는 절차라면 (ex. 구글로그인 -> 구글캘린더 접속)
- `Federated SSO`는 **여러 도메인**간 사이에서 SSO를 가능하게 하는 기술을 뜻한다. (ex. facebook로그인 -> 11번가 접속)
- 유저는 복잡하게 여러 사이트에 회원가입하지 않아도 되고, Service Provider들은 유저의 정보를 보관할 책임을 지지 않아도 됨

>헷갈리는 부분) 다만 로그인 자체는 3rd party IdP를 통해서 인증하더라도, Service Provider(SP)에서의 리소스를 접근할 수 있는 권한(IAM)은 또 다른얘기고,  
>IdP에서 전달하는 값 외에는 유저의 다른 정보들을 SP에서는 알 방법이 없기 때문에 필요하다면 추가적인 정보 입력이 필요합니다.  
>
> ex) 쇼핑몰사이트를 Ferderated SSO로 인증할 시, 유저의 주소정보가 추가로 필요하므로 최초 로그인할때 따로 입력하게 함

----