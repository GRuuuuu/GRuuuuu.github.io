---
title: "ZeroSSL에서 무료 인증서 발급받기"
slug: openssl
tags:
  - Network
  - ssl
date: 2020-10-03T13:00:00+09:00
---

## Overview

**SSL(Secure Sockets Layer)**은 클라이언트와 서버간의 통신을 제3자가 보증해주는 전자화된 문서입니다.  

클라이언트가 서버에 접속한 직후, 서버는 클라이언트에게 해당 인증서 정보를 전달하고, 클라이언트는 받은 인증서 정보가 신뢰할 수 있는지 검증한 이후에 안전한 연결을 할 수 있게 됩니다.  

현재 인터넷 연결은 HTTPS로 연결하는 것을 권장하고있습니다. HTTPS는 SSL위에서 돌아가는 프로토콜 중 하나이기때문에 HTTPS로 데이터 전송을 하려면 SSL이 제공하는 데이터 보안이 반드시 필요합니다.  

이번 문서에서는 공인된 ssl을 무료로 발급받을 수 있는 방법에 대해서 기술하겠습니다.  

# ZeroSSL
90일간의 SSL인증서를 3개까지 무료로 발급해주는 사이트입니다.  

보통 1년 2년 단위로 발급받는 유료 인증서에 비해 90일이라는 짧은 기간이긴 하지만 무료로 사용할 수 있다는게 큰 장점인것 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/94986271-5e49e100-0598-11eb-9d29-96d8ad7772e8.png)  

ZeroSSL 무료 인증서 :   
- 90일
- 3개까지 생성가능
- wildcard인증서 안됨

## SSL발급받기
회원가입 후, Dashboard에서 New Certificate 버튼을 클릭합니다.  
![image](https://user-images.githubusercontent.com/15958325/95009526-b860aa00-065d-11eb-8356-f924550e8a36.png)  

그 다음, ssl발급을 원하는 도메인을 기입합니다. 이때 와일드카드는 선택하지 않도록 합니다. (와일드 카드는 유료플랜)  
![image](https://user-images.githubusercontent.com/15958325/95009540-d6c6a580-065d-11eb-90d0-e2f2e65c6419.png)  


다음 90일 certificate를 선택해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/95009344-4b98e000-065c-11eb-9c55-108c46b086b5.png)  

넥스트를 한 후 이제 도메인이 유효한 도메인인지 검증을 해야합니다.  

![image](https://user-images.githubusercontent.com/15958325/95009365-7c791500-065c-11eb-836c-467706a1c262.png)  

방법은 위와 같이 3가지 방법이 있습니다.  
1. Email Verification
    - DNS에 작성된 메일서버(관리자용)로 메일발송 및 검증
2. DNS(CNAME)
    - DNS에 zerossl에서 주는 CNAME레코드를 추가하는걸로 검증
3. HTTP File Upload
    - zerossl에서 원하는 파일경로에 파일을 업로드시키고 다운로드 가능하게 설정하는걸로 검증 

이중에서 저는 2번방법을 써서 검증해보겠습니다.  

가지고 있는 DNS의 레코드에 zerossl에서 주는 CNAME레코드를 추가해줍니다.  
주의해야할 점은, Name부분의 도메인은 떼고 넣어주셔야 합니다.  
![image](https://user-images.githubusercontent.com/15958325/95009660-c82cbe00-065e-11eb-8376-0f5cd1b23ab7.png)    

>ex)  
>_038AB2F4959BEF94DBE168E1C9A95716.registry.gru.hololy-dev.com 이렇게 있으면 뒤에 `hololy-dev.com`은 떼고  
>_038AB2F4959BEF94DBE168E1C9A95716.registry.gru 만 적으면 됨.  

레코드를 추가해주고 외부에서 `nslookup`같은 도구로 제대로 추가되었는지 확인해주겠습니다.  
`nslookup`은 기본적으로 A레코드를 찾기 때문에 `set type=CNAME`을 해줘 CNAME레코드를 찾게 설정해주어야 합니다.  
![image](https://user-images.githubusercontent.com/15958325/95010133-ed6efb80-0661-11eb-9f7c-3e7b35083117.png)  

target url이 정상적으로 출력되었다면 Validation을 해주고 인증서를 받으시면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/95010167-2018f400-0662-11eb-9938-3120c3ddcef8.png)  
![image](https://user-images.githubusercontent.com/15958325/95010170-21e2b780-0662-11eb-9396-1e27d06ffc66.png)  

마지막으로 ssl 설치를 체크하는 부분이 있는데, 이부분은 그냥 넘어가셔도 됩니다.  

----
