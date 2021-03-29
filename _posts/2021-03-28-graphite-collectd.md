---
title: "Graphite와 Collectd를 사용해 모니터링하기!"
categories: 
  - LINUX
tags:
  - Monitoring
  - Graphite
  - Collced
  - Metric
last_modified_at: 2021-03-28T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---
## Overview
>이런 저런 일들이 있어 [2020회고](https://gruuuuu.github.io/docs/2021-01-08-2020/)를 제외하고는 올해 첫 게시글이네요!  
>이제 다시 꾸준히 작성해야 겠습니다. 오늘도 봐주셔서 감사합니다!

이번 포스팅에서는 시스템 모니터링을 할 때 자주 등장하는 `Graphite`와 `Collectd`가 무엇인지, 어떻게 메트릭들을 수집해서 그래프로 볼 수 있는지 살펴보겠습니다.  

# WHAT IS GRAPHITE?
**Graphite**는 시계열 데이터를 저장하고 핸들링하는데 특화된 Python베이스의 모니터링 툴입니다.  
크게 3가지 컴포넌트로 볼 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/112748380-3642b400-8ff6-11eb-91fb-0cc0d2ccf929.png)  

`Carbon` : 시계열 데이터를 수신하는 백엔드 데몬 (다른 collector에서 수집한 메트릭을 수신)   
`Whisper` : Carbon에서 넘겨받은 데이터를 저장하는 데이터베이스 (RRD와 비슷)    
`Graphite-Web` : 저장된 데이터를 웹에서 그래프로 확인 가능 (Django)   

