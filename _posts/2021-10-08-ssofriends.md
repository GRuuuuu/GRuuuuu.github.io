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
![image](https://user-images.githubusercontent.com/15958325/137650440-23361196-d93a-4595-8114-40b895df2992.png)   

자연스럽게 사용하는 기능이지만 자세히는 몰랐던 내용들, SSO와 SSO를 구현하기 위한 몇가지 인증 방법에 대해서 알아보도록 하겠습니다.

## SSO(Single Sign On)?

이름 그대로 단일 로그인, 즉 한번의 로그인으로 여러개의 애플리케이션들을 이용할 수 있게해주는 서비스 입니다.

![1](https://user-images.githubusercontent.com/15958325/137668561-5b9fa59a-0c9b-46fd-9d5f-98ee2e1492eb.png)    
SSO가 없다면 사용하고자 하는 서비스마다 따로따로 계정을 갖고 있어야 하지만,

![2](https://user-images.githubusercontent.com/15958325/137668566-d8cb5017-2324-4784-88ec-caf4b3acae02.png)     
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

- `SAMLRequest`, `SAMLResponse`는 **XML형식**이라 브라우저를 통해서만 동작 가능 -> 모바일이나 Native Application에는 부적절한 형식

## 2. OAuth 2.0

>참고 : [OAuth 2.0 Simplified](https://www.oauth.com/)

`OAuth 2.0`(Open Authorization 2.0, 이하 OAuth)는 "**Authorization**"을 위한 개방형 표준 프로토콜입니다.  
Third-Party App에게 리소스 소유자를 대신하여 리소스 서버에서 제공하는 자원에 대한 **접근 권한을 위임**하는 방식을 제공합니다.  
즉, 사용자의 동의를 받고 Third-Party App과 중요한 정보(계정)를 공유하지 않고도 자원에 접근할 수 있게 해줍니다.

예를 들어 다음과 같은 경우를 예시로 들 수 있습니다.  
![3](https://user-images.githubusercontent.com/15958325/137652947-17b0138d-f9b3-4ff3-a88a-0ca04877610d.png)  
1. 사용자는 3rd party app에 있는 "facebook 친구 리스트 import" 단자를 클릭함
2. 사용자가 Facebook에 성공적으로 로그인하면, Facebook 친구 목록을 공유하라는 메시지가 표시됨  

![4](https://user-images.githubusercontent.com/15958325/137652950-809de581-da03-4d1d-836d-e9b336644b52.png)  
3. 사용자가 Yes를 클릭하면 3rd party app에 Facebook 친구 목록을 가져올 수 있는 권한과 승인을 부여하는 토큰과 함께 사용자는 app으로 돌아감  

OAuth는 사용자가 자격 증명을 공유하지 않고도 app에서 리소스에 액세스 할 수 있습니다.  
즉, 3rd앱이 facebook아이디를 몰라도 facebook에 있는 정보를 서비스에서 안전하게 사용할 수 있다는 의미입니다.    

`OAuth`는 모바일 플랫폼에서의 `SAML`의 단점을 보완하기 위해 개발되었으며, SAML과 다르게 **XML이 아닌 JSON을 기반**으로 합니다.

또한 `SAML`은 Authentication/Authorization(인증/인가)를 둘 다 다루는데 반해 `OAuth`는 **Authorization**를 목적으로 설계되었습니다.

> `Authentication` vs `Authorization`
>
> - Authentication : 인증. 내가 누군지!
> - Authorization : 인가. 내가 어떤 권한을 갖고 있는지!  

### Access Token

OAuth의 핵심은 **Access Token**입니다.  

Access Token은 임의의 문자열 값이고, 토큰을 발급해 준 서비스만이 해당 토큰의 정보를 알고 있습니다.  

이 토큰은 **Resource Owner가 자신의 정보(Resource)를 넘겨주는 것에 대해서 동의**한다는 증표입니다.  

**SAML**에서 `SAMLAssertion`이 안에 User의 인증정보를 갖고 있어서, 해당 Assertion을 가지면 User의 인증/권한을 사용할 수 있듯이  
**OAuth**에서는 `Access Token`이 이와 비슷한 역할을 수행하게 됩니다.  
(Access Token는 인증은 불가능, 권한에 대한 허가만 가능)   


![5](https://user-images.githubusercontent.com/15958325/137664378-1bb5e28d-26b9-4236-9dd9-54769b46b681.png)  
토큰을 요청할 때에는 `redirect_uri`값을 같이 요청하여 발급받을 위치를 지정하게 됩니다.  
하지만 어떤 악의적인 사용자가 `redirect_uri`값을 변경한다면? 그럼 그 해커는 AccessToken을 탈취하고 resource에 마음대로 접근할 수 있는 권한을 갖게 됩니다.  

이러한 위험성때문에 OAuth를 사용하려는 ServiceProvider에 AccessToken을 발급받을 위치인 `redirect_uri`을 등록해야합니다.  


![6](https://user-images.githubusercontent.com/15958325/137664381-1ba3016f-fe31-4861-a5db-b0d98c0162a8.png)   
만약 위의 예시처럼 페이스북의 친구를 끌고오는 3rd party app이 있다면, OAuth방식으로 자원에 대한 권한을 얻으려면 페이스북에 3rd party app로 돌아오는 `redirect_uri`를 등록해주어야 합니다.  

![7](https://user-images.githubusercontent.com/15958325/137664383-6f6b81fb-216b-4259-9187-6f41a49675a0.png)  
만약 기 등록된 `redirect_uri`가 아니라 다른 uri로 리다이렉트로 AccessToken을 보내려고 한다면 페이스북에서는 수상한 행동으로 여기고 정보를 보내주지 않을 것입니다.  

### Refresh Token
Access Token은 탈취당하면 안되는 OAuth에서 가장 중요한 토큰입니다.  
만약 탈취당하면 악의적인 사용자가 나의 정보에 접근할 수도 있습니다.  

때문에 OAuth에서는 일정 시간이 지나면 AccessToken을 사용하지 못하도록 유효기간을 설정해둡니다.  

보통 짧게는 몇분에서 길어야 반나절 정도로 유효기간을 설정해두는데요, 이 방식은 짧으면 짧을 수록 안전하지만 **만료될때마다 다시 Resource Owner에게 허락**받아야 한다는 단점이 있습니다.(다시 로그인해야한다는 의미)  

그래서 Access Token을 간편하게 발급받을 수 있는 Refresh Token을 Access Token과 함께 받게 됩니다.  
Refresh Token은 Access Token보다 유효기간이 길어서 Access Token이 만료되더라도 **Refresh Token이 만료되지 않는 이상 로그인 없이 계속 발급**받을 수 있습니다.  


### 플로우: Authorization Code Grant
지금부터는 OAuth의 플로우에 대해서 알아보도록 하겠습니다.  

총 4가지 방법이 있는데, 해당 포스팅에서는 그 중 가장 많이 사용하고 권장하는 방법인 **Authorization Code Grant**(권한 코드 인증)에 대해서 설명하도록 하겠습니다.  

역할은 4가지입니다.  
- `Resource Owner` : 자원소유자, User
- `Client` : 클라이언트 (Ex. 3rd party app)
- `Service Provider` : 서비스 제공자 
    - `Resource Server` : 자원 서버
    - `Authorization Server` : 권한 서버


![oauth-code](https://user-images.githubusercontent.com/15958325/137623349-651dc2cc-cfa5-48d0-afcf-d6b9befc6422.png)  


**0. Client 서비스 등록**  
- 신뢰할 수 있는 Redirect Uri를 위해 미리 Service Provider(**SP**)에 Access Token을 받을 Client의 uri를 등록합니다.  

**1. 서비스 요청**  
- Resource Owner(User)가 Client에 **서비스를 요청**합니다.  
- Client에서는 Session내 Access정보가 있는지 확인합니다.  
  >ex. 같이 "게임(client)"할 친구를 구하고 싶은 "호롤리(User)"는 게임내 "페이스북(SP) 친구 연동하기" 버튼을 클릭합니다.

**2. Authorization Code 요청**  
- Session 내 Access정보가 없는 것을 확인한 Client는 SP의 **Authorization Server에 Authorization Code를 요청**합니다.  
- 이 때 Request에 포함되는 파라미터 : `client_id`, `redirect_url`, `scope` `response_type=code`
- `scope`는 어떤 권한을 요청할건지 범위
- 서버 내 Access정보가 남아있는지 확인합니다.  

**3. 로그인 팝업 출력 & 로그인 정보 입력**  
- 서버 내 Access 정보가 없다면 로그인 팝업을 사용자에게 띄웁니다.  
- 로그인하면 어떤 권한을 허가할것인지에 대한 메세지 창을 띄웁니다.
- **이때의 인증과정은 OAuth의 범위가 아닙니다. Token을 받기 위한 인증일 뿐!**  
  >ex. 호롤리는 페이스북 로그인창에 자신의 계정을 입력하여 로그인하고, 게임에서 나의 페이스북 친구리스트에 접근할 수 있는 권한을 허가해줍니다.  

**4. Authorization Code 응답**  
- 로그인 정보와 `redirect_url`이 valid하다면 Authorization Code를 `redirect_url`로 응답해줍니다.  
- **Authorization Code**는 해당 Client는 Resource Owner에게 사용허락을 인가받았음의 증서와 같습니다.  

**5. Access Token 요청**
- Access Token을 요청합니다.  
- 이 때 Request에 포함되는 파라미터 : `client_id`, `client_secret`, `redirect_url`, `authorization_code`  

**6. Access Token, Refresh Token 응답**
- `Access Token` : (user가 허락한 scope만큼의)Resource를 사용할 수 있게 해주는 토큰
- `Refresh Token` : 보안을 위해 유효시간이 짧은 Access Token을 위해 간단히 Access Token을 발급받을 수 있게 해주는 토큰
- 아래와 같은 형식으로 응답이 오게됩니다.  
  ~~~
  HTTP/1.1 200 OK
  Content-Type: application/json
  Cache-Control: no-store
  Pragma: no-cache
  
  {
    "access_token":"MTQ0NjJkZmQ5OTM2NDE1ZTZjNGZmZjI3",
    "token_type":"bearer",
    "expires_in":3600,
    "refresh_token":"IwOGYzYTlmM2YxOTQ5MGE3YmNmMDFkNTVk",
    "scope":"create"
  }
  ~~~

**7. Resource 요청**
- Client는 발급 받은 Access Token을 통해 Resource Server에서 사용자의 정보에 접근합니다.   
- Resource를 요청할 때에는 다음과 같이 **Request헤더에 AccessToken을 세팅**합니다.  
  ~~~
  Authorization: Bearer <ACCESS TOKEN>
  ~~~


**8. Resource 응답**
- Resource Server는 받은 **Access Token의 유효성**과 **지정된 scope**에 접근하는것이 맞는지 확인한 후, 정보를 내어줍니다.  

**9. 서비스 응답**
- 요청했던 Resource를 토대로 Client는 Resource Owner가 요청했던 서비스를 제공합니다.  
  > ex) 페이스북 로그인을 마친 호롤리는 게임 화면에서 자신의 페이스북 친구들을 확인할 수 있게 되었습니다!  

### Access Token이 만료되었을 경우  

![refreshtkn](https://user-images.githubusercontent.com/15958325/137625616-86147feb-67d5-440e-8e3c-f6e29298a759.png)  

Access Token이 만료되면 Client는 더이상 Resource Server로부터 Resource를 가져올 수 없습니다.(권한 없음!)  

**1. Access Token 재요청**
- Refresh Token과 만료된 Access Token을 Authorization Server로 보냅니다.  
  ~~~
  POST /oauth/token HTTP/1.1
  Host: authorization-server.com
  
  grant_type=refresh_token
  &refresh_token=xxxxxxxxxxx
  &client_id=xxxxxxxxxx
  &client_secret=xxxxxxxxxx
  ~~~

**2. 새로운 Access Token 발급**
- 서버는 받은 Refresh Token이 조작되지 않았는지 DB의 토큰과 비교 합니다.  
- 토큰이 동일하고 Refresh Token의 유효기간도 지나지 않았다면 새로운 Access Token을 발급해 줍니다.  

>만약 Refresh Token도 만료되었다면 다시 로그인을 해야합니다!  

## 3. OIDC (OpenID Connect)
OpenID Connect(이하 OIDC)는 권한 허가 프로토콜인 OAuth 2.0를 이용하여 만들어진 인증 레이어 입니다.  

OAuth는 위에서 언급했듯이, Authorization을 위한 기술이지 Authentication을 위한 기술은 아닙니다.  
OAuth에서 발급하는 Access Token은 일시적으로 특정 권한을 허가해준 토큰일 뿐이지 사용자에 대한 정보는 담고 있지 않습니다.  
Access Token을 발급하기 위해 사용자 인증을 하긴 하였으나 **Access Token이 사용자 인증을 위해 사용되어선 안됩니다.**  

그래서 OIDC에서는 **인증**을 위해 `ID Token`이라는 토큰을 추가하였습니다.  

### ID Token
**Access Token**이 Bearer 토큰 형식이었다면,  
**ID Token**은 `JWT`(JSON Web Token)형식입니다.  

**JWT**는 header, payload, signature 3가지 부분이 담겨있는 토큰입니다. **ID Token**을 얻으면 Client는 `payload`부분에 인코드 된 사용자 정보를 얻을 수 있습니다.  

`payload`에는 `claims`라는 필드를 포함하게 되는데 기본적인 `claims`는 다음과 같습니다.  
~~~
{
  "iss": "https://server.example.com",
  "sub": "24400320",
  "aud": "s6BhdRkqt3",
  "exp": 1311281970,
  "iat": 1311280970
}
~~~
`iss`(issuer) : 토큰 발행자  
`sub`(subject) : 토큰의 고유ID  
`aud`(audience) : 토큰을 요청하는 Client의 ID  
`exp`(expiration time) : 토큰의 유효시간  
`iat`(issued at) : 토큰이 발행된 시간  

`claims` 필드는 원한다면 추가로 다른 값들을 추가할 수 있습니다. (ex. `eamil`, `address`, `id` 등)  

ID Token(JWT)를 통해서 누가 인증을 했는지, 발행자(issuer)가 누구인지 등을 알 수 있습니다.  

### 인증 플로우
그럼 OIDC의 인증 플로우에 대해서 살펴보겠습니다.  

![oidc](https://user-images.githubusercontent.com/15958325/137629931-276443eb-398c-46f8-8929-9e3cc7c1a93a.png)  

기본적인 토큰발급과 refresh token으로 토큰을 갱신하는등 일련의 동작들은 OAuth와 동일합니다.  
다른 점은 로그인 시, `id_token`이라는 별도로 발급받게되고 해당 토큰을 통해 유저의 인증을 손쉽게 할 수 있게 됩니다.  

- `id_token`의 audience를 통해 유효한 client로부터 온 토큰인지 검증
- `id_token`으로부터 user정보를 추출한 뒤, DB와 교차검증

## Appendix. SAML vs OAuth2.0 vs OIDC
마지막으로 세가지 방식의 차이점을 알아보겠습니다.  

.|SAML|OAuth2.0|OIDC
---|---|---|---
Format|XML|JSON|JSON
Authorization|O|O|X
Authentication|O|Pseudo-authentication|O
created|2001|2005|2006
Best Suited for|SSO for Enterprise(Not well suited for mobile)|API authorization|SSO for consumer apps

- **SAML** : 인증/인가 모두 제공, XML기반, Enterprise용 SSO구축에 주로 사용
- **OAuth2.0** : Authorization만 제공, JSON기반, 자격증명을 app과 공유하지 않고도 자원을 사용할 수 있게 해줌
- **OpenID Connect** : OAuth2.0과 함께 주로 사용, JSON기반, mobile과 native app에서 사용될 수 있는 구조를 가짐

### OAuth2.0 Pseudo Authentication and OPenID
이 포스팅을 만들면서 꽤나 많은 자료들을 읽었는데 이부분이 많이 헷갈려서 정리할겸 적어둡니다.  

참고 : [WIKI:OpenID vs. pseudo-authentication using OAuth](https://en.wikipedia.org/wiki/OAuth#OpenID_vs._pseudo-authentication_using_OAuth)  
참고2 : [Common pitfalls for authentication using OAuth](https://oauth.net/articles/authentication/)

먼저 OAuth는 `Authorization`을 목표로 설계되었으며,  
OpenID는 `Authentication`을 목표로 설계된 툴입니다.  

하지만 인터넷에 검색해보면 OAuth로 인증을 시도하는 몇가지 사례들을 볼 수 있습니다.(실제로도 OAuth로 인증 프로토콜을 구축하는 것은 가능합니다)  
이때 OAuth로 인증하는 것을 **Pseudo Authentication**이라고 부릅니다.  

왜 Pseudo Athentication이라고 할까요?  

아래 OAuth로 인증을 시도할 경우의 취약점들을 보면 왜 허위/사칭 인증이라고 적어놨는지 알 수 있습니다.

1. OAuth를 통해 얻는 Access Token은 User인증 후에 발급받게 되기 때문에 인증의 증거로 간주될 수 있으나, 실제로 Access Token에는 User에 대한 정보가 없고 **특정 권한에 대한 허가**만 존재
2. Access Token을 통해 특정 사용자의 특정 자원에 접근 할 수 있으니 인증의 증거로 생각될 수 있으나, Refresh Token이나 Assertion을 통해 **사용자가 인증하지 않아도 Access Token을 발급**받을 수 있음
3. 외에도 Access Token의 탈취 가능성, Access Token Injection공격, 다른 Client의 Access Token으로 로그인 위장 공격 등 여러 **보안 위협**들이 존재

>OIDC에서는 인증을 위한 `id_token` 토큰을 따로 두어 위의 위협들을 해소했습니다.

따라서 OAuth로 Authentication을 할 수는 있지만! 여러 보안위협들이 존재하기 때문에 OIDC나 SAML과 같은 방식을 따르는 것이 안전합니다.  

----

