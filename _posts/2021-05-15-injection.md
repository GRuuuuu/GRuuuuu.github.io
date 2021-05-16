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

# OS Command Injection

시스템의 명령어를 쿼리문에 주입하여 서버 운영체제에 접근하는 공격
즉, 웹페이지에 시스템 명령어를 주입하여 쉘을 획득하는 공격!

예를 들어 아래와 같이 nslookup으로 입력된 주소의 dns를 확인하는 웹 페이지가 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/118359000-47527f00-b5bc-11eb-8325-fcdb3938a9ec.png)  

해당 페이지는 php로 짜져있고, dns lookup을 하기위해 파라미터를 `commandi`로 받아 `shell_exec`로 실행시키고 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/118359046-87b1fd00-b5bc-11eb-8411-8b9596f2d7b2.png)   

그런데 command로 실행시킬 파라미터를 plain하게 받아오는것부터가 뭔가 찜찜하지 않으십니까?  

아래 사진과 같이 주소옆에 파이프('`|`')를 붙이고 파일의 리스트를 출력하는 `ls` command를 입력하였더니 정상적으로 dns리스트가 출력되는 것이 아니라 웹서버 내 파일들이 출력되는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/118359087-ca73d500-b5bc-11eb-8f27-eb61d5f00d1b.png)   

