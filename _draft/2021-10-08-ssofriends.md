---
title: "호다닥 공부해보는 SSO와 친구들 (SAML, OAuth, OIDC)"
categories:
  - Security
tags:
  - Security
  - Auth
last_modified_at: 2021-10-08T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview

우리는 여러 사이트를 돌아다니면서 내가 "나"임을 증명하기 위해 계정을 만들고 로그인을 하게 됩니다.  
예전에는 여러 사이트마다 각자 계정을 만드는 일이 잦았는데 최근엔 대형 회사들(eg. Google, Naver, Facebook 등)의 계정으로 로그인을 대신 할 수 있게 되었습니다.

자연스럽게 사용하는 기능이지만 자세히는 몰랐던 내용들, SSO에 대해서 알아보도록 하겠습니다.

## SSO(Single Sign On)?

이름 그대로 단일 로그인, 즉 한번의 로그인으로 여러개의 애플리케이션들을 이용할 수 있게해주는 서비스 입니다.

(아이디 여러개 그림)  
SSO가 없다면 위와 같이 사용하고자 하는 서비스마다 따로따로 계정을 갖고 있어야 하지만,

(SSO 도입)  
SSO가 도입된다면 서비스마다 개별로 계정을 만드는 대신 하나의 계정으로 연관된 서비스들을 사용할 수 있게 됩니다.

사용자로써는 여러개의 계정(비밀번호)을 일일히 기억할 필요가 없게 되고,  
관리자로써는 서비스별로 인증시스템을 구축할 필요가 없게되며 하나의 계정으로 여러 시스템과 플랫폼, 기타 리소스에 대한 사용자 접근을 관리할 수 있게 됩니다.

### 작동원리

SSO를 구현하기 위한 표준은 여러가지이지만 기본 패턴은 동일합니다.  
일반적으로 두가지 모델로 구분됩니다.

