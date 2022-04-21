---
title: "Curl Command for ICOS REST API"
categories: 
  - ICOS
tags:
  - ICOS
last_modified_at: 2019-04-10T13:00:00+09:00
toc : true
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


## 1. IBM Cloud Object Storage API
IBM Cloud Object Storage API는 객체 읽기 및 쓰기를 위한 REST 기반 API 입니다. 인증을 위해 IBM Cloud Identity와 Access Management를 사용하며, S3 API의 서브셋을 지원하여 app이 IBM Cloud로 쉽게 마이그레이션되도록 합니다.   

아래 챕터부터 CLI환경에서 curl command를 이용해 ICOS와 통신하는것에 대해 기술하겠습니다.  

>수정  
>22.04.21 upload object API부분 local file 경로받는 부분을  `--data-binary @`로 변경  

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
>파라미터를 전부 맞게 집어넣었는데 Access Denied가 뜬다면 이 점을 고려해봅시다.  

### Obtain your resource instance id   
몇몇 커맨드는 `ibm-service-instance-id` 파라미터가 필요한 경우가 있습니다.  
이 파라미터 값은 클라우드 콘솔의 cos인스턴스 > 서비스 인증정보에서 확인할 수 있습니다.  

맨 처음에는 새 인증정보 만들기를 해서 확인하면 됩니다.  
[참고링크](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage)  
![image](https://user-images.githubusercontent.com/15958325/55845278-31bc3100-5b7c-11e9-9791-254a5e93fb34.png)  

~~~json
 { ...
    "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/
    93c46f889ce0417b869a8b66637a02d6:1c887618-84d1-44cf-b31b-028b7da1f42d::"
 }
~~~
제법 긴 `resource_instance_id`는 (예시에서)콜론뒤의 `1c887618-84d1-44cf-b31b-028b7da1f42d`로 줄여서 사용하시면 됩니다.  

## 3. API

위의 정보들을 잘 입력해주시면 됩니다.  

### 3.1 List Bucket  
버킷의 리스트를 출력  

**입력**  
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

**출력**  
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Owner>
    <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
    <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
  </Owner>
  <Buckets><Bucket>
    <Name>web-images-bucket</Name>
    <CreationDate>2019-04-07T12:25:16.443Z</CreationDate>
  </Bucket></Buckets>
</ListAllMyBucketsResult>
~~~  

### 3.2 Add Bucket
버킷 생성  

**입력**    
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)" \
 -H "Authorization: Bearer (token)" \
 -H "ibm-service-instance-id: (resource-instance-id)"
~~~  

**출력**  
-없음-

### 3.3 Add a bucket (storage class)  
모든 데이터는 비즈니스 환경에 따라 스토리지에서 자주 꺼내쓸수도있고, 또는 10년동안 묵혀둘수도 있습니다.  
이렇게 활용빈도가 천차만별인 탓에 서로다른 스토리지 클래스를 적용하여 요금을 조정할수도 있습니다.  

- `Standard` : 데이터의 입출력이 활발한 워크로드에서 사용. 데이터를 읽는데 비용이 청구되지 않음.  
- `Vault` : 자주 access하지 않는 데이터가 많을 경우 사용. 데이터를 읽을 경우 비용이 청구됨.  
- `Cold Vault` : 더 자주 access하지 않는 데이터가 많을 경우에 사용. 데이터를 읽을 때 더 많은 비용이 청구됨.  
- `Flex` : access 패턴을 예측하기 어려운 dynamic한 경우에 사용됨.

