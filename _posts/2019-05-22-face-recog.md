---
title: "Face Recognition Terminal"
categories: 
  - Simple-Tutorial
tags:
  - IoT
  - Cloud
  - OpenCV
  - Watson
  - ICOS
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 local에서 실시간으로 촬영한 얼굴 이미지를 `Watson Visual Recognition`으로 분석하여 web UI로 볼 수 있게 구성해 보겠습니다.  

> 말로는 간단하지만 중간에 어떤 복잡한 과정이 존재할지...ㅎㅎ

다음 문서를 직접 해보고 작성한 문서입니다.  
Chapter 6. Face Recognition Terminal: [link](https://www.redbooks.ibm.com/redbooks/pdfs/sg248385.pdf)  

## 2. Prerequisites
IBM Cloud 계정 : [link](https://console.bluemix.net)  
IBM Watson 계정 : [link](https://dataplatform.cloud.ibm.com/)  
Python설치 : [link](https://www.python.org/downloads/)  
Node js설치 : [link](https://nodejs.org/ko/)   

>**Local Test version**  
>`Node js` : v10.15.3  
>`Python` : v3.7.3   

## 3. Architecture
프로젝트의 구조는 아래 사진과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/58142773-5c250200-7c83-11e9-8956-efe1a8d900aa.png)


