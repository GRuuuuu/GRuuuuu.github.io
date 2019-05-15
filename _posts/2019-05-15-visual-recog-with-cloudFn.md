---
title: "Serverless Image Recognition with Cloud Functions"
categories: 
  - Simple-Tutorial
tags:
  - Cloudant
  - Watson
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 `Apache OpenWhisk`기반의 `IBM Cloud Functions`를 사용하여 `Cloudant`에 저장된 이미지를 `Watson Visual Recognition`으로 분류하는 application을 만들어 볼것입니다.

다음 문서를 직접 해보고 작성한 문서입니다.  
링크: [link](https://github.com/IBM/ibm-cloud-functions-refarch-serverless-image-recognition)  

>

## 2. Prerequisites
IBM Cloud 계정 : [link](https://console.bluemix.net)  
IBM Watson 계정 : [link](https://dataplatform.cloud.ibm.com/)  
> 환경이 window라면 git bash를 설치해주세요.  
> Git Bash : [link](https://gitforwindows.org/)  


## 3. Application Flow
application의 flow는 다음 그림과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/57744046-8b2af900-7702-11e9-89f5-dc8ba4a7d7ad.png)  

1. 이미지파일을 고릅니다.  
2. upload버튼을 통해 이미지파일은 Cloudant DB에 저장됩니다.  
3. 새로운 이미지가 DB에 저장되면 트리거에의해 Cloud Function이 실행됩니다.  
4. Cloud Function은 이미지를 가져와 처리를 위해 Watson Visual Recognition를 실행시킵니다.  
5. Visual Recognition의 결과값인 Score와 Class등을 Cloudant에 저장합니다.  
6. 유저는 자신이 업로드한 이미지에 대한 분류결과를 확인할 수 있습니다.  