**1. Delegation Model**  
![image](https://user-images.githubusercontent.com/15958325/136686444-e8e9daf9-29cf-48a8-b50a-fe07941fcd06.png)  
권한을 얻으려는 서비스의 인증방식을 변경하기 어려울 때 많이 사용되는 방식입니다.  
**대상 서비스의 인증방식을 변경하지 않고, 사용자의 인증 정보를 Agent가 관리하여 대신 로그인 해주는 방식입니다.**  
만약 Target Service에 로그인하기 위한 정보가 admin/passwd라면, Agent가 해당 정보를 가지고 있고 로그인할때 유저대신 대상 서비스로 정보를 전달해 로그인시켜줍니다.

**2. Propagation Model**  
![image](https://user-images.githubusercontent.com/15958325/136687288-b8b898bc-d6b2-4e93-a2e2-b15e9616fb5c.png)  
통합 인증을 수행하는 곳에서 인증을 받아 **"인증 토큰"이라는 것을 발급**받게됩니다.  
유저가 서비스에 접근할 때 발급받은 인증토큰을 서비스에 같이 전달하게 되고, 서비스는 토큰정보를 통해 사용자를 인식할 수 있게 하는 방식입니다.

서비스의 특성에 따라서 두가지 모델을 혼용해서 전체 시스템의 SSO를 구성하는 것이 일반적입니다.

### 구현은 어떻게?

SSO 시스템은 여러 표준, 프레임워크에 의해서 구현될 수 있습니다.  
대표적으로 세가지 방식이 있는데요, **SAML/OAuth/OIDC** 이 세가지 방식에 대해서 알아보도록 하겠습니다.

## 1. SAML(Security Assertion Markup Language)

`SAML`은 인증 정보 제공자와, 서비스 제공자 간의 인증 및 인가 데이터를 교환하기 위한 **XML기반의 표준 데이터 포맷**입니다.

SAML이 출현하기 이전, 기업들은 독자적인 인터페이스 또는 특정한 SSO솔루션을 사용하여 SSO를 구축해야 했습니다.  
SSO솔루션들은 Private망에서 인증정보를 Cookie에 담아 사용하는 등의 방법을 사용하였지만, Public 망에서는 보안적으로 문제가 있었습니다.

`SAML`은 인증정보를 XML포맷으로 생성하고, 이 XML데이터를 암호화함으로써 제 3자에게 내용을 노출시키지 않고 최종 수신자에게 전달할 수 있습니다.  
이 때 생성한 XML을 **Assertion**이라고 부릅니다.

XML Assertion 예시)  
![image](https://user-images.githubusercontent.com/15958325/136699166-1b947ab2-b913-4a69-a6a5-11ac819f7180.png)

Assertion에는 ID공급자 이름, 발행일 및 만료일 같은 정보가 포함되어 있습니다.

> 항목별로 자세한 설명은 링크로 대신하겠습니다.  
> 참고 : [Glossary for the OASIS Security Assertion Markup Language (SAML) V2.0](http://docs.oasis-open.org/security/saml/v2.0/saml-glossary-2.0-os.pdf)

### 인증 플로우

그럼 이제 SAML의 인증 플로우가 어떤식으로 이뤄지는지 살펴보도록 하겠습니다.

SAML의 인증 플로우에는 3가지 역할이 있습니다.

- `User` : 인증을 원하는 사용자
- `Identity Provider`(IDP) : 인증 정보 제공자
- `Service Provider`(SP) : 서비스 제공자

![d](https://user-images.githubusercontent.com/15958325/136698132-430e1e7e-1628-4430-8060-7bce8553b547.png)

**1. 서비스 요청**

- 유저가 서비스에 접근합니다. SP는 해당 유저가 이미 인증을 했는지 안했는지 체크합니다.

**2. SSO 서비스 이동**

- 인증되지 않은 유저이므로 인증 요청을 생성하여 클라이언트에 전송합니다.
- SP에서 `SAMLRequest`를 생성하여 유저에게 전송합니다.
- SP는 IDP와 직접연결되지 않고 유저의 브라우저에서 IDP로 `SAMLRequest`를 redirect하게 합니다.

**3. SSO 서비스 요청**

- IDP는 `SAMLRequest`를 파싱하고 유저 인증을 진행합니다.
- 인증 방식은 패스워드, PKI등 다양하게 사용될 수 있습니다.

**4. SAML응답**

- 인증이 성공하게 되면 `SAMLResponse`를 생성하여 유저의 브라우저로 전송합니다.
- `SAMLResponse`에는 `SAMLAssertion`이 포함됩니다.(XML형식)
- IDP는 웹 브라우저에 Session Cokkie를 설정하고 해당 정보는 브라우저에 캐싱됩니다.

**5. (POST)SAML 응답 전송**

- 유저는 SP의 ACS(Assertion Consumer Service)의 URL에 `SAMLResponse`를 POST합니다.

**6. 서비스 응답**

- ACS는 `SAMLResponse`를 검증하고 유효하다면 유저가 요청한 서비스로 유저를 Forwarding합니다.
- 로그인 성공!

로그인이 성공한 뒤에 로그인되지 않은 다른 서비스를 이용하려고 할 때에는 2번까지 동일한 과정입니다.  
하지만 이미 인증이 성공한 `SAMLResponse`가 브라우저에 캐싱되어있으므로, 별도의 로그인 폼을 띄우지 않고 `SAMLResponse`를 SP에 전송하게 됩니다.

### 단점

- `SAMLRequest`, `SAMLResponse`는 **XML형식**이라 브라우저를 통해서만 동작 가능 -> Native Application에는 부적절한 형식

## 2. OAuth 2.0

`OAuth 2.0`(Open Authorization 2.0, 이하 OAuth)는 "**Authorization**"을 위한 개방형 표준 프로토콜입니다.  
Third-Party App에게 리소스 소유자를 대신하여 리소스 서버에서 제공하는 자원에 대한 **접근 권한을 위임**하는 방식을 제공합니다.  
즉, 사용자의 동의를 받고 Third-Party App과 중요한 정보(계정)를 공유하지 않고도 자원에 접근할 수 있게 해줍니다.

예를 들어 다음과 같은 경우를 예시로 들 수 있습니다.  
(facebook 친구 import)  
• 먼저 사용자는 3rd party app에 있는 “facebook 친구 리스트 import” 단자를 클릭함
• 사용자가 Facebook에 성공적으로 로그인하면, Facebook 친구 목록을 공유하라는 메시지가 표시됨
• 사용자가 Yes를 클릭하면 3rd party app에 Facebook 친구 목록을 가져올 수 있는 권한과 승인을
부여하는 토큰과 함께 사용자는 app으로 돌아감
• OAuth2는 사용자가 자격 증명을 공유하지 않고도 app에서 리소스에 액세스 할 수 있음
3rd앱이 facebook아이디를 몰라도 facebook에 있는 정보를 서비스에서 안전하게 사용할 수 있음!!!  
(위에 나중에 수정)

`OAuth`는 모바일 플랫폼에서의 `SAML`의 단점을 보완하기 위해 개발되었으며, SAML과 다르게 **XML이 아닌 JSON을 기반**으로 합니다.

또한 `SAML`은 Authentication/Authorization(인증/인가)를 둘 다 다루는데 반해 `OAuth`는 **Authorization**를 목적으로 설계되었습니다.

> `Authentication` vs `Authorization`
>
> - Authentication : 인증. 내가 누군지!
> - Authorization : 인가. 내가 뭘 할수있는지! (권한)

### Access Token

OAuth의 핵심은 Access Token입니다.
