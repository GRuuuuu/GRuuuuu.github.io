---
title: "OpenShift Assisted Installer로 설치해보기!"
categories:
  - OCP
tags:
  - Kubernetes
  - Openshift
last_modified_at: 2023-07-23T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview

최근엔 OpenShift 설치를 해볼일이 많지 않아서 그냥 예전에 해왔던 방식대로, PXE부팅으로 CoreOS를 구성하거나 직접 콘솔로 들어가서 network 세팅해주고 OS 파라미터 설정해주는 등의 일들을 해왔었는데....   
해보신 분들은 아시겠지만 매우매우매우 귀찮습니다. 콘솔 권한이 있다면 문제가 생기더라도 트러블슈팅하면서 할 수 있겠지만, 권한마저 없다면 거기서부터는 난감한 일들 투성이죠.   

그러던 차, 획기적인 방식을 찾았습니다! 무려 4.10 버전부터 지원하게된 **Assisted Installer** 입니다!  
여전히 UPI방식이라면 bastion노드를 세팅해야하는 필요성이 존재하고, 몇가지 제약사항이 있긴 하지만 생각보다 쉽고 편하게 설치할 수 있어 앞으로 많이 애용할 것 같습니다.  


## Assisted Installer
Assisted Installer는 RedHat에서 SaaS형태로 제공되며, 사용하기 편하게 GUI를 제공합니다.  

1. Web User Interface 제공
2. 따로 Bootstrap용 노드를 만들 필요가 없음
3. 설치하기 전에 설정들의 validation check를 자동으로 해줌
4. Single Node OpenShift도 지원
5. REST API 제공

### Basic Flow
설치 과정을 소개하기 전에, Assisted Installer로 설치할 때의 기본 flow를 설명드리겠습니다.  

1. 최소 구성정보만 가지고 **Cluster Resource** 생성
2. network, domain, storage 등의 커스텀 구성정보들을 바탕으로 **부팅이미지 생성**, RHCOS이미지 기반이며 설치를 위한 agent가 자동으로 돌아가게 포함되어있음
3. 부팅이미지로 **부팅**
4. agent가 돌면서 Assisted Installer와 **REST API를 통해 연결** (하드웨어 inventory정보와 connectivity information을 송신)
5. 유저는 **web화면**에서 discovery 및 나머지 Installation작업을 수행가능
6. 모든 구성정보에 대한 validation check가 성공하면 **OpenShift설치를 시작**, 진행상황은 Web혹은 API로 확인가능

>참고 문서 :   
> 1. **OpenShift Doc** : [Installing an on-premise cluster using the Assisted Installer](https://docs.openshift.com/container-platform/4.13/installing/installing_on_prem_assisted/installing-on-prem-assisted.html) (Overall한 내용)  
>2. **RedHat Product Documentation** : [Assisted Installer for OpenShift Container Platform](https://access.redhat.com/documentation/en-us/assisted_installer_for_openshift_container_platform/2022/html-single/assisted_installer_for_openshift_container_platform/index?extIdCarryOver=true&sc_cid=701f2000001Css5AAC) (메인)  
>3. **RedHat Blog** : [Using the OpenShift Assisted Installer Service to Deploy an OpenShift Cluster on Bare Metal and vSphere](https://cloud.redhat.com/blog/using-the-openshift-assisted-installer-service-to-deploy-an-openshift-cluster-on-metal-and-vsphere) (참고1)  
>4. **GitHub** : [openshift/assisted-service](https://github.com/openshift/assisted-service) (참고2)  


## STEP

>**-문서를 보기 전에-**  
>
>0. 이 문서는 OpenShift 설치에 대한 자세한 내용은 거의 생략되었습니다. 그에 관한 내용은 [공식문서](https://docs.openshift.com/container-platform/4.13/installing/installing_bare_metal/preparing-to-install-on-bare-metal.html)나 [호롤리/Openshift4.7 Baremetal 설치 - Restricted Network](https://gruuuuu.github.io/ocp/ocp4.7-restricted/) 문서를 참고하시기 바랍니다.  
>1. 해당 문서는 Assisted Installer SaaS를 사용해 OpenShift 4.12를 설치하는 과정을 담았습니다.  
>2. SaaS를 사용하는 경우라면 Cluster가 반드시 Public에 연결된 상태여야 합니다.  
>3. 참고용 아키텍처:   
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/0.png)  
> 모든 노드는 private network에만 연결되어 있고 public으로 나갈때만 bastion을 gateway로 ip masquerade하게 했습니다.  
>물론 외부에서의 패킷도 bastion노드 위의 LB를 통해 각 노드로 보낼 수 있습니다.  
> 이런 구조 하에서도 정상적으로 설치가 된 것을 보면 Assisted Installer는 IP가 아닌 Domain기반으로 통신을 하는 것 같습니다.  
> **즉, 외부에서 Domain으로 각 노드에 연결될 수 있다면 Assisted Installer를 사용할 수 있습니다!**   


### 1. Cluster Configuration 작성

RedHat Hybrid Cloud Console로이동-> https://console.redhat.com/

OpenShift 선택    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/1.png)    

Create Cluster > Datacenter > Create Cluster   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/2.png)    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/3.png)    

기본적인 클러스터 정보들을 채워넣습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/4.png)    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/5.png)    

