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

그림에서 확인할 수 있다시피, Kafka는 데이터 파이프라인을 파편화하지않고 모든 이벤트/데이터의 흐름을 중앙집중화 시켰습니다.   
그래서 모든 application은 다른 app이아니라 kafka만 바라보면 되는 구조가 되는 것이죠.  

Kafka는 2011년 오픈소스로 공개되었고, 2012년 10월 Apache 인큐베이터를 종료한 상태입니다.  
Kafka개발을 주도하던 Jay Kreps를 비롯한 일부 엔지니어들은 [Confluent](https://www.confluent.io/)라는 회사를 설립하여 Kafka관련 일들을 하고 있다고 합니다.  

>여담으로 Kafka는 유명한 작가인 프란츠 카프카(Franz Kafka)에서 따왔다고하고, 실제 구조나 기능과는 크게 관계가 없다고 합니다.  

## 