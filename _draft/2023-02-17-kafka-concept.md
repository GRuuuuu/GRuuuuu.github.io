---
title: "호다닥 톺아보는 Kafka"
categories: 
  - Integration
tags:
  - Kafka
last_modified_at: 2023-02-17T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
예를 들어서 특정 서비스를 제공하는 app이 있다고 가정하고 그 app의 로그를 받아서 처리하는 또다른 app이 있다고 가정해봅시다.  

대충 아래와 같은 모습이 되겠습니다.  
(그림)

하지만 점점 더 복잡한 서비스에서는 어떻게 될까요?  
(그림)  
위와 같이 수많은 소스 application과 타겟 application들이 직접적으로 통신하게 되면서 서비스 구조도 복잡해지고, 통신 프로토콜의 파편화가 심해지게 됩니다.  

이렇게 되면 **배포나 장애에 대응하기 어려워지고, 유지보수가 힘들어진다**는 단점이 있습니다.  

# Apache Kafka란?
## 탄생
소셜 네트워크 앱중 하나인 "**LinkedIn**"의 개발자들도 이와 같은 문제를 갖고 있었습니다.  
2011년 **LinkedIn**은 이런 복잡함을 해결하고자 소스app과 타겟app의 커플링을 낮게 하려하였고 분산메시징시스템인 **Apache Kafka**를 개발하였습니다.  

(그림)  

그림에서 확인할 수 있다시피, Kafka는 데이터 파이프라인을 파편화하지않고 **모든 이벤트/데이터의 흐름을 중앙집중화** 시켰습니다.   
그래서 모든 application은 다른 app이아니라 kafka만 바라보면 되는 구조가 되는 것이죠.  

Kafka는 2011년 오픈소스로 공개되었고, 2012년 10월 Apache 인큐베이터를 종료한 상태입니다.  
현재 Kafka개발을 주도하던 Jay Kreps를 비롯한 일부 엔지니어들은 [Confluent](https://www.confluent.io/)라는 회사를 설립하여 Kafka관련 일들을 하고 있다고 합니다.  

>여담으로 Kafka는 유명한 작가인 프란츠 카프카(Franz Kafka)에서 따왔다고하고, 실제 구조나 기능과는 크게 관계가 없다고 합니다.  

## Components
그럼 Kafka가 어떤 구조로 이뤄져있는지 살펴보도록 하겠습니다.  

### Topic
Kafka는 이벤트 스트리밍 플랫폼입니다. Kafka에 전달되는 메세지 스트림의 추상화된 개념을 Topic이라고 부릅니다.  

(그림)

이벤트를 만들어내는 Producer가 어떤 Topic에 데이터를 적재할건지, Consumer는 어떤 Topic에서 데이터를 읽을건지(구독할건지) 정하게 됩니다.  

Topic은 여러개 생성할 수 있으며, 각각의 메세지를 목적에 맞게 구분할 때 사용합니다.  

### Partition
각 Topic은 내부에 더 세분화된 단위인 Partition을 가지고 있습니다.  

(그림)  

- 메세지가 들어오면 순차적으로 추가되며, Consumer가 메세지를 읽을 때에는 Queue의 선입선출(FIFO)과 비슷하게 오래된 메세지부터 읽게됨
- Queue와 다른 점은 **레코드를 읽어도 사라지지 않는다**는 점
- 이게 가능한 이유는 Queue가 아닌 **실제 파일시스템**에 데이터가 저장되기 때문
- 때문에 Consumer처리가 늦거나 Kafka클러스터에 문제가 생겨도 메세지 손실이 발생하지 않음
- Consumer가 Partition의 레코드를 읽을 때에는 `offset`이라는 저장위치를 기억하고 있어서 문제가 생겨도 **읽던 위치부터 다시 읽기 가능**
- Partition에는 여러 Consumer 그룹이 붙을 수 있고, 그룹이 다르고 [auto.offset.reset=earlist](https://kafka.apache.org/documentation/#consumerconfigs_auto.offset.reset) 일 경우 각 Consumer 그룹은 0번 레코드부터 읽기 시작함  

Topic은 하나 이상의 Partition을 가질 수 있는데, 여러개의 Partition을 가지고 있는 경우를 생각해보겠습니다.  

(그림)

- 데이터를 적재할 시, 키값을 지정해주어 **특정 Partition**에만 데이터 적재 가능
- 키값을 지정해주지 않았을 경우, **Round-robin방식**으로 데이터 적재
- Partition을 늘리는 것은 가능하지만 줄일수는 없음
- Partition을 늘리면 Consumer를 늘려서 **데이터 처리를 분산**할 수 있음

Partition에 저장된 데이터는 삭제할 시점을 설정해줄 수 있습니다.  
- `log.retention.ms` : 최대 record 보존시간
- `log.retention.byte` : 최대 record 보존크기(byte)

### Producer
Producer는 데이터를 만들어내고 Kafka Topic에 데이터를 적재시키는 주체입니다.  

(그림)

- 특정 Topic으로 데이터를 publish
- 