---
title: "ICOS - S3 API with NodeJS"
categories: 
  - Docs
tags:
  - ICOS
  - Nodejs
last_modified_at: 2019-03-22T13:00:00+09:00
toc : true
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

In this recipe, we will show how to do basic operations with Cloud Object Storage using the same S3 API.  

## 1. Overview
이 문서에서는 Nodejs로 ICOS를 사용하는 법을 알아보도록 하겠습니다.  

## 2. Environment
`Nodejs : v10.15.3`  
`npm : 6.4.1`  
`aws-sdk : ^2.438.0`  
`express : ^4.16.4`  

Icos 생성 및 credential얻기 : [https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage)   

>생성할때 `access_key_id`와 `secret_access_key`는 메모해둡시다.  

`endpoint` : cos>Buckets>Configuration에서 해당 정보를 확인할 수 있습니다.  
![Image](https://user-images.githubusercontent.com/15958325/55774768-89519280-5ad1-11e9-8bf6-ea9a5cf7577b.png)

## 3. API

>AWS s3 api doc : [link](https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html#)  
>아래 예시에서 사용하는 소스코드 : [link](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/simple-tutorial/ICOS02/icos-s3-api-test/galleryController.js)  

js에서 s3모듈을 사용하기 위해 aws-sdk를 추가합니다.  
~~~js
//aws api를 사용하기위해 추가
var aws = require('aws-sdk'); 
~~~  

### 3.1 Create S3 Client 

aws.s3 api를 사용하기 위한 인증정보들을 추가합니다.  

~~~js
//s3프로토콜을 위한 정보 기입
    var ep = new aws.Endpoint('https://s3.us-south.cloud-object-storage.appdomain.cloud');
    var s3 = new aws.S3({
        endpoint: ep, 
        region: 'us-south',
        accessKeyId:'b01c551bb9604c8ebc22fefe36e4fbc7',
        secretAccessKey:'06d88e8c4d75adba1d51ce863144fe29b02d6fcb36c15f39'
    });
~~~  

### 3.2 Create Bucket
버킷을 생성합니다.  

~~~js
var createBucket=function(req,res){
  //bucket 이름은 unique해야함.
  var params = {Bucket: '190418testbucket'};
  s3.createBucket(params, function(err) {
      console.log("checking for error on createBucket " + params.Bucket, err);
  });
};
~~~

#### response
~~~c
//success
null
~~~  

>cos 인스턴스에 가서 확인해보면 버킷이 생성된 것을 확인할 수 있습니다.  
>![image](https://user-images.githubusercontent.com/15958325/56328786-80d91600-61bb-11e9-9c73-e715022bcf1c.png)  


### 3.3 Storing Object

버킷에 file object를 저장합니다.  

~~~js
var putObject=function(req,res){
    var data = {Bucket: '{버킷이름}', Key: '{저장할 파일의 이름}', Body: require('fs').createReadStream('{파일경로}')};
    s3.putObject(data, function(err, data) {
      if (err) {
        console.log("Error uploading data: ", err);
      } else {
        console.log("Successfully uploaded file to bucket");
      }
    });
};
~~~

>multer 모듈을 쓰는 방법은 다음 링크를 참고 : [링크](https://gruuuuu.github.io/simple-tutorial/icos-api/#upload)

#### response
~~~json
//success
{"ETag":"\"99fb31087791f6317ad7c6da1433f172\""}
~~~

### 3.4 Listing Object

bucket에 담긴 object들의 리스트를 반환합니다.  

~~~js
var getGalleryImages = function (req, res) {
    var params = {Bucket: {버킷이름};
    s3.listObjectsV2(params, function (err, data) {
        if(data) {
            console.log("listing " + myBucket, [err, JSON.stringify(data)]);
        }
    });
};
~~~

#### response
~~~json
//success
{
  "IsTruncated":false,
  "Contents":[{
    "Key":"hellohello.txt",
    "LastModified":"2019-04-18T02:16:40.853Z",
    "ETag":"\\"99fb31087791f6317ad7c6da1433f172\\"",
    "Size":15, "StorageClass":"STANDARD"},
    {"Key":"mykey",
    "LastModified":"2019-04-18T01:31:02.978Z",
    "ETag":"\\"952d2c56d0485958336747bcdd98590d\\"",
    "Size":6,"StorageClass":"STANDARD"},
    {"Key":"test.txt",
    "LastModified":"2019-04-18T04:14:57.559Z",
    "ETag":"\\"99fb31087791f6317ad7c6da1433f172\\"",
    "Size":15,"StorageClass":"STANDARD"
    }],
  "Name":"190418testbucket","Prefix":"",
  "Delimiter":"","MaxKeys":1000,
  "CommonPrefixes":[],"KeyCount":3
}
~~~

### 3.5 Deletion of Objects 
버킷에 담긴 object들을 삭제합니다.  

~~~js
var delObject=function(req,res){
    var itemsToDelete = Array();
        itemsToDelete.push ({ Key : '{file이름}' });
        itemsToDelete.push ({ Key : '{file이름}' });
    var params = {Bucket: myBucket,
        Delete: {
            Objects: itemsToDelete,
            Quiet: false}};
    s3.deleteObjects(params, function(err, data) {
        if (err) {
          console.log("Error data: ", err);
        } else {
          console.log("checking for data "+ JSON.stringify(data));
        };
    });
}
~~~

#### response
~~~json
//success
{"Deleted":[],"Errors":[]}
~~~  


### 3.6 Deletion of Bucket

버킷을 삭제합니다.

~~~js
var delBucket=function(req,res){
    var params={Bucket:{버킷이름}};
    s3.deleteBucket(params, function(err, data) {
      if (err) {
        console.log("Error data: ", err);
        } 
      else {
        console.log("checking for data "+ JSON.stringify(data));
        };
    });
}
~~~

#### response
~~~
//success
null
~~~

----