가격정보는 아래 링크를 참조해주세요.  
[price table](https://www.ibm.com/cloud-computing/bluemix/pricing-object-storage#s3api)  

각 지역의 provisioning-code는 다음링크를 참조해주세요.  
[provisioning-code](https://cloud.ibm.com/docs/services/cloud-object-storage?topic=cloud-object-storage-use-storage-classes#locationconstraint)  

**입력**   
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


**출력**   
-없음-  

![image](https://user-images.githubusercontent.com/15958325/55866638-b7130600-5bbb-11e9-9bd6-748fa8e0e42d.png)  

### 3.4 Check a bucket ACL
bucket의 ACL권한 확인  

Amazon S3 ACL(Access Control Lists)은 bucket과 객체에 대한 access를 관리합니다. 각 bucket과 객체마다 액세스를 허용할 계정이나 그룹, 유형등을 정의할 수 있습니다.  
기본적으로 리소스에 대한 모든 권한을 부여하는 `FULL_CONTROL`권한이 부여됩니다.  
참고링크 : [AMAZON S3 ACL-Overview](https://docs.aws.amazon.com/ko_kr/AmazonS3/latest/dev/acl-overview.html)  

ACL권한 | bucket권한 
--------|-----------
READ | s3:ListBucket, s3:ListBucketVersions, s3:ListBucketMultipartUploads
WRITE | s3:PutObject, s3:DeleteObject, 피부여자가 소유권자일경우 s3:DeleteObjectVersion가능 
READ_ACP | s3:GetBucketAcl
WRITE_ACP | s3:PutBucketAcl
FULL_CONTROL | 모든 권한

**입력**  
~~~bash
$ curl "https://(endpoint)/(bucket-name)/?acl" \
 -H "Authorization: bearer (token)"
~~~

**출력**  
default로 소유자에게 `FULL_CONTROL`권한이 부여된 것을 확인할 수 있습니다.  

~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Owner>
    <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
    <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
  </Owner>
  <AccessControlList>
    <Grant>
      <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
        <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
        <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
      </Grantee>
      <Permission>FULL_CONTROL</Permission>
    </Grant>
  </AccessControlList>
</AccessControlPolicy>
~~~

### 3.5 Change bucket ACL  

bucket의 ACL권한 변경  

>aws에서는 굉장히 다양한 canned ACL을 제공하지만 ICOS에서 bucket에 적용되는건 private와 public-read만 가능합니다.  
>
>![image](https://user-images.githubusercontent.com/15958325/55880567-efc2d780-5bdb-11e9-9acd-5a458622ba03.png)  

**입력**  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)/?acl" \
 -H "Authorization: bearer (token)" \
 -H "x-amz-acl: (ACL policy)"
~~~  

>예시)
>~~~bash
>$ curl -X "PUT" "https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/?acl" \
>  -H "Authorization: bearer eyJraWQiOiIyMDE3MTEyO..." \
>  -H "x-amz-acl: public-read"
>~~~

**출력**  

-없음-  

> public-read로 ACL권한을 변경했을 경우,  
>권한을 변경한 bucket의 ACL권한을 체크해보면 소유자 외 타 모든 유저들의 권한이 READ로 바뀐것을 확인해볼수 있습니다.  
> 
>~~~xml
><?xml version="1.0" encoding="UTF-8" standalone="yes"?>
><AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
>  <Owner>
>    <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
>    <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
>  </Owner>
>  <AccessControlList>
>    <Grant>
>      <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">
>        <URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>
>      </Grantee>
>      <Permission>READ</Permission>
>    </Grant>
>  </AccessControlList>
></AccessControlPolicy>
>~~~  

### 3.6 Create a bucket CORS  

bucket의 CORS 설정  

CORS(Cross-Orign Resource Sharing). 한마디로 근원이 다른 자원들을 공유하기. 즉 다른Origin에서 제공하는 자원에 접근할 수 있는 방법입니다. Origin이라 함은 물리적인 서버뿐만이아니라 서브도메인이 다르거나 포트가 다른것도 다른 Origin으로 간주됩니다.  
브라우저의 [Same-Orign policy](https://en.wikipedia.org/wiki/Same-origin_policy)를 합법적으로 우회해서 다른 Origin에서 제공하는 자원에 접근하고 싶을때 사용합니다.  

**입력**   
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)/?cors" \
 -H "Content-MD5: (md5-hash)" \
 -H "Authorization: bearer (token)" \
 -H "Content-Type: text/plain; charset=utf-8" \
 -d "<CORSConfiguration><CORSRule><AllowedOrigin>(url)</AllowedOrigin><AllowedMethod>(request-type)</AllowedMethod><AllowedHeader>(url)</AllowedHeader></CORSRule></CORSConfiguration>"
~~~  

Content-MD5는 xml block을 base64로 인코딩한 값이 들어가게 됩니다.  
~~~bash
$ echo -n (XML block) | openssl dgst -md5 -binary | openssl enc -base64
~~~  
xml block은 적용하고자하는 CORS을 구성하는 xml정보가 들어가면 됩니다.  
> 예시)
>`AllowedOrigin`에 적용하고자하는 bucket의 url, `request-type`에 POST를 넣고 `AllowedHeader`에 모든 Origin의 요청을 뜻하는 *을 넣고 인코딩을 하게되면 다음과 같은 커맨드가 완성됩니다. `AllowedHeader`에는 bucket과 통신하고싶은 다른 Origin의 헤더를 뜻합니다.    
>~~~bash
>$ echo -n "<CORSConfiguration><CORSRule><AllowedOrigin>https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/</AllowedOrigin><AllowedMethod>POST</AllowedMethod><AllowedHeader>*</AllowedHeader></CORSRule></CORSConfiguration>" | openssl dgst -md5 -binary | openssl enc -base64
>
>결과 : i1BSauZknPpaga10iAThvQ==
>~~~  

>그래서 완성된 커맨드라인은 다음과 같습니다.  
>~~~bash
>$ curl -X "PUT" "https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/?cors" \
> -H "Content-MD5: i1BSauZknPpaga10iAThvQ==" \
> -H "Authorization: bearer eyJraWQiOiIyMDE3MTEyOSIsImF..." \
> -H "Content-Type: text/plain; charset=utf-8" \
> -d "<CORSConfiguration><CORSRule><AllowedOrigin>https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/</AllowedOrigin><AllowedMethod>POST</AllowedMethod><AllowedHeader>*</AllowedHeader></CORSRule></CORSConfiguration>"
>~~~

**출력**  
-없음-  


### 3.7 Get a bucket CORS  
bucket의 CORS를 출력합니다.  

**입력**  
~~~bash
$ curl "https://(endpoint)/(bucket-name)/?cors" \
 -H "Authorization: bearer (token)"
~~~  

**출력**  
3.6을 하고 난 다음의 결과. POST규칙이 생긴것을 확인할 수 있습니다.  

~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <CORSRule>
  <AllowedMethod>POST</AllowedMethod>
  <AllowedOrigin>https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/</AllowedOrigin>
  <AllowedHeader>*</AllowedHeader>
  </CORSRule>
</CORSConfiguration>
~~~  

### 3.8 Delete a bucket CORS
bucket의 CORS를 삭제합니다.  

**입력**  
~~~bash
$ curl -X "DELETE" "https://(endpoint)/(bucket-name)/?cors" \
 -H "Authorization: bearer (token)"
~~~  

**출력**  
-없음-  

> 3.7의 GET bucket CORS를 실행해보면 CORS가 사라진것을 확인할 수 있습니다.  
>~~~xml
><?xml version="1.0" encoding="UTF-8" standalone="yes"?>
><Error>
>  <Code>NoSuchCORSConfiguration</Code>
>  <Message>The CORS configuration does not exist</Message>
>  <Resource>/test-bucket-api/</Resource>
>  <RequestId>27592942-b9b3-4fbd-8b77-c74eb7fb4cfc</RequestId>
>  <httpStatusCode>404</httpStatusCode>
></Error>
>~~~  

### 3.9 List objects  
bucket의 object 리스트를 출력  

**입력**  
~~~bash
$ curl "https://(endpoint)/(bucket-name)" \
 -H "Authorization: bearer (token)"
~~~  

**출력**  
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Name>test-bucket-api</Name>
  <Prefix></Prefix>
  <Marker></Marker>
  <MaxKeys>1000</MaxKeys>
  <Delimiter></Delimiter>
  <IsTruncated>false</IsTruncated>
  <Contents>
  <Key>images.jpg</Key>
  <LastModified>2019-04-11T00:14:03.848Z</LastModified>
  <ETag>&quot;db8250affcef03657f7dc900feb83d5f&quot;</ETag>
  <Size>6683</Size>
  <Owner>
    <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
    <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
  </Owner>
  <StorageClass>STANDARD</StorageClass>
  </Contents>
</ListBucketResult>
~~~  

### 3.10 Get bucket headers
bucket의 헤더정보를 가져옵니다.  

**입력**  
~~~bash
$ curl --head "https://(endpoint)/(bucket-name)" \
 -H "Authorization: bearer (token)"
~~~
**출력**  
~~~
TP/1.1 200 OK
Date: Thu, 11 Apr 2019 00:22:08 GMT
X-Clv-Request-Id: 0c826d86-0786-44c8-ab3a-d4acc23bd5cd
Server: 3.14.3.47
X-Clv-S3-Version: 2.5
Accept-Ranges: bytes
x-amz-request-id: 0c826d86-0786-44c8-ab3a-d4acc23bd5cd
ibm-sse-kp-enabled: false
Content-Length: 0
~~~

### 3.11 Delete a bucket  
bucket을 삭제합니다.  

**입력**  
~~~bash
$ curl -X "DELETE" "https://(endpoint)/(bucket-name)/" \
 -H "Authorization: bearer (token)"
~~~
**출력**  
-없음-  

>삭제하려는 bucket이 비어있지 않다면 에러메세지가 뜹니다.  
>~~~xml
><?xml version="1.0" encoding="UTF-8" standalone="yes"?>
><Error>
>  <Code>BucketNotEmpty</Code>
>  <Message>The bucket you tried to delete is not empty.</Message>
>  <Resource>/web-images-bucket/</Resource>
>  <RequestId>7aeabc50-d5f1-4b02-bbc9-9c6ef0e5a32c</RequestId>
>  <httpStatusCode>409</httpStatusCode>
></Error>
>~~~  

### 3.12 Upload an object
bucket에 object를 업로드합니다.  

**입력**  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)/(object-key)" \
 -H "Authorization: bearer (token)" \
 -H "Content-Type: (content-type)" \
 --data-binary @"(local-file-path)"
~~~  
`object-key`에는 파일의 name과 확장자  
`content-type`은 파일의 확장자에 따른 type정보. 다음링크를 참고 -> [content-type](https://www.iana.org/assignments/media-types/media-types.xhtml)  
`local-file-path`에는 업로드하려는 파일의 로컬 경로  
>예시)   
>~~~bash
>curl -X "PUT" "https://s3.us-south.cloud-object-storage.appdomain.cloud/test-bucket-api/cat.png" \
> -H "Authorization: bearer eyJraWQiOiIyMDE3MTE..." \
> -H "Content-Type: image/png" \
> --data-binary @"/cat.png"
>~~~  

**출력**  
-없음-  
> bucket에 가보면 파일이 추가된것을 확인할 수 있습니다.  
>![image](https://user-images.githubusercontent.com/15958325/55925891-13246b80-5c4a-11e9-975e-ebfe5df1bb3c.png)  

### 3.13 Get an object's headers
object의 header를 출력합니다.  

**입력**   
~~~bash
$ curl --head "https://(endpoint)/(bucket-name)/(object-key)" \
 -H "Authorization: bearer (token)"
~~~  

**출력**   
~~~
TP/1.1 200 OK
Date: Thu, 11 Apr 2019 02:14:14 GMT
X-Clv-Request-Id: dfb63a37-7ca0-4d5d-b0a9-a2b7bfc0a567
Server: 3.14.3.47
X-Clv-S3-Version: 2.5
Accept-Ranges: bytes
x-amz-request-id: dfb63a37-7ca0-4d5d-b0a9-a2b7bfc0a567
ETag: "4fe8c0df4f9ae6e8d0e58926bec9d641"
Content-Type: image/png
Last-Modified: Thu, 11 Apr 2019 02:05:38 GMT
Content-Length: 28
~~~  

### 3.14 Copy an object  
object를 복사합니다.  

**입력**  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)/(object-key(dest))" \
 -H "Authorization: bearer (token)" \
 -H "x-amz-copy-source: /(bucket-name)/(object-key(src))"
~~~  
`object-key(dest)`는 복사해서 새로 만드려는 파일의 이름  
`object-key(src)`는 복사하려는 파일의 이름  

**출력**  
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<CopyObjectResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <LastModified>2019-04-11T02:17:16.743Z</LastModified>
  <ETag>&quot;4fe8c0df4f9ae6e8d0e58926bec9d641&quot;</ETag>
</CopyObjectResult>
~~~  

### 3.15 Download an object  
object를 다운로드합니다.  

**입력**  

~~~bash
$ curl "https://(endpoint)/(bucket-name)/(object-key)" \
 -H "Authorization: bearer (token)"
~~~  

**출력**  
~~~
/Program Files/Git/cat.png
~~~  
 
### 3.16 Check object's ACL  
object의 ACL을 확인합니다.  

**입력**  
~~~bash
$ curl "https://(endpoint)/(bucket-name)/(object-key)?acl" \
 -H "Authorization: bearer (token)"
~~~   

**출력**  
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Owner>
    <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
    <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
  </Owner>
  <AccessControlList>
    <Grant>
      <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
      <ID>1c887618-84d1-44cf-b31b-028b7da1f42d</ID>
      <DisplayName>1c887618-84d1-44cf-b31b-028b7da1f42d</DisplayName>
      </Grantee>
      <Permission>FULL_CONTROL</Permission>
    </Grant>
  </AccessControlList>
</AccessControlPolicy>
~~~  

### 3.17 Allow anonymous access to an object
아무나 object에 접근할 수 있게 합니다.  

**입력**  
~~~bash
$ curl -X "PUT" "https://(endpoint)/(bucket-name)/(object-key)?acl" \
 -H "Content-Type: (content-type)" \
 -H "Authorization: bearer (token)" \
 -H "x-amz-acl: public-read"
~~~  

**출력**  
-없음-  

### 3.18 Delete an object  
object를 삭제합니다.  

**입력**  
~~~bash
$ curl -X "DELETE" "https://(endpoint)/(bucket-name)/(object-key)" \
 -H "Authorization: bearer (token)"
~~~  

**출력**  
-없음-  

### 3.19 Delete multiple objects  
여러개의 object를 동시에 삭제합니다.  

**입력**  
~~~bash
$ curl -X "POST" "https://(endpoint)/(bucket-name)?delete" \
 -H "Content-MD5: (md5-hash)" \
 -H "Authorization: bearer (token)" \
 -H "Content-Type: text/plain; charset=utf-8" \
 -d "<Delete><Object><Key>(object1)</Key></Object><Object><Key>(object2)</Key></Object></Delete>"
~~~   

>예시)  
>`Content-MD5` : gSv/+7KDNhb+Gv2vSVq7WQ==  
>~~~bash
>$ echo -n "<Delete><Object><Key>ttt.png</Key></Object><Object><Key>cat.png</Key></Object></Delete>" | openssl dgst -md5 -binary | openssl enc -base64  
>
>result: gSv/+7KDNhb+Gv2vSVq7WQ==
>~~~   