컴포넌트를 보면 알 수 있지만, Graphite는 데이터를 수집하는 컴포넌트가 없습니다.  
그래서 3rd Party 툴들을 같이 사용해야 합니다. (ex. Collectd, telegraf ...[more](https://graphite.readthedocs.io/en/latest/tools.html))  
이번 포스팅에서는 **Collectd**를 Collector로써 사용할 예정입니다.  

여담으로 Graphite에 붙어있는 시각화 툴인 `Graphite-Web`도 유용하긴 하지만 기능이 썩 좋지는 않습니다.  
그래서 보통 모니터링툴도 `Grapana`와 같은 3rd Party툴을 사용합니다.  

그럼 왜 Graphite를 사용하나? 라고 생각이 들 수 있습니다.  
Graphite의 특장점은 데이터수집이나 그래프를 그리는데 있지 않고 **시계열 데이터를 다루는데에 있습니다.**  

**Graphite의 여러 Functions -> [Link](https://graphite.readthedocs.io/en/latest/functions.html)**  

수집된 시계열 데이터들을 변형하고 합치고 연산하는 일련의 과정을 Graphite에서는 Functions로 정의를 해두었는데요, 모든 Function을 이 게시글에서 다루긴 힘들 것 같습니다.  
추후에 기회가 되면 포스팅을 해보도록 하겠습니다.   


# HOW TO INSTALL GRAPHITE

## Prerequisite
사용한 서버 :   
`OS` : `UBUNTU 18.04`

## 1. System Update & Dependency 설치
~~~
$ sudo apt update
$ sudo apt -y upgrade

$ sudo reboot
~~~

dependency 설치   
~~~
$ apt-get install python-dev libcairo2-dev libffi-dev build-essential
~~~

## 2. Graphite Component 설치

Path 설정
~~~
$ export PYTHONPATH="/opt/graphite/lib/:/opt/graphite/webapp/"
~~~

Component들 pip으로 설치  
~~~
$ pip3 install --no-binary=:all: https://github.com/graphite-project/whisper/tarball/master
$ pip3 install --no-binary=:all: https://github.com/graphite-project/carbon/tarball/master
$ pip3 install --no-binary=:all: https://github.com/graphite-project/graphite-web/tarball/master
~~~

(210328기준) 설치 후 :  
~~~
Successfully installed whisper-1.2.0
Successfully installed cachetools-4.2.1 carbon txAMQP-0.8.2
Successfully installed Django-3.0.13 asgiref-3.3.1 cairocffi-file-.cairocffi-VERSION cffi-1.14.5 django-tagging-0.4.3 graphite-web pycparser-2.20 pyparsing-2.4.7 pytz-2021.1 scandir-1.10.0 sqlparse-0.4.1
~~~

## 3. Webapp Database Setup
먼저 Django베이스의 Graphite-Web의 Database를 만들어주어야 합니다.  

싱글 인스턴스인 경우 기본으로 제공되는 SQLite db를 사용하면 되고(STORAGE_DIR/graphite.db)  
멀티인스턴스거나 커스텀 db(MySQL, PostgreSQL등)를 사용하고 싶은 경우 모든 인스턴스가 같은 데이터소스를 공유해야합니다.  
> 커스텀 db를 사용해야 하는 경우 `$GRAPHITE_ROOT/webapp/graphite/local_settings.py`의 DATABASES영역을 수정할 것.  
> 참고링크 : [Django Documentation - DATABASES](https://docs.djangoproject.com/en/dev/ref/settings/#databases)


이번 포스팅에서는 기본 제공되는 SQLite db를 사용하겠습니다.(db영역 수정x)  

Database 세팅:  
~~~
$ PYTHONPATH=$GRAPHITE_ROOT/webapp django-admin.py migrate --settings=graphite.settings
~~~
![image](https://user-images.githubusercontent.com/15958325/112755166-829feb00-901a-11eb-9b95-37df840c3986.png)  

Webapp이 사용할 db이므로 Web 서비스가 해당 db에 접근할 수 있어야 합니다.  
ex) nobody유저가 Apache웹서버를 돌리고있다면 `chown nobody:nobody $GRAPHITE_ROOT/storage/graphite.db` 으로 변경   

## 4. Configuring The Webapp
[공식문서](https://graphite.readthedocs.io/en/latest/config-webapp.html)에서는 크게 세가지 조합을 권장하고 있습니다.  

- nginx + gunicorn
- Apache + mod_wsgi
- nginx + uWSGI

저는 첫번째 nginx+gunicorn 조합을 골라서 테스트해봤습니다. (이유없음)  

### gunicorn 설치 
~~~
$ pip3 install gunicorn
~~~
![image](https://user-images.githubusercontent.com/15958325/112755303-09ed5e80-901b-11eb-9fc0-fdcd87de5757.png)  

### nginx 설치
~~~
$ sudo apt install nginx
~~~

### Graphite-web 로그를 저장할 로그 파일 생성
~~~
$ sudo touch /var/log/nginx/graphite.access.log
$ sudo touch /var/log/nginx/graphite.error.log
$ sudo chmod 640 /var/log/nginx/graphite.*
~~~

### nginx config
~~~
$ vim /etc/nginx/sites-available/graphite

upstream graphite {
    server 127.0.0.1:8080 fail_timeout=0;
}

server {
    listen 80 default_server;

    server_name _;

    root /opt/graphite/webapp;

    access_log /var/log/nginx/graphite.access.log;
    error_log  /var/log/nginx/graphite.error.log;

    location = /favicon.ico {
        return 204;
    }

    # serve static content from the "content" directory
    location /static {
        alias /opt/graphite/webapp/content;
        expires max;
    }

    location / {
        try_files $uri @graphite;
    }

    location @graphite {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 10;
        proxy_read_timeout 10;
        proxy_pass http://graphite;
    }
}
~~~

nginx의 default페이지를 없애 graphite-web이 기본 페이지가 되도록 설정:    
~~~
$ sudo ln -s /etc/nginx/sites-available/graphite /etc/nginx/sites-enabled
$ sudo rm -f /etc/nginx/sites-enabled/default
~~~

### nginx 재시작
~~~
$ systemctl restart nginx
~~~

## 5. Configuring Carbon
graphite web페이지는 띄웠으니 이제 Collector로부터 데이터를 수신할 Carbon을 띄울 차례입니다.  

모든 Carbon의 설정파일은 `/opt/graphite/conf/`에 있습니다.  

필요한 설정파일을 example에서 복사:  
~~~
$ cp carbon.conf.example carbon.conf
$ cp storage-schemas.conf.example storage-schemas.conf
~~~

**carbon.conf** 는 Carbon의 메인 설정파일입니다.  
내부에는 `[cache]`, `[relay]`, `[aggregator]`섹션이 있고 각각 내부의 컴포넌트들의 설정값들입니다.  
- `carbon-cache.py` : Carbon의 메인 컴포넌트, metric을 수신하여 RAM에 저장하고 저장된 metric들을 whisper 라이브러리를 통해 disk에 저장하는 역할.
- `carbon-relay.py` : 데이터 replication과 sharding 담당
- `carbon-aggregator.py` : carbon-cache 앞단에서 작동하는 버퍼역할이며, 세분화된 메트릭들을 집계하여 합 또는 평균의 단일 메트릭으로 carbon-cache로 전달하는 역할.

테스트 용도이며 graphite-web의 db도 default로 사용을 하고 있으니 Carbon.conf에서는 수정해야 할 내용이 없습니다.  

**storage-schemas.conf**는 얼마나 데이터를 저장할 지 whisper에게 알려주는 파일입니다.  

예를 들어 기본 설정파일에는 아래와 같이 적혀있는데,  
~~~
[carbon]
pattern = ^carbon\.
retentions = 60:90d

[default]
pattern = .*
retentions = 60s:1d,5m:30d,1h:3y
~~~
metric의 이름앞에 `carbon.`이라고 적혀있는 metric에 적용되며, 60초마다 수집되는 데이터는 90일간 whisper에 저장된다는 뜻입니다.  

carbon-cahce 시작
~~~
$ /opt/graphite/bin/carbon-cache.py start

Starting carbon-cache (instance a)
~~~

~~~
$ ps aux |grep carbon
~~~
![image](https://user-images.githubusercontent.com/15958325/112756475-4c656a00-9020-11eb-876f-9b508bd4154c.png)  


## 6. Gunicorn 시작 (WSGI server)

> 기본 설정 path를 사용하지 않고 커스텀 path를 사용했다면 `$GRAPHITE_ROOT/webapp/graphite/local_settings.py`를 변경할 것.
>
>local_settings.py 설정값의 기본값들은 `$GRAPHITE_ROOT/webapp/graphite/settings.py`에 정의되어 있습니다.  
>![image](https://user-images.githubusercontent.com/15958325/112756766-9f8bec80-9021-11eb-8272-c56f4f64f5fc.png)  

변경한 것 없이 그냥 기본으로만 설치했다면 아래 명령어를 통해 gunicorn을 실행 :  
~~~
$ PYTHONPATH=/usr/graphite/webapp gunicorn wsgi --workers=4 --bind=127.0.0.1:8080 --log-file=/var/log/gunicorn.log --preload --pythonpath=/usr/graphite/webapp/graphite &
~~~

gunicorn 끌때에는 `pkill gunicorn`   

## 7. graphite-web 탐방하기
gunicorn까지 실행하는데 문제가 없었다면 graphite를 실행한 서버의 ip를 통해 graphite-web 화면을 확인할 수 있을겁니다.  
![image](https://user-images.githubusercontent.com/15958325/112756842-deba3d80-9021-11eb-9db3-1f0422a05f27.png)    
지금은 아무 collector설정도 해두지 않았기 때문에 graphite가 설치된 서버의 기본 수집값들만 수집하고 있습니다.  

수집된 데이터들은 아래 위치에 쌓이게 되며,  
~~~
$ ls $GRAPHITE_ROOT/storage/whisper/carbon/agents/$HOSTNAME
~~~
![image](https://user-images.githubusercontent.com/15958325/112756904-3789d600-9022-11eb-92a1-ab5238d0d905.png)   
위와 같이 wsp파일 형식으로 데이터가 쌓이게 됩니다.  

안을 열어보면 눈으로 데이터를 확인할 수는 없지만,  
![image](https://user-images.githubusercontent.com/15958325/112756908-3a84c680-9022-11eb-9b71-bab046e09918.png)    


graphite web 대시보드로 보게되면 그래프가 그려지는 것을 보실 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/112756909-3c4e8a00-9022-11eb-965d-32d86f3b7bbd.png)  


# HOW TO COLLECT DATA (Collectd)
위에서 언급했듯이 graphite자체는 데이터를 수집하는 기능이 존재하지 않습니다.  
그래서 다른 3rd party툴을 사용해서 수집을 해야하는데요,  

여러 툴들이 있지만 이번엔 `Collectd`를 사용하여 데이터를 수집해보도록 하겠습니다.  

## Collectd?

![image](https://user-images.githubusercontent.com/15958325/112796085-6ea0cb80-90a4-11eb-8a47-35cb13345490.png)  

**Collectd**는 타겟 시스템의 metric을 수집하고 분석또는 모니터링툴에 전송하는 C언어 기반의 데몬입니다.  
굉장히 가볍지만 지원하는 플러그인이 많아 다채롭게 사용할 수 있습니다.  

os나 application, 로그파일, 디스크 등 여러 장치들에서 collectd의 plugin을 통해 metric들을 수집할 수 있고 네트워크를 통해 수집한 데이터를 전송할 수 있습니다.  

>사용가능한 plugin 목록 : [collectd wiki - plugin](https://collectd.org/wiki/index.php/Table_of_Plugins)

### 1. Collectd 설치
먼저 관찰 대상이 되는 호스트에 collectd 데몬을 설치하여야 합니다.  

**관찰대상 : CentOS7 리눅스 서버**

~~~
$ yum install collectd
~~~
![image](https://user-images.githubusercontent.com/15958325/112815058-e24dd300-90ba-11eb-88d5-e7ac10ab0a96.png)  


### 2. Collectd config
Collectd의 주요 설정은 `/etc/collectd.conf`파일에 들어있습니다.  

내부를 보면  
![image](https://user-images.githubusercontent.com/15958325/112815413-3f498900-90bb-11eb-8e8d-bd446c2cc0c1.png)  
맨 윗부분은 전역 설정으로 되어있고 주석처리된 부분은 default값이 들어가게 됩니다.  

그리고 가장 중요한 "어떤 데이터를 수집할지"는 아래쪽 `LoadPlugin`으로 결정하게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/112815569-6c963700-90bb-11eb-99ce-b8fd6cec6cc6.png)  
![image](https://user-images.githubusercontent.com/15958325/112815585-6e5ffa80-90bb-11eb-880e-5eca320a1fb2.png)  
default로는 `cpu`, `interface`, `load`, `memory`가 collectd의 plugin으로써 추가되어있고,   
실제 실행시키면 해당 plugin에 관련된 metric들만 수집하게 됩니다.  

또한, plugin을 로드만시키면 되는게 아니라 해당 plugin을 어떤식으로(수집빈도수, 수집한 데이터는 어디에 보낼건지, port는 몇번인지 등)수집할 건지 정의도 해주어야 합니다.  

`collectd.conf`파일에 전부 기록해도 되지만, 너무 길어지기 때문에 `/etc/collectd.d`폴더를 include하게 되어있습니다.  
![image](https://user-images.githubusercontent.com/15958325/112816662-9a2fb000-90bc-11eb-848c-b76d7719f86b.png)  

그리고 이번 포스팅에서는 collectd의 기본적인 수집만으로 진행하도록 하겠습니다.  
(설정 손 안댐)  


### 3. graphite와 연결하기
collectd에서 수집한 데이터들은 graphite의 carbon으로 넘겨주어야 합니다.  

이럴땐 collectd의 `write_graphite` plugin을 사용합니다.  

/etc/collectd.d 밑에 conf파일 생성:   
~~~
$ vim collectd.d/write_graphite.conf

LoadPlugin write_graphite
<Plugin write_graphite>
  <Node "graphing">
    Host "{GRAPHITE_HOST}"
    Port "2003"
    Protocol "tcp"
    LogSendErrors true
    Prefix "collectd."
    StoreRates false
    AlwaysAppendDS false
    EscapeCharacter "."
    SeparateInstances true
  </Node>
</Plugin>
~~~

- **Host** : graphite ip
- **Port** : graphite port (default 2003)
- **Protocol** : tcp/udp
- **LogSendErrors** : true로 설정하면 에러 로그도 같이 전송됨, false로 설정하면 에러로그는 로깅안됨. 이 경우는 udp프로토콜을 사용할때 유용! (fire-and-forget 접근)
- **Prefix** : 호스트이름 앞에 prefix를 붙임(점, 공백은 escape 문자가 아님)
- **StoreRates** : true면 값을 비율값으로 변환함 false면 나온 값 그대로 저장
- **AlwaysAppendDS** : true면 metric에 datasource(DS)이름을 붙임 false(default)는 두개이상의 DS가 있을때 사용
- **EscapeCharacter** : 기본값은 "_", 설정하게되면 적힌 문자는 이스케이프 문자가 된다
- **SeparateInstances** : ex) true로 하면 host.cpu.0.cpu.idle , false로하면 host.cpu-0.cpu-idle

### 4. collectd 시작

~~~
$ systemctl start collectd
~~~
![image](https://user-images.githubusercontent.com/15958325/112817433-643efb80-90bd-11eb-8a12-d3eb06922eb2.png)  

시작 후 조금 기다렸다가 graphite gui화면으로 가보면 아래와 같이 collectd항목이 새로 생긴 것을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/112817577-90f31300-90bd-11eb-8433-fcf72973d32b.png)  

collectd.conf파일에 로드되었던 plugin인 cpu, interface, load, memory가 정상적으로 수집되고 있는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/112817587-93556d00-90bd-11eb-88a5-f8c2af1b2ea8.png)    


-끝-


# APPENDIX (Graphite port)
collectd 말고도 여러 데이터 수집기를 붙여야 할 때가 있을텐데, 가장 중요한건 graphite의 어떤 port로 데이터를 송신하느냐 입니다.  
그래서 graphite의 핵심적인 port 3가지를 정리해보았습니다.  

**LINE_RECEIVER_PORT 2003** 
- 플레인 텍스트 
- 포맷 : <metric path> <metric value> <metric timestamp>
- ex: hello.graphite 3.5 1405608517
	
**PICKLE_RECEIVER_PORT 2004**
- 배치데이터나 많은 양의 데이터를 핸들링하는경우
- 포맷 : [(path, (timestamp, value)), ...]
	
**CACHE_QUERY_PORT 7002**
- AMQP (Advanced Message Queing Protocol)
  -  MQ(Message Queue) 기반 표준 프로토콜
  - 가장 많이 사용되는 제품 : RabbitMQ
- 잘안쓰이는듯?
- 위스퍼db에서 데이터를 읽어와야하는데 카본에서 받은 데이터는 실시간 위스퍼에 쓰여지지 않기 때문에 카본에서 받은 데이터가 위스퍼에 쓰여지기전에 쿼리하는데 사용됨


----