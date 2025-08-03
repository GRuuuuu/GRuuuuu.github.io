---
title: "Openshift4.3 Installation on AWS"
slug: ocp4-install-aws
tags:
  - Kubernetes
  - AWS
  - RHEL
  - Openshift
date: 2020-03-07T13:00:00+09:00
---

## Overview
이번 포스팅에서는 Openshift Container Platform 4.x 를 AWS에 설치해보도록 하겠습니다.   

# Prerequisites

- AWS계정
- Red Hat 계정
- linux서버 아무거나 하나

# 1. 설치 준비 단계

## Install AWS CLI
먼저 AWS CLI툴을 설치해줍니다.  

~~~sh
# Download the latest AWS Command Line Interface
$ curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"

$ unzip awscli-bundle.zip

# Install the AWS CLI into /bin/aws
$ ./awscli-bundle/install -i /usr/local/aws -b /bin/aws 
~~~

제대로 동작하는지 확인해주고 설치파일은 삭제해줍니다.  
~~~sh
# Validate that the AWS CLI works
aws --version

# Clean up downloaded files
rm -rf /root/awscli-bundle /root/awscli-bundle.zip
~~~
![image](https://user-images.githubusercontent.com/15958325/76138808-ee20be80-608d-11ea-8226-55940e2e95df.png)  

이제 아마존 크레덴셜파일을 생성해줄 차례입니다.  
본인의 계정을 참고해서 환경변수로 넣어주고, 파일로 만들어줍니다.
~~~sh
$ export AWSKEY=AKIAVLWERVDBNWD6DLGF
$ export AWSSECRETKEY=Q7766cxfyVX3NeJvgnruEEABCD39fUW8Fzq6AYc
$ export REGION=ap-southeast-1

$ mkdir $HOME/.aws
$ cat << EOF >>  $HOME/.aws/credentials
[default]
aws_access_key_id = ${AWSKEY}
aws_secret_access_key = ${AWSSECRETKEY}
region = $REGION
EOF
~~~

제대로 반영이 되었는지 체크해줍니다.  
~~~sh
$ aws sts get-caller-identity
~~~
![image](https://user-images.githubusercontent.com/15958325/76139808-4f00c480-6097-11ea-82d3-f642fcceb3ab.png)  


## Install Openshift Installer
이제 openshift installer binary파일을 다운받아줍니다.  

원하는 ocp버전을 설정해주고, 다운받아서 압축을 해제해줍니다. 
~~~sh
$ OCP_VERSION=4.3.1

$ wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-install-linux-${OCP_VERSION}.tar.gz

$ tar zxvf openshift-install-linux-${OCP_VERSION}.tar.gz -C /usr/bin

$ rm -f openshift-install-linux-${OCP_VERSION}.tar.gz /usr/bin/README.md
chmod +x /usr/bin/openshift-install
~~~

## Install oc CLI
kubernetes의 kubectl과 같은 역할을 해주는 oc cli툴을 설치해줍니다.  
~~~sh
$ wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux-${OCP_VERSION}.tar.gz

$ tar zxvf openshift-client-linux-${OCP_VERSION}.tar.gz -C /usr/bin

$ rm -f openshift-client-linux-${OCP_VERSION}.tar.gz /usr/bin/README.md

$ chmod +x /usr/bin/oc
~~~

제대로 설치되었는지 확인 :   
~~~sh
$ ls -l /usr/bin/{oc,openshift-install}
~~~
![image](https://user-images.githubusercontent.com/15958325/76138903-9a62a500-608e-11ea-8bc5-79d86a9b08c2.png)  

>+추가로 oc 커맨드에 대해 자동완성(bash completion)설정을 하려면 :  
>~~~sh
>$ oc completion bash >/etc/bash_completion.d/openshift
>~~~

## Get Pull Secret
이제 설치할때 필요한 **pull secret**을 얻어야 합니다.  
[RedHat Openshift Cluster Manager](https://cloud.openshift.com/clusters/install)로 이동  

<img src="https://user-images.githubusercontent.com/15958325/76142040-369ba480-60ad-11ea-801a-905c1e720f93.png" width="600px">   

openshift cluster를 올릴 플랫폼은 `aws`이니 `aws`를 선택해줍니다.  
물론 `vmware`나 `openstack`, `bare-metal`도 존재합니다.  

다음으로 `Installer-provisioned infrastructure`를 선택 :  
<img src="https://user-images.githubusercontent.com/15958325/76142042-38fdfe80-60ad-11ea-9d37-3fa3f709cd14.png" width="600px">    

> **Installer-Provisioned Infrastructure(IPI)** : 클러스터를 구성하는데 필요한 네트워크, 시스템, os 등의 모든 부분을 코드로 구현하여 사용자가 인프라를 프로비저닝할 필요가 없음  
>**User-Provisioned Infrastructure(UPI)** : installer는 클러스터만 구성해주고 사용자가 인프라에 대한것을 프로비저닝 해야한다. 더 세세한 구성이 가능.  

마지막으로 pull secret을 복사해둡니다.  
<img src="https://user-images.githubusercontent.com/15958325/76142397-a3646e00-60b0-11ea-86e1-09195262d439.png" width="600px">   

아래와 비슷한 형식입니다.  
~~~sh
{"auths":{"cloud.openshift.com":{"auth":"b3Bl...Qw==","email":"example@example.com"},"quay.io":{"auth":"b3Bl...Qw==","email":"example@example.com"},"registry.connect.redhat.com":{"auth":"NTMwN...N0VQ==","email":"example@example.com"},"registry.redhat.io":{"auth":"NTMwN...N0VQ==","email":"example@example.com"}}}
~~~

## SSH key 생성
ssh key를 생성해줍니다.  
~~~sh
$ ssh-keygen -f ~/.ssh/cluster-key -N ''
~~~

# Install OpenShift Container Platform
이제 본격적으로 설치를 시작해보겠습니다.  

<img src="https://user-images.githubusercontent.com/15958325/76138392-e7dd1300-608a-11ea-904f-93d92d870e56.png" width="600px">   

설치 순서는 다음과 같습니다.   
1. **Bootstrap 노드 생성**, 해당 노드는 마스터 노드 부팅에 필요한 리소스를 제공해줌
2. **마스터**는 리소스를 bootstrap노드에서 가져와 부팅을 마침
3. 마스터는 bootstrap 노드를 사용해 **etcd 클러스터를 구성**
4. bootstrap노드는 etcd클러스터를 사용해 **임시 쿠버네티스 컨트롤플레인**을 시작
5. 임시 컨트롤플레인은 **진짜 컨트롤플레인**을 마스터 머신에 올림
6. 임시 컨트롤플레인은 꺼지고 마스터머신의 컨트롤플레인으로 **컨트롤 권한**이 옮겨감
7. bootstrap노드는 마스터머신의 컨트롤플레인에 **openshift component**들을 넣음
8. Installer는 bootstrap노드를 다운시킴


설치커맨드는 간단하게 한줄로 끝납니다.   
~~~sh
$ openshift-install create cluster --dir $HOME/temp
~~~

![image](https://user-images.githubusercontent.com/15958325/76142803-56829680-60b4-11ea-97f7-01d1f0d53cbb.png)  
`SSH Public Key`는 위에서 생성했었던 ssh key  
`Platform`은 aws  
`Region`은 가까운곳으로 선택  
`Base Domain`은 ocp클러스터 라우트의 기본도메인으로 사용될 도메인을 선택  
`Cluster Name`은 유니크하게 작성  
`Pull Secret`은 위에서 복사했던 pull secret을 붙여넣기  

![image](https://user-images.githubusercontent.com/15958325/76142859-0ce67b80-60b5-11ea-8e47-657d7c700335.png)  

![image](https://user-images.githubusercontent.com/15958325/76142860-0e17a880-60b5-11ea-887b-02c82d35eb6f.png)  

설치가 완료되면 웹콘솔의 url과 클러스터 admin의 계정을 알려줍니다.  

<img src="https://user-images.githubusercontent.com/15958325/76142874-2e476780-60b5-11ea-9f0a-f38cb9b744da.png" width="600px">  

~~~sh
$ export KUBECONFIG=$HOME/temp/auth/kubeconfig
$ echo "export KUBECONFIG=$HOME/temp/auth/kubeconfig" >>$HOME/.bashrc

$ oc get nodes
~~~

![image](https://user-images.githubusercontent.com/15958325/76142904-51721700-60b5-11ea-8e98-c4eefbcfc183.png)  


클러스터를 삭제하려면 :  

~~~sh
$ openshift-install destroy cluster --dir $HOME/temp

$ rm -rf $HOME/.kube 
$ rm -rf $HOME/temp
~~~

끗

----