**출력**   

~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DeleteResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Deleted>
    <Key>ttt.png</Key>
  </Deleted>
  <Deleted>
    <Key>cat.png</Key>
  </Deleted>
</DeleteResult>
~~~  

## 3.20 Multipart
사이즈가 매우 큰 파일을 분할하여 병렬 upload 처리를 하는 방법입니다.  

4가지 step을 밟아야 합니다.
1. 파일쪼개기
2. Multipart 시작
3. Part단위로 upload
4. upload된 Part들을 하나의 파일로 묶어서 저장

### 3.20.1 파일쪼개기  
ex) Linux의 경우 `split`사용
~~~
$ split -n 4 random_zipcodeKR.txt random_zipcodeKR.txt_

$ ls -alh
total 2.4G
drwxrwxr-x  2 gru gru 4.0K Apr 21 07:15 .
drwxr-xr-x 17 gru gru 4.0K Apr 21 07:14 ..
-rwxrwxr-x  1 gru gru 1.2G Dec 28 15:15 random_zipcodeKR.txt
-rw-rw-r--  1 gru gru 295M Apr 21 07:15 random_zipcodeKR.txt_aa
-rw-rw-r--  1 gru gru 295M Apr 21 07:15 random_zipcodeKR.txt_ab
-rw-rw-r--  1 gru gru 295M Apr 21 07:15 random_zipcodeKR.txt_ac
-rw-rw-r--  1 gru gru 295M Apr 21 07:16 random_zipcodeKR.txt_ad 
~~~
### 3.20.2 Multipart Upload 시작하기

