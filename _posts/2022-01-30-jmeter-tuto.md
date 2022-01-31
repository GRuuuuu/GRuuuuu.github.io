---
title: "[JMeter]JMeter Basics"
categories:
  - Testing
tags:
  - Jmeter
  - Performace
  - Testing
last_modified_at: 2022-01-30T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview
애플리케이션이 성능 요건을 충족하는지, 병목현상을 유발하는 곳은 어딘지, 많은 트래픽 이벤트에서 안정성은 충분한지 측정하기 위해 여러 **테스트**를 진행합니다.  

이번 문서에서는 성능/부하/스트레스 테스트를 위한 툴 중 하나인 **Apache JMeter**에 대해서 알아보도록 하겠습니다.  

# Testing
먼저 비슷하지만 약간씩 다른 용어들을 정리하고 넘어가도록 하겠습니다.  
## Testing
### Performance Test(성능)
시스템에서 수용 가능한 처리량을 판별하기 위한 테스트   

- 응답속도나 단위 시간당 일 처리량 등을 측정
- 기존 시스템에 대한 '성능'을 측정하는 테스트  
- 성능 측정을 위해 실제 사용될 것과 같은 환경에서 작동  

### Load Test(부하)  
임계치에 도달할 때까지 시스템에 부하를 꾸준히 증가시키며 진행하는 테스트   

- 부하 상황에서 시스템이 어떻게 동작하는지 모니터링  
- WAS, DB, Network IO나 여러 서버로의 로드밸런싱 등 모든 요소의 한계를 찾아서 미래에 발생할 부하에 대비하는 것이 목표  

### Stress Test(스트레스)  
시스템이 과부하 상태에서 어떻게 작동하는지를 검사하는 테스트   
- 과부하상태에서의 시스템의 안정성, 이용가능성, 오류 관리등을 모니터링  
- 장애 조치와 복구 절차가 효과적이고 효율적인지   

### Spike Test 
사용자가 갑자기 몰렸을 때, 요청이 정상적으로 처리되는지 그리고 부하가 줄어들 때 정상적으로 반응하는지 확인하는 테스트   

### Stability / Soak Test
긴 시간동안 테스트를 진행
- 시간에 따른 시스템 리소스 변화를 측정
- 짧게는 1-2시간, 길게는 며칠동안 진행  

성능을 측정한다는게 여러 의미로 생각될 수 있기 때문에, **성능테스트가 아래의 테스트들을 포함하는 큰 개념**이라고 보시면 됩니다.  
테스트 목적에 따라 여러 테스트로 나뉘어 불리게 됩니다.  

# JMeter 

## JMeter?

