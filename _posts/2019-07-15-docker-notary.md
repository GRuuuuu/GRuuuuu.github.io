---
title: "Content Trust in Docker : Docker Notary와 DCT란?"
categories: 
  - Container
tags:
  - Docker
  - TUF
  - Notary
  - Security
last_modified_at: 2019-07-29T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

----

# Overview
네트워크로 연결된 시스템 사이의 데이터 송수신에서 가장 중요하게 여기는 점은 **"신뢰"**입니다.  
특히 인터넷과 같이 신뢰할 수 없는 매체를 통해 통신할 때는 데이터의 무결성과 게시자를 보장하는 것이 중요합니다.  

이번 포스팅에서는 **Docker**에서의 이미지 위변조 방지기술인 `Docker Notary` 서비스와 `Docker Content Trust`에 대해서 알아보도록 하겠습니다.  

>같이보면 좋은 글 : [The Update Framework(TUF)](https://gruuuuu.github.io/security/tuf/)  

# Docker Notary
Notary의 사전적 정의는 다음과 같습니다.  

>**Notary**:  
>법률 당사자나 관계자의 부탁을 받아 민사에 관한 공정 증서를 작성하며, 사서 증서에 인증(認證)을 주는 권한을 가진 사람.   

쉽게 말해 어떠한 사실을 인증하는 역할을 하는 제 3자입니다. (공인인증서같이...)  
사전적 정의와 같이 **Notary**는 Docker Image에 대해서 **무결성**을 **인증**해주는 역할을 하고 있습니다.  

Notary는 해당 서비스를 사용하는 사용자에게 데이터의 신뢰성을 제공하기 위해 `The Update Framework(TUF)`라는 프레임워크를 사용하고 있습니다.  

>참고 : [TUF에 대한 설명](https://gruuuuu.github.io/security/tuf/)

본격적으로 **Notary Service**의 Archtecture로 넘어가기 전에 **TUF Key**에 대해 짚고 넘어가도록 하겠습니다.  

## TUF Key?
TUF의 기본 개념은 4가지 정도가 있습니다.  
- **Trust** : 영원하지 않고 균등하게 부여되지 않음.
- **Compromise-Resilience** : 키가 노출되었을때 클라이언트를 안전하게 유지시킴.
- **Integrity** : 단일파일 뿐만 아니라 전체 저장소도 무결함.
- **Freshness** : 시스템은 업데이트 할 파일의 최신 버전을 알고있음.  

위의 개념들을 구현하기 위해 TUF에서는 4가지 Role을 제공하고 있습니다.  

각 Role에 해당하는 Key들은 상응하는 `Metadata`를 서명합니다. 그 구조는 아래 사진과 같습니다.  
![tuf key](https://camo.githubusercontent.com/c4166122f8b4e908ad9d59421072ea1f64074a9d/68747470733a2f2f63646e2e7261776769742e636f6d2f7468657570646174656672616d65776f726b2f6e6f746172792f303966383137313730383066353332373665363838316563653537636262626639316238653261372f646f63732f696d616765732f6b65792d6869657261726368792e737667)   

>**[참고]**  
>아래 나오는 파일이름, 크기 등은 실제 송수신하는 데이터를 뜻합니다. 즉 저장소에 저장하거나 내려받을 **실제 content** 입니다.  

**Root Key** :  
- **root metadata file**을 서명
- 해당 metadata file에는 root의 ID, timestamp, snapshot, targets의 **public key**가 존재
- 이 public key로 다른 metadata file의 **서명을 검증**
- **Owner**가 소유하여야 하며 안전을 위해 **offline**에 보관을 권장  

**Snapshot Key** :  
- **snapshot metadata file**을 서명
- 해당 metadata file에는 파일이름, 크기, root, target, delegation의 metadata file **Hash**가 존재
- 다른 metadata의 **무결성을 검증**
- **Owner**또는 **Admin**이 소유하거나 위임을 통해 **multi-sign**가능한 사용자가 소유

**Timestamp Key** :  
- **timestamp metadata file**을 서명
- 해당 metadata file에는 이 metadata file의 **만료시간**, 파일이름, 크기, 가장 최근 snapshot의 Hash가 존재
- snapshot파일의 **무결성을 검증**
- **Notary Service**가 소유하고 있으며 server로부터의 요청이 있을때마다 <U>자동으로 생성</U>됨

**Targets Key** :   
- **targets metadata file**을 서명
- 해당 metadata file에는 파일이름의 리스트, 사이즈, 각 파일의 Hash값이 존재
- **실제 contents의 무결성 검증**
- **Owner**또는 **Admin**이 소유  

**Delegation Key** :   
- **delegation metadata file**을 서명
- Targets metadata file의 내용과 동일
- 권한을 위임받은 **collaborator**면 누구나 소유 가능

## Docker Notary Architecture
지금부터는 TUF를 바탕으로 한 **Notary Service**의 아키텍처를 살펴보도록 하겠습니다.  

![notary arch](https://user-images.githubusercontent.com/15958325/62032133-e493c600-b223-11e9-824f-701a795e3457.png)
    

### Notary Server
Notary Server는 TUF metadata file들을 저장합니다.   
- 업로드된 metadata들이 **유효**하고, **서명**되어 있으며, **self-consistent**하다는 것을 보장
- **timestamp** (또는 **snapshot**) metadata를 생성
- **유효하며 가장 최근인** metadata를 저장하고 client에 보냄


~미완~