**입력**  
~~~
curl -X "POST" "https://(endpoint)/(bucket-name)/(object-key)?uploads"
 -H "Authorization: bearer (token)"
~~~

**출력**
~~~xml
<InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Bucket>some-bucket</Bucket>
  <Key>multipart-object-123</Key>
  <UploadId>01000750-45a2-8152-9314-27b6cabc412a</UploadId>
</InitiateMultipartUploadResult>
~~~

### 3.20.3 part upload

**입력**  
~~~
curl -X "PUT" "https://(endpoint)/(bucket-name)/(object-key)?partNumber=(sequential-integer)&uploadId=(upload-id)"
 -H "Authorization: bearer (token)"
 -H "Content-Type: (content-type)"
 --data-binary @"(file-path)"
~~~

순차적으로 `sequential-integer` 값 할당. (n>1, n<10000)  
`upload-id` 에는 위에서 받은 id값 할당  

>예시)   
>~~~bash
>curl -X "PUT" "https://cloud-object-storage-url/bucketName/sample1G.txt?partNumber=1&uploadId=01000750-45a2-8152-9314-27b6cabc412a" \
> -H "Authorization: bearer $TOKEN" \
>--data-binary @"./random_zipcodeKR.txt_aa"
>~~~   
>파일이 1개 이상이면 `partNumber`를 1씩 증가시키면서 upload해야함  