- 싱글노드면 SNO에 체크
- Pull Secret을 현재 포탈에 로그인한 사용자가 아닌 다른사람 것으로 사용하려면 `Edit pull secret`을 체크하고 변경
- **Include custom manifests**는 install시 manifest 수정할게 있다면 체크
- Host Network Configuration도 상황에 맞게 선택, 이 문서에서는 Static으로 진행  

Static IP로 진행하기를 선택했기 때문에 그에 대한 정보들을 기입해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/6.png)    

전역 설정을 마쳤으면, 각 노드에 대한 ip와 mac주소를 지정해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/7.png)    

그리고나서 OpenShift와 같이 설치할 Operator도 선택해줍니다. (클러스터 구성 후 manual로 진행할 수도 있습니다.)  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/8.png)    

### 2. OS 부팅
설정 입력이 끝나면 Discovery iso파일을 다운로드 받게 됩니다.  
RHCOS와 Assisted service와의 통신을 담당할 agent가 담긴 파일이고, 모든 호스트에 동일한 iso를 배포하게 됩니다.  

다운로드 받기 전에 host에 추가할 ssh key를 작성해주고,  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/9.png)   

다운로드 받아서,    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/10.png)     

다운로드 받은 iso로 vm을 부팅해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/11.png)     

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/12.png)     

부팅되면서 agent가 돌아가면서 Assisted Installer에 호스트가 떴음을 알리고, 호스트에 대한 inventory 정보를 송신합니다.  
그럼 Assisted Installer는 호스트의 정보를 확인하고 기존에 작성했던 네트워크 파라미터들을 보내주고 부팅을 마치게 됩니다.    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/13.png)     

정상적으로 부팅되면 Assisted Installer의 Host discovery에서 확인할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/14.png)     

부팅된 호스트들의 Role(Master/Worker)을 정해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/15.png)     
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/16.png)     
최소 클러스터 구성조건인 Master 3개 Worker3개 이상이 채워지면 next 버튼이 활성화됩니다.  

> 아래 경고는 ODF설치옵션을 활성화 했을 경우 확인할 수 있습니다.
>ODF에 사용할 노드들은 os설치 디스크 외의 디스크들은 모두 로컬 스토리지로 편입되니 미리 포맷하라는 내용입니다.  
>
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/17.png)     
>디스크가 여러개라면 어떤디스크를 ODF용으로 사용할건지도 정해줄 수 있습니다.  
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/18.png)     

### 3. OpenShift 설치
다음은 네트워크 파트입니다.  
bastion혹은 사용하고 있는 DNS, LB장비가 있다면 User-Managed Networking을 선택합니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/19.png)     

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/20.png)     


설치를 진행하기 전 리뷰페이지입니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/21.png)     

모든 설정이 제대로 들어갔다면 Install Cluster 버튼을 클릭해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/22.png)     
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/23.png)     

만약 status가 오랫동안 pending상태에 있다면 직접 서버에 들어가서 journal log를 보면서 트러블슈팅해줘야 합니다.  

>겪었던 에러들 :   
> 1. multipath관련 에러 : [Ubuntu 20.04 multipath configuration](https://askubuntu.com/questions/1242731/ubuntu-20-04-multipath-configuration)  
> 2. no Configuration file in /etc/cni/net.d/ : crio 서비스 restart

### 4. 설치완료!
좀 기다리면 클러스터 설치가 완료되고, web화면에서 결과를 확인할 수 있습니다.   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/24.png)     

Launch Openshift Console버튼을 누르면 콘솔로 리다이렉트됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/25.png)     

옵션으로 줬던 ODF설치도 정상적으로 된 것을 확인할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2023/2023-07-23-ocp-assisted-service/26.png)     


트러블슈팅한 시간을 생각해도 기존에 했던 방식보다 훨씬 쉽고 간편해진 것 같습니다.  
아직 여러번 테스트해보지 않아서 상세한 옵션이나 아직 겪어보지 못한 문제들은 추후에 업데이트 하겠습니다.  

끝!

----