더 나아가서는 웹서버의 서버 계정을 탈취될 위험성이 있으며  
![image](https://user-images.githubusercontent.com/15958325/118359730-d44b0780-b5bf-11eb-8f84-4b438091e51a.png)   
이를 토대로 웹서버로의 원격 접속까지 시도될 수 있습니다.

**OS Command Injection으로 발생할 수 있는 문제들:**  
- 전체 시스템 탈취
- 서비스거부
- 서버 내 중요한 정보 유출(password, 암호키 등)
- 다른 시스템에 대한 공격용 패드
- Botnet 또는 cryptomining을 위한 시스템으로 전락

## OS Command Injection 예방하기
### 1. OS command를 실행시키지 말자!
OS Command를 사용하면 쉽고 빠르게 문제를 해결할 수 있습니다.  
하지만 완벽한 validation없이는 치명적인 문제를 안고 있기 때문에 **아예 사용하지 않는 것을 권장**하고 있습니다.  

하지만 서버단의 액션이 필요한 경우에는 os command 대신 3rd party의 라이브러리를 사용하는 것을 추천합니다.  

예를들어 파일을 지우는 command를 실행해야 한다면,  
`rm` 대신 `java.nio.file.Files.deleteIfExists(file)`,  
파일을 복사해야한다면  
`cp`대신 `java.nio.file.Files.copy(source, destination)` 과 같은 라이브러리를 사용하도록 합니다.  

### 2. 최소한의 권한으로만 실행하기
os command를 피치못하게 사용해야할 경우, 실행 권한을 root가 아닌 제한된 권한을 가진 user로 실행하게 하는 방법입니다.  

예를 들어 `rm -rf /`가 실행되는 경우(실행되면 안되겠지만!) `root`유저로써 실행되는 것보다 `tomcat`유저로써 실행되는것이 피해를 줄일 수 있습니다.  

### 3. command를 shell interpreter를 통해서 실행시키지 말 것
보통 shell interpreter로는 `sh`, `bash`, `cmd`, `powershell`등을 사용하는데 이런 interpreter로 command를 돌리게되면 원래 목적과는 맞지 않은 명령어들을 실행할 가능성이 있습니다.  

예를들어 `rm -rf`을 command injection 했다고 했을 때,  
`sh`로 실행했을 때에는 `rm -rf` 파이프 구문이 실행됩니다.  
~~~
/bin/sh -c "/bin/rm/var/app/logs/x;rm –rf /"
~~~
반면 `sh`가아니라 `rm`바이너리 파일로 명령어를 실행시킨다면 전체 명령어가 실행되지 않을 것입니다. (rm명령어 포맷에 맞지 않기 때문)  
~~~
/bin/rm /var/app/logs/x;rm -rf /
~~~

### 4. system command를 실행할 때 안전한 function사용하기
웹에서 시스템 command를 실행시킬 때 사용하는 명령어중 하나인 `Runtime.getRuntime().exec()`입니다.  
~~~
Runtime.getRuntime().exec("/usr/bin/nmap " + ipAddress);
~~~
위 경우, 변수 `ipAddress`가 설계자의 의도대로 ip주소 하나만 적을 수도 있지만 파이프를 통해 여러 malicious한 코드를 적는다면?  
exec 명령어는 여러개의 파라미터로 인식하고 파이프로 이어진 코드들을 의심없이 실행시킬 것입니다.  

하지만 아래와 같이 `exec`의 파라미터를 String Array로 감싼다면,  
~~~
Runtime.getRuntime().exec(new String[]{"/usr/bin/nmap",ipAddress});
~~~
두 개의 배열("/usr/bin/nmap", "ipAddress")로만 인식되어 여러 malicious코드를 실행시킬 가능성을 배제시킬 수 있습니다.  

### 5. (가능하면) 사용자의 입력이 command실행에 영향을 끼치지 못하게 하라
예를 들어 파일을 삭제하는 액션을 설계해야하는 경우,  
유저와 파일의 매핑테이블같은 것을 만들어서 파일의 id만을 입력하게 하는겁니다.  

~~~java
realName = getRealFileName(fileID);
Runtime.getRuntime().exec(new String[]{"/bin/rm","/var/app/logs/"+realName});
~~~
위 코드에서는 유저의 입력(fileID)을 받아서 `getRealFileName`함수로 매핑테이블에서 검색을 하고 진짜 file이름을 반환하게 됩니다.  
이런 과정하에서는 해커가 malicious한 코드를 input에 끼워넣어도 `getRealFileName`함수에서 일치하는 파일 명을 찾을 수 없으니 무용지물이 되게 됩니다.  

### 6. Input validation (Whitelist사용! Blacklistㄴㄴ)
[이전포스팅](https://gruuuuu.github.io/security/xss/#4-input-validation)에서도 설명했다시피 blacklist로는 기상천외한 공격들을 완벽하게 막을 수 없기 때문에 Whitelist를 사용하는 것을 강력하게 권고하고 있습니다.  

예를 들어 파일이름의 whitelist 같은 경우 `[A-Za-z0-9.]+`과 같이 제한을 둘 수 있습니다.  

# SQL Injection
웹 어플리케이션이 뒷단의 Database에 SQL쿼리를 질의하는 과정 사이에 발생하는 Injection공격입니다.  
주로 인풋값을 제대로 필터링하거나 이스케이핑 하지 못했을 경우에 발생하며 공격난이도에 비해 파괴력이 무시무시하기 때문에 DB관리자, 웹 개발자라면 반드시 알아야 할 보안 위협입니다.  

## 공격 유형
### 1. Error-based
가장 많이 쓰이는 대중적인 유형입니다.  

예를 들어 로그인 화면이 있다고 가정해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/118385667-fdb17500-b64b-11eb-934b-7c53822d05b4.png)  

뒷단의 로그인을 위한 쿼리는 다음과 비슷하게 짜져 있을 겁니다.  
~~~
stmt.executeQuery("SELECT * FROM users WHERE user='"+user+"' AND pass='"+pass+"'")
~~~

정상 쿼리 :   
~~~
SELECT * FROM users WHERE user='bob' AND pass='secret'
~~~
정상적으로 user이름과 password가 들어가 있습니다.


SQL Injection 쿼리: 
~~~
SELECT * FROM users WHERE user='' OR 1=1;--' AND pass=''
~~~
user이름에 "`' OR 1=1;--`", password에 "`null`"을 넣어,  
- `OR 1=1` : WHERE 절을 모두 참으로 만듬
- `;--` : 뒤의 구문을 모두 주석처리
결과적으로 users 테이블의 모든 정보를 조회함으로써 가장 먼저 만들어진 계정으로 로그인에 성공하게 됩니다.  

보통 관리자 계정을 가장 먼저 생성하므로, 관리자 계정이 탈취되어 다른 피해를 야기시킬 수도 있습니다.  

### 2. UNION-based
SQL에서 **UNION**은 두 개의 쿼리문을 통합하여 하나의 테이블로 보여주게 하는 키워드 입니다.  

~~~
SELECT name, text FROM log WHERE date='2018-04-01'UNION SELECT user, password FROM users --'
~~~

원래는 `log`테이블에서 설정한 `date`에 맞춰 `name`과 `text`를 출력하는 구문이지만,  

SQL Injection으로 `date`항목에 `2018-04-01'UNION SELECT user, password FROM users --`구문을 끼워넣었습니다.  
Injection된 구문이 성공하게 되면 `log`테이블에서 18년 4월 1일 name과 text를 출력하고, `users`테이블에서 **user와 password를 모두 출력**하게 됩니다.   

> **UNION-based Injection이 성공하려면:**    
>- 두 테이블의 **컬럼수**가 같아야 함
>- 두 테이블의 **데이터 형**이 같아야 함

### 3. Blind injection
Blind Injection은 DB로부터 특정 값이나 데이터를 전달받지 않고, 많은 쿼리를 실행하여 원하는 항목의 값을 추론할 수 있는 방법입니다.   

**1. Boolean based SQL**  
쿼리의 응답값이 단순히 참과 거짓의 정보만 알 수 있을 때 사용할 수 있는 방법입니다.  

![image](https://user-images.githubusercontent.com/15958325/118389278-25acd280-b664-11eb-80d8-3b90033d4594.png)  
> 사진출처 : [SQL Injection 이란? (SQL 삽입 공격)/NoirStar](https://noirstar.tistory.com/264)  

위의 그림은 Blind Injection을 사용하여 DB의 테이블 명을 알아내는 사진입니다.  

정상대로라면 `id`값에 사용자의 id가 들어가고 `password`에 password값이 들어가 `User`테이블에서 검색하는 작업을 시도할텐데,  

해커가 아무렇게나 가입한 자신의 아이디 'abc123'을 가지고 INPUT1에 빨간색으로 칠해진 코드를 삽입하였습니다!  
삽입된 코드:   
~~~
abc123’ and ASCII(SUBSTR(SELECT name From information_schema.tables WHERE table_type=’base table’ limit 0,1),1,1) > 100 --  
~~~

1. `SELECT name From information_schema.tables WHERE table_type=’base table’ limit 0,1` : `information_schema.tables`테이블에서 `table_type`이 base table인 값을 찾아 name을 반환하는데 0번째부터 1개의 값만 반환합니다.  
2. `SUBSTR(1번에서 나온 table name 1개),1,1` : table name의 1번째 위치에서 1개의 글자를 반환합니다(첫 번째 글자만 반환)  
3. `ASCII(table name의 첫 번째 글자) > 100` : 첫 번째 글자를 ASCII코드로 변환하여 비교! 참이라면 로그인이 성공할 것이고 거짓이라면 로그인이 실패할 것입니다.  

이런 작업을 스크립트로 만들어서 반복한다면 쉽게 테이블의 이름을 추론할 수 있을 것입니다.  

> 이건 여담인데... SQL을 졸업 이후로 처음봐서 그런가 기억이 가물가물해서... 왜 limit은 0부터 시작하고 substr은 1부터 시작하는걸까요...

**2. Time based SQL**  
위의 예시가 참과 거짓을 바탕으로 추론했다면 Time based SQL에서는 결과값이 반환되는 시간으로 추론하는 방법을 사용합니다.  

![image](https://user-images.githubusercontent.com/15958325/118394889-69aed000-b682-11eb-9f5b-694adfaa2d9f.png)  
> 사진출처 : [SQL Injection 이란? (SQL 삽입 공격)/NoirStar](https://noirstar.tistory.com/264)  

위와 마찬가지로 해커는 임의의 계정 'abc123'을 가지고 공격을 시도합니다.  

삽입된 코드:  
~~~
abc123’ OR (LENGTH(DATABASE())=1 AND SLEEP(2)) --
~~~

1. `DATABASE()` : 현재 사용중인 데이터베이스의 이름을 반환  
2. `LENGTH(DATABASE())=1` : DATABASE이름의 길이를 반환하여 지정한 숫자(1)와 일치하는지 비교
3. `AND SLEEP(2)` : 참이라면 2초동안 정지했다가 로그인이 성공할 것이고, 거짓이라면 바로 로그인이 성공할 것입니다.  

이런식으로 database 이름의 길이를 알아낼 수 있습니다.  

이 외에도 여러 Injection 공격방법이 널렸지만 이번 포스팅에서는 여기까지만 소개하고 이제 어떻게 Injection을 예방할 수 있는지 알아보겠습니다!  

## SQL Injection 예방하기!
### 1. Prepared Statement 구문을 사용하자
대부분의 Injection 공격은 SQL 쿼리가 텍스트로 함께 묶여있기 때문에 발생하게 됩니다.  

아래와 같이 쿼리를 실행하는 대신에 :    
~~~java
stmt.executeQuery("SELECT * FROM users WHERE user='"+user+"' AND pass='"+pass+"'")
~~~

Prepared statement구문을 사용해서 쿼리를 실행시키는 것을 권장합니다.  
~~~java
PreparedStatement ps= conn.prepareStatement("SELECT * FROM users WHERE user = ? AND pass = ?");
ps.setString(1, user);
ps.setString(2, pass);
~~~

왜 안전한지 추가적으로 설명하자면...

아래 사진은 SLECT쿼리의 실행 과정입니다. 웹 상에서 입력된 쿼리는 DBMS내부적으로 4가지 단계를 통해 결과를 출력합니다.  
![image](https://user-images.githubusercontent.com/15958325/118395443-7a147a00-b685-11eb-80a0-10dfcc8b7796.png)  
> 사진 출처 : [인포섹 공식블로그/Prepared Statement를 쓰면 SQL인젝션 공격이 되지 않는 이유는?](https://m.blog.naver.com/PostView.nhn?blogId=skinfosec2000&logNo=220482240245&proxyReferer=https:%2F%2Fwww.google.com%2F)  


쿼리의 문법을 검사하기 위해서는 parse단계를 통해 문법을 분석하게 되는데요   

Prepared Statement를 사용하게 되면 사용자의 입력값이 DB의 파라미터로 들어가기 전에 미리 컴파일하여 대기합니다.  
쿼리의 **문법 처리 과정이 선수**되기 때문에 입력값은 더이상 SQL의 문법적인 의미가 없는 **단순 문자열**이 되고, 전체 쿼리문도 공격자의 의도대로 동작하지 않게 됩니다.  

### 2. Input Validation
OS Command Injection에서 언급했듯이, SQL Injection도 Input에 대한 Validation이 필요합니다.  

Blacklist가 아닌 Whitelist로요!  

### 3. DB의 에러메세지를 user에게 노출시키지 말 것
SQL Injection을 수행하기 위해서는 DB의 정보(테이블 명, 컬럼명 등)가 필요합니다.  
DB 에러 발생 시, 메세지에 따로 처리를 해주지 않을 경우 테이블명이나 컬럼명같은 정보가 유출될 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/118396404-64ee1a00-b68a-11eb-8135-f52b205b78f3.png)  

때문에 에러 메세지 핸들링시 사용자에게 보여줄 페이지 또는 메세지 박스를 띄우도록 해야 합니다.  

### 4. DB에 대한 user의 권한 제한
사용자의 권한을 제한적으로 두게 되면 SQL Injection공격이 들어와도 피해를 최소화 시킬 수 있습니다.  

read-only권한만 부여한다던지 각 operation마다 다른 user를 사용한다던지 하는 방법을 생각해볼 수 있을겁니다.  

# Other Types of Injection
지금까지 OS Command, SQL Injection에 대해서 알아보았습니다. 이 두 종류이외에도 여러 종류의 Injection공격이 존재하는데요!  

짧게 알아보도록 하겠습니다.  

## NoSQL Injection
NoSQL DB중 MongoDB에서는 `$where`파라미터가 javascript로 처리됩니다.  

예를 들어 `$where`파라미터의 input을 다음과 같이 받는다고 합시다.  
~~~js
$where: "$expression"
~~~
일반적인 경우 전혀 위험하지 않은 구문이지만, `$expression`에 다음과 같은 구문을 삽입한다면:  
~~~js
$where: "d = new Date; do {c = new Date;} while (c-d<100000);"
~~~
DOS 공격을 수행시켜 시스템을 마비시킬수도 있습니다.  

## XPath Injection
XPath란 XML문서의 특정 요소나 속성에 접근하기 위한 경로를 지정하는 언어입니다.  

예를 들어 로그인을 하는데 XPath 표현식이 다음과 같다고 해봅시다.  
~~~
"//Employee[UserName/text()='" + Request("Username") + "' And Password/text()='" + Request("Password") + "']"
~~~

일반적이라면 user와 password를 정확하게 입력하여 다음과 같은 형태가 되었을 것입니다.  
~~~
"//Employee[UserName/text()='abc' And Password/text()='secret']"
~~~

하지만 이 경우 SQL Injection과 유사하게 malicious한 구문을 추가하여 공격을 시도할 수 있습니다.  
~~~
"//Employee[UserName/text()='' or 1=1 or '1'='1' And Password/text()='secret']"
~~~
추가된 구문: `' or 1=1 or '1'='1`  

## LDAP Injection
LDAP(Light Directory Access Protocol)은 일반적으로 user 정보를 다루는 프로토콜로 사용됩니다.  

이 프로토콜에서는 다음과 같은 표현식을 사용하여 user를 찾습니다.  
~~~
find ("(&(cn=" + user +")(password=" + pass +"))")
~~~
일반적인 경우 다음과 같은 형태가 될 것입니다.  
~~~
find ("(&(cn=abc)(password=secret))")
~~~

하지만 역시나 타 Injection공격과 유사하게 malicious한 구문을 추가하여 공격을 시도할 수 있습니다.  
~~~
find ("(&(cn=*)(cn=*))(|(cn=*)(password=any))")
~~~
추가된 구문 : `*)(cn=*))(|(cn=*`  

타 Injection공격도 위에서 언급했던 OS Command, SQL Injection 예방방법과 비슷하게 예방할 수 있습니다.  

해커는 똑똑하고 창의적이니 다양한 위협이 있을 수 있다는 점을 인지하고 코드를 짤때 이 점을 숙지하고 개발하는 것이 중요한 것 같습니다!

# Wrap-Up

## 요약 -OS Command Injection
- **OS Command는 사용하지 말 것!**
- 최소의 권한을 가진 유저로 실행할 것
- shell interpreter는 사용하지 말 것
- OS Command를 사용할 때에는 안전한 library를 사용할 것
- 사용자의 입력이 command실행에 영향을 끼치지 못하게 할 것
- **반드시 Input Validation을 할 것!!**

## 요약 -SQL Command Injection
- prepared statement를 사용할 것
- **반드시 Input Validation을 할 것!!**
- DB의 error message를 사용자에게 노출시키지 말 것
- user의 권한을 제한적으로 부여할 것

----