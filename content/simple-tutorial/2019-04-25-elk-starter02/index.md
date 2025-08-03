---
title: "02.Configuring Cluster"
tags:
  - ELK-Stack
  - Elasticsearch
date: 2019-04-25T13:00:00+09:00
series: ["ELK-Starter"]
series_order: 2
---

## 1. Overview
이번 문서에서는 elasticsearch의 클러스터 상태를 확인해보겠습니다.  

## 2. Prerequisites
>**환경 정보**  
>`centOS` : v7.0  
>`elasticsearch` : v6.7.1  

[elasticsearch 설치](https://gruuuuu.github.io/elk-starter/elk-starter01/)를 완료하셔야 합니다.  

## 3. Cluster Health
클러스터는 es에서 가장 큰 시스템 단위이며 node들의 집합을 일컫는 말입니다.  

클러스터의 status의 종류는 총 세가지로, `green`, `yellow`, `red`가 있습니다.  
* `green` : 모든 샤드가 정상적으로 동작하고 있음. 모든 인덱스에 READ/WRITE가 **정상적**으로 동작.  
* `yellow` : 모든 데이터의 읽기/쓰기가 가능한 상태지만 일부 replica 샤드가 아직 배정되지 않은 상태. **정상작동중**이지만, replica 샤드가 없기 때문에 검색 성능에 영향이 있을 수 있다.   
* `red` : primary와 replica샤드가 정상적으로 동작하고 있지 않음. 인덱스에 READ/WRITE가 **정상적으로 동작하지 않고** 데이터의 유실이 발생할 수 있다.

### get status
클러스터의 status를 확인하려면 다음 명령어를 통해 확인할 수 있습니다.  
~~~bash
$ curl -XGET localhost:9200/_cluster/health?pretty
~~~  
![image](https://user-images.githubusercontent.com/15958325/57598324-c35cfb00-758d-11e9-920d-5fd3cd53f658.png)   
아무런 인덱스도 만들지않고, elasticsearch를 설치한 직후 위 명령어를 쳐보면 해당 클러스터의 status는 green이라고 나오게 됩니다.  
배정되지 않은 샤드가 하나도 없기 때문입니다.  

이번에는 index를 만들고나서 status를 확인해보겠습니다.    
~~~bash
$ curl -XPUT localhost:9200/model?pretty
$ curl -XPUT localhost:9200/sys_user_mapping?pretty
~~~  
status가 yellow가 되어버렸네요!  
![image](https://user-images.githubusercontent.com/15958325/57599308-35830f00-7591-11e9-9746-43879f13517b.png)  

이유를 알아보기 위해 index정보와 shard정보를 출력해봅시다.  

### get index list
~~~bash
$ curl -XGET localhost:9200/_cat/indices?v
~~~
![image](https://user-images.githubusercontent.com/15958325/57599903-28671f80-7593-11e9-99a2-9ed12d39c90b.png)  

인덱스들의 정보를 보아하니 primary 하나당 replica 1개씩인것을 확인할 수 있습니다.  

### get shard info
~~~bash
$ curl -XGET localhost:9200/_cat/shards?v
~~~
![image](https://user-images.githubusercontent.com/15958325/57599251-0a002480-7591-11e9-9d7f-751799fe5881.png)  
확인해보니 각 replica들이 전부 unassigned입니다.  
elasticsearch에서 primary와 replica는 같은 node에 존재할 수 없습니다. 현재 환경은 1node로 운영하고 있으므로 replica를 배정할수가 없게 됩니다.  

나중에 다른 node가 클러스터에 포함되게 된다면 replica를 배정할 수 있고 status도 green으로 변하게 됩니다.  

하나의 node에서 status를 green으로 만들기 위해서는 클러스터의 세팅에서 replica 샤드를 0으로 만드는 방법이 있습니다. 
~~~bash
$ curl -XPUT 'localhost:9200/_settings?pretty' -d '{"index":{"number_of_replicas": 0}}' -H 'Content-Type: application/json'
~~~
하지만, 이는 안정성이 떨어지는 아키텍처이므로 추천하지 않습니다.  

일단은 yellow상태라도 문제없으니 앞으로의 실습에서 참고해주시기 바랍니다.  

>클러스터에서 여러개의 노드를 다루는 방법은 추후에 서술  

----