**출력**  
`-vvv`을 붙여야 필요한 값을 얻을 수 있음  
~~~
...
* Mark bundle as not supporting multiuse
< HTTP/1.1 100 Continue
* We are completely uploaded and fine
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Date: Thu, 01 Jan 1970 00:00:00 GMT
< X-Clv-Request-Id: 71b2ccf7-3e90-4439-a324-27e0a5db6108
< Server: Cleversafe
< X-Clv-S3-Version: 2.5
< x-amz-request-id: 71b2ccf7-3e90-4439-a324-27e0a5db6108
< ETag: "f6dc63cad9838b4ee8811393472bc9ab"
< Content-Length: 0
~~~

뒤에서 분할 업로드 된 파일들을 식별하는 식별자로 `ETag`값을 사용하니, 반드시 메모해둘것  

### 3.20.4 Complete a multipart upload

**입력**  
~~~
curl -X "POST" "https://(endpoint)/(bucket-name)/(object-key)?uploadId=(upload-id)"
 -H "Authorization: bearer (token)"
 -H "Content-Type: text/plain; charset=utf-8"
 -d "<CompleteMultipartUpload>
         <Part>
           <PartNumber>1</PartNumber>
           <ETag>(etag)</ETag>
         </Part>
         <Part>
           <PartNumber>2</PartNumber>
           <ETag>(etag)</ETag>
         </Part>
       </CompleteMultipartUpload>"