>**참고**  
>[APACHE JMeter doc](https://jmeter.apache.org/)  
>[JMeter User's Manual](https://jmeter.apache.org/usermanual/index.html)  

**Apache JMeter**는 웹 어플리케이션처럼 클라이언트-서버 구조로 된 소프트웨어의 성능 테스트를 위해 만들어진 순수 JAVA 프로그램입니다.  

위에서 언급했던 테스트들을 **JMeter**를 통해 전부 해볼 수 있으며, `TCP`, `HTTP(S)`, `FTP`, `JDBC`, `LDAP`, `SMTP` 등 범용으로 사용되는 프로토콜 대부분을 지원합니다.  

**특징**  
- 통신 프로토콜 단계에서만 동작, 일반적인 클라이언트에서 행해지는 **연산동작은 수행하지 않음**. (통신 규약에 맞도록 클라이언트-서버 간 메세지만 송수신)  
- JVM위에서 동작   
- CLI/GUI 모두 지원  
- 사용자 Plugin이 많음   

## Tutorial
### Installation
>**실습환경**  
>OS : Window 10 pro  
>CPU : 4  
>RAM : 32GB

**JMeter는 자바 어플리케이션이므로 반드시 실습환경에 JAVA가 설치되어 있어야 합니다!!!**

Download Link : [https://jmeter.apache.org/download_jmeter.cgi](https://jmeter.apache.org/download_jmeter.cgi)  

OS에 맞는 버전을 다운로드 받아줍니다.  

Window의 경우 jmeter.bat 실행  
![image](https://user-images.githubusercontent.com/15958325/151743902-d5c72a0b-ff45-4cdc-8b9b-c009eba5f51a.png)  

그럼 바로 뿅 하고 Jmeter가 뜨게 됩니다!    
![image](https://user-images.githubusercontent.com/15958325/151743955-ca42fdb1-8b09-493a-8010-a285a167d592.png)  

### Test Plan 짜기  
**Test Plan**은 JMeter를 실행할 때 기본적으로 뜨는 가장 상위 객체이자 각 테스트들의 묶음이라고 보시면 됩니다.  
Test Plan에는 하위 테스트들에 적용될 변수, 하위테스트를 한번에 또는 각각 실행할 것인지에 대한 여부를 결정할 수 있습니다.  

### Thread Group 생성   
**Thread Group**은 테스트 하나를 묶는 객체입니다. 하위 Element를 제어하는 시작점이라고 보시면 됩니다.  

Test Plan > Add > Thread > Thread Group   
![image](https://user-images.githubusercontent.com/15958325/151745589-2e78a5b9-497e-4a92-b28c-34c6445d7faa.png)  

생성하면 아래와 같이 항목들이 나옵니다.  
![image](https://user-images.githubusercontent.com/15958325/151745886-83712e77-248d-425f-9d0e-d5ec04e28d08.png)  

**Number of Threads** : 사용자 수  
**Ramp-up period** : 각 Thread를 균일하게 실행시키는 총 시간 (thread가 30개고 ramp가 120초면 120초안에 30개의 쓰레드를 돌리는거 -> 각 쓰레드 사이 딜레이 4초씩)  
**Loop Count** : Thread(사용자)가 행하는 작업의 반복횟수  

테스트를 얼마나 많은사용자가, 어느만큼 돌릴건지 정하고 나면, 이제 실제 테스트를 정의해야 합니다.  

### HTTP Request 
Controller는 테스트 절차를 제어하는 역할을 수행합니다.  

**Sampler** : Request를 Server에 전달하기 위한 도구  
**Logical Controller** : Request를 조작할 수 있는 로직  

먼저 HTTP Request Sampler를 하나 생성해보겠습니다.  

Thread Group > Add > Sampler > HTTP Request  
![image](https://user-images.githubusercontent.com/15958325/151748414-271227d0-409d-4752-abc9-4ee22391646e.png)   


<img width="769" alt="image" src="https://user-images.githubusercontent.com/15958325/151749107-f29ab37b-a333-469d-a8d4-35d1699278a0.png">  

Name과 Comments엔 해당 Request의 이름과 description을 적어주고,  

**Protocol**: 기본적으론 HTTP이고, HTTPS를 사용하려면 사진과 같이 적어주어야 합니다.  
**Server Name or IP** : Request를 보낼 서버의 정보를 기입합니다.  
**HTTP Request** : `GET`/`POST`/`HEAD`/`PUT`/`OPTIONS`/`TRACE`/`DELETE`/`PATCH` 중 원하는 방식을 선택합니다.  
**Path** : URL Path를 기입합니다. (ex. `GRuuuuu` -> `github.com/GRuuuuu`)  
**Parameters/BodyData** : 서버에서 파라미터 값을 어떻게 처리하느냐에 따라 선택 (Request의 Content type이 `application/json`라면 `body data` `application/www-x-form-urlencoded`라면 `parameters`)  

### Request 날릴 준비
준비된 웹서버가 있다면 테스트할 웹서버의 api 형식을 보고 넣으면 되고,  
저는 딱히 테스트해볼 서버가 없어서 구글 Translate의 POST Request를 넣어봤습니다.  

-> [구글번역](https://translate.google.com/)  

사이트로 이동해서 번역할때 사용하는 api의 path와 request header 정보를 먼저 파악해야 합니다.  

그다음 F12를 눌러서 브라우저의 개발자도구 > Network 탭으로 들어가줍시다.  
![image](https://user-images.githubusercontent.com/15958325/151759205-150dce87-cdb0-44ce-98bb-b5e04c79421d.png)  

그 다음, hello를 입력해서 한국어로 번역하는 요청을 잡아보도록 하겠습니다.  
![image](https://user-images.githubusercontent.com/15958325/151759049-3eaa61d7-8fd0-47bc-94cd-20cdc7d28a2a.png)  

들어온 요청들을 보다보면 `batchexecute`라는 이름의 요청이 있습니다.  
무슨일을 하는진 정확히 잘 모르겠지만, `Payload`와 `Response` 결과를 보면 이게 번역요청에 관련된 api라는 것을 알 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/151760093-9949a9f3-63f7-4219-88b9-59b321f3764d.png)  

요청을 날리기 위해서 봐야 할 부분은 `Request Header` 입니다.  
<img width="706" alt="image" src="https://user-images.githubusercontent.com/15958325/151760422-73f4810e-343b-4abe-b5ab-7726a1eed46a.png">  

`content-type`을 보니 body값을 JMeter의 `bodydata`가 아닌 `parameters`에 넣어야된다는 것도 알 수 있습니다.  

POST요청이니 body값을 확인하기위해 payload 탭을 눌러서 확인해줍니다.  

![image](https://user-images.githubusercontent.com/15958325/151761194-c67bbb03-cc8f-42c0-9d7f-2a1057df383f.png)  

그리고 마지막으로 Response값을 확인해봅니다.(테스트결과와 확인하기 위해)  
![image](https://user-images.githubusercontent.com/15958325/151762496-3d927fbd-e717-4916-9e20-fa8d82860136.png)  

이제 필요한 정보들은 다 모였으니 JMeter 테스트케이스를 만들어봅시다!   

### POST Request 날리기!  

<img width="764" alt="image" src="https://user-images.githubusercontent.com/15958325/151763243-804ef586-0f6a-4430-a546-e23830131d07.png">   

`Protocol` : https  
`ServerName or IP` : translate.google.com  
`HTTP Request` : POST  
`Path` : /_/TranslateWebserverUi/data/batchexecute?...8014&rt=c  
`Parameters` : 여기는 브라우저에서 확인한 `payload`값을 view source로 하고 복사한다음에 JMeter의 **Add from Clipboard**를 눌러 한번에 붙여넣기하시면 됩니다   

### Listener 추가   
**Listener**는 Request요청에 대한 Response Time추이 그래프나 실시간 Request/Response 응답을 확인할 수 있는 플러그인들을 제공해주는 툴입니다.  

종류가 많아서 이 문서에서는 두 종류의 Listner만 소개하겠습니다.  

#### View Results Tree   
Request에 대한 Response를 텍스트형태로 확인할 수 있습니다  

Thread Group > Add > Listenr > View Results Tree  
![image](https://user-images.githubusercontent.com/15958325/151764161-42291e35-00e9-424d-af20-d27e5543a939.png)  

그럼 빨간색으로 표시한 부분을 눌러 Request를 보내보겠습니다.  
<img width="332" alt="image" src="https://user-images.githubusercontent.com/15958325/151783887-87ce8522-e219-486b-bd89-2b52ae1fcd22.png">  

>Number of Threads: 1  
>Ramp-up period : 1   
>Loop Count : 1

200대 응답이 오면 초록색으로 뜨고 error응답이 오면 빨간색으로 뜹니다.  
![image](https://user-images.githubusercontent.com/15958325/151784104-b14578c7-af6a-49fa-8ffb-4488d23f1b2b.png)  

탭의 Response data를 선택하면 body에 어떤 데이터가 응답이 왔는지 확인할 수 있습니다.  

Request 탭에서는 실제 어떤 데이터를 보냈는지 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/151784343-8670a322-d275-4db6-9f4b-6357bda9b318.png)   

Result Tree로 정확한 Request를 보냈는지 확인하고 부하테스트를 진행하는것이 좋습니다.  

#### Graph Results
Request와 Response의 특정 항목들에 대한 그래프를 그려줍니다.  

Thread Group > Add > Listener > Graph Results   
![image](https://user-images.githubusercontent.com/15958325/151784539-8a9f2ff1-c183-475c-a34c-1b3d8fdf3158.png)  

그래프를 그리려면 Request를 많이 보내야 예쁜 그래프가 그려질테니 Thread Group의 수치를 조절해주도록 하겠습니다.  

>Number of Threads: 100  
>Ramp-up period : 100   
>Loop Count : 10

그러면 아래와 같이 그래프가 그려지게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/151785137-dc9819a7-281a-45b9-b63c-9254456c9100.png)  

`No of samples` : 총 Request한 sample수  
`Average` : Request한 sample의 평균  
`Deviation` : 표준편차  
`Throughput` : 서버의 처리량  

Throughput이 높을 수록 서버 성능이 좋고,  
Deviation은 평균과의 편차이므로 작을수록 좋습니다.  


----