---
title: "10.Using Grafana & InfluxDB in Sawtooth"
categories: 
  - Sawtooth-Starter
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for ubuntu(18.03.01-ce)에서 다루며 os는 ubuntu-18.04 LTS임`

## 1. Overview
이번 문서에서는 Grafana를 사용해 sawtooth의 모니터링을 할 수 있게 해보겠습니다.  


## 2. Prerequisites

sawtooth-core의 클론

## 3. Set up InfluxDB

다음 커맨드를 통해 Docker Hub로부터 이미지를 받습니다.
~~~
$ docker pull influxdb
~~~

다음으로는 로컬파일시스템에 InfluxDB의 저장공간을 만들어줘야 합니다.
~~~
$ sudo mkdir /var/lib/influx-data
~~~

폴더까지 만들어줬으면 도커에서 실행시켜봅시다!
~~~
$ docker run -d -p 8086:8086 -v /var/lib/influx-data:/var/lib/influxdb \
 -e INFLUXDB_DB=metrics -e INFLUXDB_HTTP_AUTH_ENABLED=true \
 -e INFLUXDB_ADMIN_USER=admin -e INFLUXDB_ADMIN_PASSWORD='{admin-pw}' \
 -e INFLUXDB_USER=lrdata -e INFLUXDB_USER_PASSWORD='{lrdata-pw}' \
 --name sawtooth-stats-influxdb influxdb
~~~
`INFLUXDB_DB`: DB이름  
`INFLUXDB_HTTP_AUTH_ENABLED`: DB에 접근하기위한 인증절차   
`INFLUXDB_ADMIN_USER` & `INFLUXDB_ADMIN_PASSWORD`: 관리자계정  
`INFLUXDB_USER` & `INFLUXDB_USER_PASSWORD`: 일반계정


> ** `INFLUXDB_HTTP_AUTH_ENABLED`에 관하여...  
>이게 로컬에서 할 때는 별 문제없이 작동하다가 원격으로 서버에 접근하려고 할때 인증메세지가 뜨는데 저는 뭘 넣어도 인증이 안됬어요... (*서버의 슈퍼계정, 할당받은 서버계정, influxDB의 관리자계정, influxDB의 유저계정)  
> <b>그래서 이 속성은 빼고 진행을 했습니다.</b> 혹시 이 문제에 대해서 뭔가 아시거나 해결하신분은 메일주세오...  
>sygy0509@naver.com
>
> ![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/1.PNG)

## 4. Install and Configure Grafana

 sawtooth-core에 포함된 Grafana Docker이미지를 찾고 빌드합니다.
 ~~~
 $ cd sawtooth-core/docker
 $ docker build . -f grafana/sawtooth-stats-grafana \
 -t sawtooth-stats-grafana
 ~~~

다음은 Grafana를 도커에서 실행!
~~~
$ docker run -d -p 3000:3000 --name sawtooth-stats-grafana \
 sawtooth-stats-grafana
~~~

실행시켰다면 그라파나를 실행시킨 호스트의 주소:포트3000 (`http://{host}:3000`)으로 접속해봅시다!  

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/2.PNG)  
초기 관리자 계정인 `id: admin`, `pwd: admin`으로 로그인이 가능합니다.  
(*관리자 계정의 비밀번호를 바꾸는건 기본!)

다음으로 Grafana에 아까 실행시켰던 InfluxDB를 연동시켜야 합니다.  좌측상단 아이콘을 누른 뒤 "Data Sources"클릭 -> "Metrics"클릭하시면 다음과 같은 화면이 뜹니다.  

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/3.PNG)

HTTP Settings->`URL`: influxDB가 실행되는 호스트와 포트(8086)  
InfluxDB Details->`Database`: influxDB의 이름  
InfluxDB Details->`userInfo`: influxDB의 유저정보(없어도됨)  
다음과 같이 설정해 주시고 `Save&Test` 버튼을 클릭하면 연동이 성공하게 됩니다.

## 5. Configure the Sawtooth Validator&REST API for Grafana

