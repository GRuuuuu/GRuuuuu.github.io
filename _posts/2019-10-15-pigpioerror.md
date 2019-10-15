---
title: "Error: pigpio error -1 in gpioInitialise"
categories: 
  - ERROR
tags:
  - GPU
  - ML
last_modified_at: 2019-10-15T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


## Environment
`Arch : RaspberryPi 3`   
`OS kernel : Linux raspberrypi 4.14.30-v7`  
`node : v8.11.3`  
`npm : v5.6.0`

## Purpose
라즈베리파이의 servo(모터)를 동작시키려고 함

## Problem
>02arm.js는 모터동작하게 하는 코드

~~~
pi@raspberrypi:~/tjbot/recipes/conversation $ sudo node 02arm.js
verbose: TJBot initializing servo motor on PIN 7
2019-10-11 18:56:53 initInitialise: Can't lock /var/run/pigpio.pid
/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:11
    pigpio.gpioInitialise();
           ^

Error: pigpio error -1 in gpioInitialise
    at initializePigpio (/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:11:12)
    at new Gpio (/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:25:3)
    at TJBot._setupServo (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:361:19)
    at TJBot.<anonymous> (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:74:22)
    at Array.forEach (<anonymous>)
    at new TJBot (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:59:14)
    at Object.<anonymous> (/home/pi/tjbot/recipes/conversation/02arm.js:22:10)
    at Module._compile (module.js:652:30)
    at Object.Module._extensions..js (module.js:663:10)
    at Module.load (module.js:565:32)
    at tryModuleLoad (module.js:505:12)
    at Function.Module._load (module.js:497:3)
    at Function.Module.runMain (module.js:693:10)
    at startup (bootstrap_node.js:191:16)
    at bootstrap_node.js:612:3
~~~

pin7에서 에러가 났다고 하길래 하드웨어적인 문제인줄 알고 모터, 판, 선 다바꿔봤는데 똑같은 에러 발생.  

~~~
initInitialise: Can't lock /var/run/pigpio.pid
~~~
이 에러에 대한걸 찾아봤더니 몇 개 해결책이 나오긴 했다.  

그 중 하나가 `/var/run/pigpio.pid`를 날려버리는것.  

~~~
pi@raspberrypi:~/tjbot/recipes/conversation $ cat /var/run/pigpio.pid
313
pi@raspberrypi:~/tjbot/recipes/conversation $ sudo kill -9 313
pi@raspberrypi:~/tjbot/recipes/conversation $ rm /var/run/pigpio.pid
~~~
`pigpio.pid`에 적혀있는 프로세스 아이디를 찾아서 없애버리고 pid파일도 날려버린다.  

근데 또 에러가 난다.  

~~~
pi@raspberrypi:~/tjbot/recipes/conversation $ sudo node 02arm.js
verbose: TJBot initializing servo motor on PIN 7
2019-10-11 18:57:28 initInitialise: bind to port 8888 failed (Address already in use)
/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:11
    pigpio.gpioInitialise();
           ^

Error: pigpio error -1 in gpioInitialise
    at initializePigpio (/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:11:12)
    at new Gpio (/home/pi/tjbot/recipes/conversation/tjbotlib/node_modules/pigpio/pigpio.js:25:3)
    at TJBot._setupServo (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:361:19)
    at TJBot.<anonymous> (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:74:22)
    at Array.forEach (<anonymous>)
    at new TJBot (/home/pi/tjbot/recipes/conversation/tjbotlib/lib/tjbot.js:59:14)
    at Object.<anonymous> (/home/pi/tjbot/recipes/conversation/02arm.js:22:10)
    at Module._compile (module.js:652:30)
    at Object.Module._extensions..js (module.js:663:10)
    at Module.load (module.js:565:32)
    at tryModuleLoad (module.js:505:12)
    at Function.Module._load (module.js:497:3)
    at Function.Module.runMain (module.js:693:10)
    at startup (bootstrap_node.js:191:16)
    at bootstrap_node.js:612:3
~~~
비슷해보이는 에러인데 이번엔 포트충돌문제다.  

~~~
initInitialise: bind to port 8888 failed (Address already in use)
~~~

# Solution

## Caused by : 잘모르겠다
~~~
initInitialise: Can't lock /var/run/pigpio.pid
~~~
위 에러에 대한 원인은 잘 모르겠다.  

~~~
initInitialise: bind to port 8888 failed (Address already in use)
~~~
port8888을 누가 점유하고 있기때문에 발생.

## How to solve?
pigpio는 default port가 8888이기 때문에 해결방법은 두가지다.  

1. 8888포트를 쓰고있는 프로세스의 포트를 변경
2. pigpio의 default port를 변경

나는 2번으로 해결  

pigpio를 설정하는 코드에 `configureSocketPort`로 포트 지정.  

>근데 `configureSocketPort`를 사용하려면 `pigpio` 버전이 0.6.0 이상이어야 한다.

~~~js
TJBot.prototype._setupServo = function(pin) {
    var pigpio=require('pigpio');
    pigpio.configureSocketPort(8889);
    var Gpio=pigpio.Gpio;
    ....
~~~

GOOD!

----
