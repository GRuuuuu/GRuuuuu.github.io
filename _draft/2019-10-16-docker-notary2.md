---
title: "Content Trust in Docker(2) : DCT 실습"
categories: 
  - Container
tags:
  - Docker
  - TUF
  - Notary
  - Security
last_modified_at: 2019-10-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

# Overview
네트워크로 연결된 시스템 사이의 데이터 송수신에서 가장 중요하게 여기는 점은 **"신뢰"**입니다.  
이전에 Docker Notary 서비스에 대한 것을 포스팅한 적이 있습니다.  

이번 포스팅은 `Notary`서비스를 기반으로 **Docker Registry**(`Docker Hub` 또는, `Docker Trusted Registry`)에서 제공하는 **Docker Content Trust**입니다.  

기본적인 이론은 Notary에서 설명이 되었으니 요번엔 실습을 한번 해보도록 하겠습니다.  

> [Content Trust in Docker(1) : Docker Notary란?](https://gruuuuu.github.io/container/docker-notary/)  