~~~
위에서 얻은 ETag값을 순차적으로 넣을 것

>예시)  
>`Content-MD5` : gSv/+7KDNhb+Gv2vSVq7WQ==  
>~~~bash
>curl -X "POST" "https://cloud-object-storage-url/bucketName/sample1G.txt?uploadId=01000750-45a2-8152-9314-27b6cabc412a" \
> -H "Authorization: $TOKEN" \
> -H "Content-Type: text/plain; charset=utf-8" \
> -d "<CompleteMultipartUpload>
>         <Part>
>           <PartNumber>1</PartNumber>
>           <ETag>f6dc63cad9838b4ee8811393472bc9ab</ETag>
>         </Part>
>         <Part>
>           <PartNumber>2</PartNumber>
>           <ETag>67cbdbde0503410f21f7cead601d6c0e</ETag>
>         </Part>
>...
>       </CompleteMultipartUpload>"
>~~~  

**출력**  
~~~xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<CompleteMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Location>http://cloud-object-storage-url/bucketName/sample1G.txt</Location>
  <Bucket>bucketName</Bucket>
  <Key>sample1G.txt</Key>
  <ETag>"ca54e12384f94c2f2bb6a7cff8848936-4"</ETag>
</CompleteMultipartUploadResult>
~~~

<img width="1247" alt="image" src="https://user-images.githubusercontent.com/15958325/164446656-69f91ae5-3a5c-432b-a5ee-b08c7205f36d.png">  



### 3.20.5 아직 안끝난 multipart upload 보기

**입력**   
~~~
curl "https://(endpoint)/(bucket-name)/?uploads"
 -H "Authorization: bearer (token)"
~~~

**출력**   

~~~
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ListMultipartUploadsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Bucket>bucketName</Bucket>
  <KeyMarker/>
  <UploadIdMarker/>
  <NextKeyMarker>sample1G.txt</NextKeyMarker>
  <NextUploadIdMarker>01000750-45a2-8152-9314-27b6cabc412a</NextUploadIdMarker>
  <MaxUploads>1000</MaxUploads>
  <IsTruncated>false</IsTruncated>
  <Upload>
    <Key>sample1G.txt</Key>
    <UploadId>01000750-45a2-8152-9314-27b6cabc412a</UploadId>
    <Initiator>
      <ID>576d6bf3-acc4-4a07-bbeb-2352e614469b</ID>
      <DisplayName>576d6bf3-acc4-4a07-bbeb-2352e614469b</DisplayName>
    </Initiator>
    <Owner>
      <ID>576d6bf3-acc4-4a07-bbeb-2352e614469b</ID>
      <DisplayName>576d6bf3-acc4-4a07-bbeb-2352e614469b</DisplayName>
    </Owner>
    <StorageClass>STANDARD</StorageClass>
    <Initiated>2022-04-21T05:40:05.794Z</Initiated>
  </Upload>
</ListMultipartUploadsResult>
~~~

### 3.20.6 아직 안끝난 multipart upload 삭제하기

**입력**   
~~~
curl -X "DELETE" "https://(endpoint)/(bucket-name)/(object-key)?uploadId=(uploadId)"
 -H "Authorization: bearer (token)"
~~~

**출력**  
없음


끗

----