이제 Grafana와 InfluxDB의 연동이 성공하였으니 Sawtooth네트워크와 연동해야합니다.  
>[공식문서](https://sawtooth.hyperledger.org/docs/core/nightly/master/sysadmin_guide/grafana_configuration.html#configure-the-sawtooth-validator-for-grafana)에서는 docker가 아닌 우분투위에서 sawtooth네트워크를 실행하기 때문에 toml파일을 수정하는 방법을 설명하고 있습니다.
>저는 docker위에서 sawtooth를 실행시키므로 yaml파일을 수정하는 방법을 소개하겠습니다.

실행시킬 sawtooth네트워크의 docker-compose.yaml파일을 수정해봅시다.  

먼저 validator부분을 봅시다.
~~~
  validator:
    build:
      context: .
      dockerfile: validator/Dockerfile
    image: sawtooth-validator-local:${ISOLATION_ID}
    volumes:
      - ./:/project/sawtooth-core
    container_name: sawtooth-validator-local
    expose:
      - 4004
      - 8008
      - 8086
    ports:
      - "4004:4004"
    # start the validator with an empty genesis batch
    command: |
      bash -c "
        bin/protogen
        cd validator
        python3 setup.py clean --all
        python3 setup.py build
        mkdir -p bin
        mkdir -p lib
        cargo build --release
        cp ./target/release/sawtooth-validator bin/sawtooth-validator
        cp ./target/release/libsawtooth_validator.so lib/libsawtooth_validator.so
        sawadm keygen
        sawtooth keygen
        sawset genesis
        sawadm genesis config-genesis.batch
        sawtooth-validator -v \
            --endpoint tcp://localhost:8800 \
            --bind component:tcp://eth0:4004 \
            --bind network:tcp://eth0:8800 \
            --bind consensus:tcp://eth0:5050 
      "
    stop_signal: SIGKILL
~~~
제가 사용하고 있는 yaml파일의 validator입니다. 다른부분은 필요없고 이 부분을 수정하시면 됩니다.
~~~
sawtooth-validator -v \
            --endpoint tcp://localhost:8800 \
            --bind component:tcp://eth0:4004 \
            --bind network:tcp://eth0:8800 \
            --bind consensus:tcp://eth0:5050 \
            --opentsdb-url http://{influxdb}:8086 \
            --opentsdb-db metrics
~~~
`--opentsdb-url`: influxDB가 실행되고 있는 호스트의 주소:포트  
`--opentsdb-db` : influxDB의 이름

다음은 REST-API부분
~~~
 rest-api:
    build:
      context: .
      dockerfile: rest_api/Dockerfile
    image: sawtooth-rest-api-local:${ISOLATION_ID}
    volumes:
      - ./:/project/sawtooth-core
    container_name: sawtooth-rest-api-local
    ports:
      - "8008:8008"
    depends_on:
      - validator
    command: |
      bash -c "
        bin/protogen
        cd rest_api
        python3 setup.py clean --all
        python3 setup.py build
        sawtooth-rest-api -v --connect tcp://validator:4004 --bind rest-api:8008 
      "
    stop_signal: SIGKILL
~~~

validator와 마찬가지로 rest-api의 커맨드를 수정해주시면 됩니다.
~~~
 sawtooth-rest-api -v --connect tcp://validator:4004 --bind rest-api:8008 --opentsdb-url http://{influxDB}:8086 --opentsdb-db metrics
~~~

> ** 일부 속성 문제에 대하여...  
> 공식문서의 toml파일을 수정하는 부분을 보시면 속성이 두 개가 더있습니다. `opentsdb_username`이랑 `opentsdb_password`인데요.. sawtooth개발자분들이 의도적으로 빼두신건지 아니면 까묵은건지 sawtooth-validator의 CLI에는 저 두 속성이 존재하지 않습니다.  
>물론 이 둘을 없애도 잘 돌아가긴 합니다. 저는 빼고 진행했습니다.

-->수정 후, sawtooth네트워크 실행!

## 6. Configure Telegraf

Telegraf는 InfluxDB의 제작사에서 제작한 시스템 모니터링 및 지표 수집 에이전트입니다. 간단히 말해서 sawtooth네트워크와 os의 여러 정보를 InfluxDB로 보내주는 역할을 합니다.

그럼 Telegraf를 다운로드 받아봅시다.
~~~
$ curl -sL https://repos.influxdata.com/influxdb.key |  sudo apt-key add -
$ sudo apt-add-repository "deb https://repos.influxdata.com/ubuntu xenial stable"
$ sudo apt-get update
$ sudo apt-get install telegraf
~~~

다운로드가 끝났다면 InfluxDB와 연결하기 위해 Telegraf의 속성을 수정하여야 합니다.
~~~
$ sudo vim /etc/telegraf/telegraf.conf
~~~
파일을 열어서 `OUTPUT PLUGINS`을 찾은다음 다음 속성을 추가합시다.
~~~
# Configuration for sending metrics to InfluxDB
[[outputs.influxdb]]
  urls = ["http://{influxDB host}:8086"]
  database = "metrics"
~~~
이후, telegraf 명령어를 입력하면 준비완료!
~~~
$ telegraf
~~~


## 7. Grafana

### 7.1 Graph 
sawtooth네트워크를 올려봅시다. 별 문제가 없다면 다음과 같은 화면이 뜰 것입니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/4.PNG)  
하단에 빨간색으로 표시한 줄은 오류가 아니에요!  
저는 Bad Request가 떠서 제대로 연결이 되지 않았나 해서 온갖 삽질을 했지만^^... 
 validator에서 전달되는 값이 없어서 그런것 같습니다.  

 그럼 바로 xo게임을 시험삼아 실행해서 게임을 진행해봅시다. [참고](https://github.com/GRuuuuu/sawtooth-starter/tree/master/sawtooth/%232%20xo%20transaction%20family)

 트랜잭션을 발생시키고 블록이 생성된 것을 확인했으면 Grafana페이지로 가서 Dashboard를 확인해봅시다!  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/5.PNG)  
네트워크를 올리고 얼마 시간이 지나지 않아서 그래프가 많이 빈약하지만 그래프의 생성유무를 확인할 수 있습니다.    

또한, 그래프에 마우스를 올려놓으면 세부 사항도 확인할 수 있습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/6.PNG)

실시간 모니터링(Auto-Refresh)은 Dashboard 우측 상단 시계를 클릭해서 설정할 수 있습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/7.PNG)  
5초로 설정하면 5초마다 그래프가 새로고침됩니다.

### 7.2 User

Dashboard를 볼 수 있는 유저를 추가하는 방법입니다.  
좌측상단 똥글뱅이문양을 누르고 Admin->Grobal Users->Add new User  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/8.PNG)  
정보를 기입하고 생성을 누르면 다음과 같이 유저계정을 만들 수 있습니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2310%20using%20grfana%20%26%20influxdb/img/9.PNG)  
생성한 유저의 권한 관리는 우측의 Edit버튼을 통해 관리할 수 있습니다.

## 8. 마치며

sawtooth공식 doc에 있는 내용을 거의 다 해봤네요! 꺄오꺄오! 다음에 또 만나요!

---

---