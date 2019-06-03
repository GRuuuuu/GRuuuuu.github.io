---
title: "Simple JSON Query for IBM Cloudant"
categories: 
  - Simple-Tutorial
tags:
  - JSON
  - Cloudant
  - NoSQL
last_modified_at: 2019-04-29T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 `IBM Cloudant`에 DB를 작성하고, 이를 문서로 채우고, 인덱스를 작성하고, 인덱스를 사용하여 DB를 조회하는 방법을 소개하겠습니다.  

CLI와 GUI환경 모두에서 실습을 진행하겠습니다.  

## 2. Prerequisites

IBM Cloud 계정 : [link](https://console.bluemix.net)  
> 환경이 window라면 git bash를 설치해주세요.  
> Git Bash : [link](https://gitforwindows.org/)

## 3. IBM Cloudant
실습을 진행하기전에 `IBM Cloudant`가 무엇인지 잠시 짚고 넘어가겠습니다.  

`IBM Cloudant`는 document중심 DBaaS(Database as a Service)입니다. 타 NoSQL DB와 같이 데이터를 `JSON`형식의 Document로 저장할 수 있습니다.  

한마디로 클라우드 위의 NoSQL DB라고 생각하시면 됩니다.  

## 4. Basic Query

### Add Cloudant Instance
먼저 cloudant 인스턴스를 cloud에 추가해야 합니다.  
리소스 추가에서 Cloudant를 검색한 뒤, 생성해 줍시다.  
![image](https://user-images.githubusercontent.com/15958325/56877680-a3581280-6a8a-11e9-8978-00e00618cf27.png)  

외부에서의 접근을 허용하기 위해 새 인증정보를 생성해야합니다.  
![image](https://user-images.githubusercontent.com/15958325/56877737-25e0d200-6a8b-11e9-96dd-f3c6e15860e2.png)  

인증정보는 json형태로 떨어지게 됩니다.  
이 튜토리얼에서 사용할 부분은 `url`과 `port`부분입니다. 두 개 파라미터를 다른데 적어두도록 합시다.  
![image](https://user-images.githubusercontent.com/15958325/56877750-3c872900-6a8b-11e9-888c-4ec3a1dd27b1.png)  
> url은 다음과 같이 구성되어 있습니다.  
> `url` : https://`$USERNAME`:`$PASSWORD`@`$ACCOUNT`.cloudantnosqldb.appdomain.cloud 

### Set ENV

앞으로 `curl`명령문을 작성할 때 다음과 같은 형태로 작성할 것입니다. 계속 같은 구문이 반복되고, 그 길이가 상당히 길기때문에 환경변수를 세팅하도록 하겠습니다.  
~~~
1) curl -k https://$USERNAME:$PASSWORD@$ACCOUNT.cloudantnosqldb.appdomain.cloud:$PORT/...

2) curl -k $URL:$PORT/...
~~~  
1번 2번 둘다 같기때문에 마음에 드는걸로 골라서 하시면 됩니다. 이 문서에서는 2번방법으로 진행하겠습니다.  

`git bash`를 실행시키고 인증정보에서 얻은 값들로 환경변수를 세팅해줍니다.  
~~~bash
export URL=https://51a3858b-376c-4922-9f9b-157b27392f7d-bluemix:d4c325374b61fd3d5da86523d3bfe16d04969f75259b1658ae9d7a971c4e0a14@51a3858b-376c-4922-9f9b-157b27392f7d-bluemix.cloudantnosqldb.appdomain.cloud
export PORT=443
~~~

### Create DB

#### CLI 

input:  
~~~bash
$ curl -XPUT -k $URL:$PORT/{db name}
~~~  

output:   
~~~json
{"ok":true}
~~~

#### GUI

cloudant 인스턴스에 들어가서 Create DB를 클릭하고 진행합니다.   
![image](https://user-images.githubusercontent.com/15958325/56878498-617d9b00-6a8f-11e9-8f72-0cbf085f3f0b.png)  


### Create Document

Document는 indexing할 수 있는 데이터의 기본 단위입니다.  

#### CLI
다음 내용의 json파일을 생성합니다.  
~~~json
{
"docs":
[
  {
    "_id": "doc1",
    "firstname": "Sally",
    "lastname": "Brown",
    "age": 16,
    "location": "New York City, NY"
  },
  {
    "_id": "doc2",
    "firstname": "John",
    "lastname": "Brown",
    "age": 21,
    "location": "New York City, NY"
  },
  {
    "_id": "doc3",
    "firstname": "Greg",
    "lastname": "Greene",
    "age": 35,
    "location": "San Diego, CA"
  },
  {
    "_id": "doc4",
    "firstname": "Anna",
    "lastname": "Greene",
    "age": 44,
    "location": "Baton Rouge, LA"
  },
  {
    "_id": "doc5",
    "firstname": "Lois",
    "lastname": "Brown",
    "age": 33,
    "location": "New York City, N"
  }
]
}
~~~

쿼리문은 다음과 같습니다. file name앞에는 '@'를 붙여주어야 합니다.

input:   
~~~bash
$ curl -XPOST -k $URL:$PORT/{db name}/_bulk_docs -H "Content-Type: application/json" -d \@{file name}
~~~  

output:
~~~json
[
    {
        "ok":true,"id":"doc1",
        "rev":"1-cce7796c7113c5498b07d8e11d7e0c12"
    },
    {
        "ok":true,"id":"doc2",
        "rev":"1-2c5ee70689bb75af6f65b0335d1c92f4"
    },
    {
        "ok":true,"id":"doc3",
        "rev":"1-f6055e3e09f215c522d45189208a1bdf"
    },
    {
        "ok":true,"id":"doc4",
        "rev":"1-0923b723c62fe5c15531e0c33e015148"
    },
    {
        "ok":true,"id":"doc5",
        "rev":"1-19f7ecbc68090bc7b3aa4e289e363576"
    }
]
~~~  

Cloudant Dashboard에서 확인해보면 제대로 document들이 들어간 것을 확인할 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/56880754-f20ca900-6a98-11e9-86da-fe95a6cc5fe9.png)  

#### GUI

새문서만들기를 선택하고,  
![image](https://user-images.githubusercontent.com/15958325/56880850-4ca60500-6a99-11e9-971b-69dba77cf958.png)  

상기의 json문서에서 document를 하나씩 추가하면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/56880870-5c254e00-6a99-11e9-9032-f6168b67530e.png)  

5개의 document가 추가된 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/56880892-6cd5c400-6a99-11e9-85c4-ddc52d034229.png)  


### Create Index
Index는 Document들을 담아두는 통입니다. 미리 특정 조건의 document들을 index에 담아두고 search를 하게되면 좀 더 빠르게 search가 가능합니다.  

#### CLI

Index를 정의하는 json파일을 생성합니다.  
~~~json
{
"index": {
    "fields": [
        "age",
        "lastname"
    ],
    "partial_filter_selector": {
        "age": {
            "$gte": 30
        },
        "lastname": {
            "$eq": "Greene"
        }
    }
},
      "ddoc": "partial-index",
    "type": "json"
}
~~~
>age가 30보다 크고, lastname이 Greene인 document를 partial-index라는 이름의 index에 넣습니다.  

input:  
~~~bash
curl -XPOST -k $URL:$PORT/{db name}/_index -H "Content-Type: application/json" -d \@{file name}
~~~  

output:  
~~~json
{
    "result":"created",
    "id":"_design/partial-index",
    "name":"c387823bba25b8fbb478293cc3b8eaa84e4093b1"
}
~~~

#### GUI

Design Documents > Query Indexes로 이동합니다.  
![image](https://user-images.githubusercontent.com/15958325/56881221-b541b180-6a9a-11e9-9f56-999e0e28c8d0.png)  

생성하려는 index를 json형식으로 입력합니다.  
![image](https://user-images.githubusercontent.com/15958325/56881295-f0dc7b80-6a9a-11e9-8fdb-813547b9ac66.png)  

### Search Query -Selector
#### CLI
Selector를 사용해 검색하는 쿼리를 작성합니다.  
위 내용과 같이 다음 json코드도 파일로 작성해줍니다.  

~~~json
{
  "selector": {
        "lastname" : "Greene",
        "firstname" : "Anna"            
     }        
}
~~~  
>lastname이 Greene이고 firstname이 Anna인 document를 찾는 쿼리입니다.  

input:  
~~~bash
$ curl -XPOST -k $URL:$PORT/{db name}/_find -H "Content-Type: application/json" -d \@{file name}
~~~  

output:  
~~~json
{
    "docs":[
    {
        "_id":"doc4",
        "_rev":"1-0923b723c62fe5c15531e0c33e015148",
        "firstname":"Anna",
        "lastname":"Greene",
        "age":44,
        "location":"Baton Rouge, LA"
    }
    ],
    "bookmark": "g1AAAAA4eJzLYWBgYMpgSmHgKy5JLCrJTq2MT8lPzkzJBYqzAFkmIDkOmBxcNAsAq-wPkQ",
    "warning": "no matching index found, create an index to optimize query time"
}
~~~  
> index를 지정해주지 않았기 때문에 warning이 뜹니다.  

#### GUI  
Query탭으로 이동해서 위에서 만들었던 json형식 그대로 붙여넣어서 검색합니다.  
![image](https://user-images.githubusercontent.com/15958325/56882704-5894c580-6a9f-11e9-9c71-7c75ddd1a9b8.png)  
바로 옆에서 결과를 확인할 수 있습니다.  

### Search Query -Field  
검색 쿼리를 날린 뒤, 결과를 출력할 때 원하는 필드만 출력하는 방법입니다.  

쿼리는 다음과 같습니다.  

~~~json
{
"selector": {
  "lastname": "Brown",
  "location": "New York City, NY"
},
"fields": [
  "firstname",
  "lastname",
  "location"
] 
}
~~~
>lastname이 Brown이고 location이 New York City, NY인 document를 찾고, 필드는 firstname과 lastname 그리고 location만 출력하도록 합니다.  

#### CLI
위 쿼리를 json파일로 만들어줍니다.  

input:  
~~~bash
$ curl -XPOST -k $URL:$PORT/{db name}/_find -H "Content-Type: application/json" -d \@{file name}
~~~  

output:  
~~~json
{
    "docs":[
    {
        "firstname":"Sally",
        "lastname":"Brown",
        "location":"New York City, NY"
    },
    {
        "firstname":"John",
        "lastname":"Brown",
        "location":"New York City, NY"
    },
    {
        "firstname":"Lois",
        "lastname":"Brown",
        "location":"New York City, NY"
    }
    ],
    "bookmark": "g1AAAAA4eJzLYWBgYMpgSmHgKy5JLCrJTq2MT8lPzkzJBYqzAFmmIDkOmBxcNAsArAYPkw",
    "warning": "no matching index found, create an index to optimize query time"
}
~~~  

#### GUI 
Query탭으로 이동해서 상기의 json 쿼리문을 Run시킵니다.  
![image](https://user-images.githubusercontent.com/15958325/56883195-eb822f80-6aa0-11e9-9b30-e24559bcb9fa.png)  

### Search Query -Operator
조건문을 쿼리에 포함시키는 방법을 알아보겠습니다.  

> Cloudant는 Mongo 스타일의 operator를 사용하고 있습니다. 다음 링크를 참조해주세요.  
> [MongoDB Query and Projection Operators](https://docs.mongodb.com/manual/reference/operator/query/)   

|Comparison Operator
----|----
$eq|같음
$gt|큼
$gte|크거나 같음
$in|일치하는 값이 있음
$lt|작음
$lte|작거나 같음
$ne|다름
$nin|일치하는 값이 없음


~~~json
{
  "selector": {
    "age": {
      "$gt": 30
    },
    "lastname": {
      "$eq": "Greene"
    }
  }
}
~~~
>age는 30보다 크고, lastname은 Greene과 같은 document를 찾습니다.  

#### CLI

input:  
~~~bash
$ curl -XPOST -k $URL:$PORT/{db name}/_find -H "Content-Type: application/json" -d \@{file name}
~~~  

output:  
~~~json
{
    "docs":[
    {
        "_id":"doc3",
        "_rev":"1-f6055e3e09f215c522d45189208a1bdf",
        "firstname":"Greg",
        "lastname":"Greene",
        "age":35,
        "location":"San Diego, CA"
    },
    {
        "_id":"doc4",
        "_rev":"1-0923b723c62fe5c15531e0c33e015148",
        "firstname":"Anna",
        "lastname":"Greene",
        "age":44,
        "location":"Baton Rouge, LA"
    }
    ],
    "bookmark": "g1AAAAA4eJzLYWBgYMpgSmHgKy5JLCrJTq2MT8lPzkzJBYqzAFkmIDkOmBxcNAsAq-wPkQ",
    "warning": "no matching index found, create an index to optimize query time"
}
~~~

그런데 json 쿼리문의 조건부가 앞전에 작성했었던 index와 일치하네요! 검색 성능의 향상을 위해 index를 사용하고, 필드를 제한해서 정렬한 뒤 좀 더 깔끔한 결과를 얻어봅시다.  

~~~json
{
"selector": {
  "age": {
     "$gt": 30
  },
  "lastname": {
     "$eq": "Greene"
  }
},
"fields": [
  "age",
  "firstname"
],
"sort": [
  {
     "age": "asc"   
  }
],
"use_index": "_design/partial-index"
}
~~~

output2:  
~~~json
{
    "docs":[
        {"age":35,"firstname":"Greg"},
        {"age":44,"firstname":"Anna"}
    ],
    "bookmark": "g1AAAABCeJzLYWBgYMpgSmHgKy5JLCrJTq2MT8lPzkzJBYqzAFkmIDkOmFwOSHWiDkiSzb0oNTUvNSsLAEsmEeQ"
}
~~~


#### GUI 
Query탭으로 이동해서 상기의 json 쿼리문을 Run시킵니다.  
![image](https://user-images.githubusercontent.com/15958325/56884781-c643f000-6aa5-11e9-943b-9fc4785a1cfc.png)  

끝!

----