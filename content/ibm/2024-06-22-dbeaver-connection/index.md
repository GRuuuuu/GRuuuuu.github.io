---
title: "DBeaver에 Presto와 Db2 붙여보기"
slug: dbeaver-connection
tags:
  - DB
  - DataScience
date: 2024-06-22T13:00:00+09:00
---

## Overview
개발과 작업의 편의성을 위해 GUI가 필요한 경우가 있습니다.  
SQL client이자 데이터베이스 관리도구인 **DBeaver**에 `Presto`와 `Db2`를 붙이는 과정에 대해서 정리하겠습니다.  

> 본 문서에서는 Openshift위의 `Db2`, Openshift위의 Cloud Pak for Data위의 WatsonX.data위의 `Presto`를 다루고 있지만 다른 환경에서도 필요한 정보는 동일할테니 참고용으로 보시면 될 것 같습니다.  

## Db2 SSL connection
### 1. certificate 뽑기
Db2의 ssl-server port(ex.50001)로 연결되는 route를 생성합니다.  

~~~
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  namespace: dbwh
  name: dbwh
spec:
  to:
    kind: Service
    name: c-db2wh-db2u-engn-svc
    weight: 100
  port:
    targetPort: ssl-server
  tls:
    termination: passthrough
  wildcardPolicy: None
~~~

그럼 443->50001로 연결되는 https endpoint가 생성될텐데요,  
~~~
https://db2wh-dbwh.apps.endpoint.com
~~~

`openssl`로 해당 endpoint에 대한 certificate를 추출해주면 됩니다.  
~~~
openssl s_client -showcerts -connect db2wh-dbwh.apps.endpoint.com:443
~~~
rootCA와 그와 연결된 chain CA를 모두 추출해 `chain.pem` 파일로 생성합니다.  

### 2. Java trust KeyStore 생성
DBeaver설치 시 같이 설치되는 `keytool` 커맨드를 통해 jks파일을 생성합니다.   
~~~
$ "C:\Program Files\DBeaver\jre\bin\keytool.exe" -import -alias mydb2demo -file /path/to/chain.pem -storetype JKS -keystore mydb2demo.jks
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/1.png)

### 3. DBeaver Connection 
필요한 정보를 기입해줍니다.  
https연결이므로 포트는 기본 443,   
연결하고자하는 DB이름, 권한을 가진 유저의 정보를 입력해줍니다.    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/2.png)   


다음 Driver Properties탭으로 이동하여 ssl관련 정보들을 기입해줍니다.    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/3.png)   

`sslConnection` : true  
`sslTrustStoreLocation`: 위에서 만든 jks파일의 위치  
`sslTrustStorePassword`: 위에서 만든 jks파일의 비밀번호   

테스트연결할때 아래와 같은 에러가 발생하면   
~~~
[jcc][t4][2030][11211][4.33.31] A communication error occurred during operations on the connection's underlying socket, socket input stream, 
or socket output stream.  Error location: Reply.fill() - socketInputStream.read (-1).  Message: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target. ERRORCODE=-4499, SQLSTATE=08001
  PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
  PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
    unable to find valid certification path to requested target
    unable to find valid certification path to requested target
~~~  

윈도우 > 설정 > 연결 > use Windows trust store의 체크를 해제하고 DBeaver를 재시작한 뒤 다시 시도하면 됩니다.   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/4.png)   

이래도 안된다면 인증서가 valid한 녀석인지 다시한번 확인!   

연결 성공!   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/5.png)    


## Presto SSL connection
### 1. certificate 뽑기
> 위 Db2 connection처럼 route를 만들고 인증서를 추출 -> jks로 생성해도 되지만 이 문서에서는 Presto의 truststore.jks를 직접 pod에서 가져와서 연결하는 방법을 기술하겠습니다.  

presto coordinator pod에서 truststore.jks를 찾습니다.  
~~~
sh-5.1$ cd /mnt/infra/tls
sh-5.1$ ls
ca.crt  keystore.p12  lh-ssl-ks.jks  lh-ssl-ts.jks  pki  tls.crt  tls.key  truststore.jks  truststore.p12
~~~

truststore.jks를 로컬로 복사, path를 기억해둡니다.  

### 2. DBeaver Connection 
필요한 정보를 기입해줍니다.  
https연결이므로 포트는 기본 443,   
연결하고자하는 스키마의이름, 권한을 가진 유저의 정보를 입력해줍니다.    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/6.png)    

다음 Driver Properties탭으로 이동하여 ssl관련 정보들을 기입해줍니다.    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/7.png)   

`SSL` : True  
`SSLTrustStorePath`: 위에서 만든 jks파일의 위치  
`SLLTrustStorePassword`: 위에서 만든 jks파일의 비밀번호 (기본은 changeit)    


연결 성공!   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-22-dbeaver-connection.md/8.png)   


----