---
title: "Curl Command for ICOS REST API"
categories: 
  - Simple-Tutorial
tags:
  - ICOS
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---

This document introduces command that how to communicate ICOS with REST-API using curl.   

## 1. IBM Cloud Object Storage API
IBM Cloud Object Storage API는 객체 읽기 및 쓰기를 위한 REST 기반 API 입니다. 인증을 위해 IBM Cloud Identity와 Access Management를 사용하며, S3 API의 서브셋을 지원하여 app이 IBM Cloud로 쉽게 마이그레이션되도록 합니다.   

아래 챕터부터 CLI환경에서 curl command를 이용해 ICOS와 통신하는것에 대해 기술하겠습니다.  

## 2. Credential & Authentication
### endpoint  
cos의 endpoint는 cos인스턴스 > Endpoint > cos만들때설정들을 입력하면 endpoint를 얻을 수 있습니다.  

![image](https://user-images.githubusercontent.com/15958325/55863003-9c895e80-5bb4-11e9-8d5f-c801c3f0fb9f.png)  

>예시) Regional에 위치가 us-south이고 public cos라면  
>endpoint -> s3.us-south.cloud-object-storage.appdomain.cloud  

### Request an IAM Token  
> IAM(Identity & Access Management)   

자격증명과 접근관리를 위해 API키를 생성합니다.  
->[link](https://cloud.ibm.com/iam#/apikeys)  
![image](https://user-images.githubusercontent.com/15958325/55844390-f7e92b80-5b77-11e9-8d03-db2534636cdd.png)  

위에서 얻은 API키를 사용해서 IAM토큰을 얻습니다.  
~~~bash
 $ curl -X "POST" "https://iam.cloud.ibm.com/identity/token" \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     --data-urlencode "apikey={api-key}" \
     --data-urlencode "response_type=cloud_iam" \
     --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey"
~~~  

![image](https://user-images.githubusercontent.com/15958325/55845043-30d6cf80-5b7b-11e9-8204-6ace4ea39101.png)  
![image](https://user-images.githubusercontent.com/15958325/55845077-506df800-5b7b-11e9-94bc-9066698eaf5f.png)  
토큰은 json형식으로 출력됩니다.  
~~~json
{
    "access_token":"eyJraWQiOiIyMDE3M...",
    "refresh_token":"ReVRQ2E-AqUzvcyzk...",
    "ims_user_id":7538723,
    "token_type":"Bearer",
    "expires_in":3600,
    "expiration":1554866287,
    "scope":"ibm openid"
}
~~~
인증에 필요한 토큰은 `access_token`입니다.  
>주의하실 점은 expire되는 시간이 있기때문에 그 시간내에만 사용이 가능하고 만료되면 새로 토큰을 발급받아야 합니다.  
>파라미터를 전부 맞게 집어넣었는데 Access Denied가 뜬다면 이점을 고려해봅시다.  

### Obtain your resource instance id   
몇몇 커맨드는 `ibm-service-instance-id` 파라키터가 필요한 경우가 있습니다.  
이 파라미터 값은 클라우드 콘솔의 cos인스턴스 > 서비스 인증정보에서 확인할 수 있습니다.  

맨 처음에는 새인증정보만들기를 해서 확인하면 됩니다.  
[참고링크](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage)  
![image](https://user-images.githubusercontent.com/15958325/55845278-31bc3100-5b7c-11e9-9791-254a5e93fb34.png)  

~~~json
 { ...
    "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/93c46f889ce0417b869a8b66637a02d6:1c887618-84d1-44cf-b31b-028b7da1f42d::"
 }
~~~
제법 긴 `resource_instance_id`는 (예시에서)콜론뒤의 `1c887618-84d1-44cf-b31b-028b7da1f42d`로 줄여서 사용하시면 됩니다.  

## 3. API

위의 정보들을 잘 입력해주시면 됩니다.  

### List Bucket  
버킷의 리스트를 출력  

#### 입력
~~~bash
$ curl "https://(endpoint)/" \
 -H "Authorization: bearer (token)" \
 -H "ibm-service-instance-id: (resource-instance-id)"
~~~  
>예시) 
>~~~bash
>curl "https://s3.us-south.cloud-object-storage.appdomain.cloud/" \
>-H "Authorization: Bearer eyJraWQiOiIyMDE3MTEyOSIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQ..." \
> -H "ibm-service-instance-id: 1c887618-84d1-44cf-b31b-028b7da1f42d"  
> ~~~   
><b>(주의) Authorization부분에서 Bearer를 빼먹지 않도록 합시다.</b>

#### 출력
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID><DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName></Owner><Buckets><Bucket><Name>web-images-bucket</Name><CreationDate>2019-04-07T12:25:16.443Z</CreationDate></Bucket></Buckets></ListAllMyBucketsResult>
~~~  

### Add Bucket
버킷 생성  
#### 입력  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)" \
 -H "Authorization: Bearer (token)" \
 -H "ibm-service-instance-id: (resource-instance-id)"
~~~  

#### 출력 
-없음-

### Add a bucket (storage class)  
모든 데이터는 비즈니스 환경에 따라 스토리지에서 자주 꺼내쓸수도있고, 또는 10년동안 묵혀둘수도 있습니다.  
이렇게 활용빈도가 천차만별인 탓에 서로다른 스토리지 클래스를 적용하여 요금을 조정할수도 있습니다.  

- Standard : 데이터의 입출력이 활발한 워크로드에서 사용. 데이터를 읽는데 비용이 청구되지 않음.  
- Vault : 자주 access하지 않는 데이터가 많을 경우 사용. 데이터를 읽을 경우 비용이 청구됨.  
- Cold Vault : 더 자주 access하지 않는 데이터가 많을 경우에 사용. 데이터를 읽을 때 더 많은 비용이 청구됨.  
- Flex : access 패턴을 예측하기 어려운 dynamic한 경우에 사용됨.

가격정보는 아래 링크를 참조해주세요.  
[price table](https://www.ibm.com/cloud-computing/bluemix/pricing-object-storage#s3api)  

각 지역의 provisioning-code는 다음링크를 참조해주세요.  
[provisioning-code](https://cloud.ibm.com/docs/services/cloud-object-storage?topic=cloud-object-storage-use-storage-classes#locationconstraint)  

#### 입력  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)" \
 -H "Content-Type: text/plain; charset=utf-8" \
 -H "Authorization: Bearer (token)" \
 -H "ibm-service-instance-id: (resource-instance-id)" \
 -d "<CreateBucketConfiguration><LocationConstraint>(provisioning-code)</LocationConstraint></CreateBucketConfiguration>"
~~~

>예시)  
>~~~bash
>$ curl -X "PUT" "https://s3.us-south.cloud-object-storage.appdomain.cloud//test-bucket-api2" \
> -H "Content-Type: text/plain; charset=utf-8" \
> -H "Authorization: Bearer eyJraWQiOiIyMDE3MTEyOSIs..." \
> -H "ibm-service-instance-id: 1c887618-84d1-44cf-b31b-028b7da1f42d" \
> -d "<CreateBucketConfiguration><LocationConstraint>us-south-flex</LocationConstraint></CreateBucketConfiguration>"
>~~~


#### 출력  
-없음-  

![image](https://user-images.githubusercontent.com/15958325/55866638-b7130600-5bbb-11e9-9bd6-748fa8e0e42d.png)  

