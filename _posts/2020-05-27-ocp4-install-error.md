---
title: "Openshift4.3 Installation on Baremetal -Errors"
categories: 
  - OCP
tags:
  - Kubernetes
  - RHCOS
  - Virtualbox
  - Openshift
last_modified_at: 2020-05-27T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
지난포스팅에서는 `ocp4.3`버전을 virtualbox에 **baremetal install**방식으로 설치를 진행해봤습니다.  
-> [Openshift4.3 Installation on Baremetal](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/)  
설치 과정이 꽤나 복잡한 만큼 여러 에러도 만났었는데, 기억나는 것들만 기록해두겠습니다.  

# Errors
## 1. GET_https://api-int.aio.ddd.com:22623/config/master : attempt #nn
![image](https://user-images.githubusercontent.com/15958325/82968352-17574800-a008-11ea-96b6-2f9da4fd910d.png)  
부트스트랩은 정상적으로 올라온상태에서 마스터노드를 부트시켰을때 생기는 에러.  
master config파일을 제대로 가져오지 못하는 상태.  

**해결 :**  
로드밸런서를 설정해주면 해결  
참고 : [이전포스팅](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/#)

## 2. http: server gave HTTP response to HTTPS client

![image](https://user-images.githubusercontent.com/15958325/82969539-dc0a4880-a00a-11ea-94c7-ded71033e8ea.png)  

1번에러는 넘겼는데 다시 GET에러가 남  

**해결 :**  
로드밸런서는 있지만 tcp용로드밸런서가아니라 http용 로드밸런서를 사용했을 경우에 발생  
tcp용으로 수정해주면 해결  

## 3. GET_https://api-int.tests.ddd.com:22623/config/worker

![image](https://user-images.githubusercontent.com/15958325/82970319-4d49fb80-a00b-11ea-8833-e15bd21ca782.png)  

부트스트랩&마스터까지 올리고나서 워커를 올리려는데 발생한 에러.  

**해결:**  
원인이 두가지정도인데  
첫번째는 워커노드를 부팅하는데 사용한 ignition파일이 만료되었을 경우,  
두번째는 마스터노드가 정상적으로 부팅되지 않았을 경우이다.  
두번째 경우일때는 마스터노드의 kubelet 로그를 살펴봐야한다.  

## 4. dhcp for interface env32 failed

~~~
[   65.570614] dracut-initqueue[949]: Warning: dhcp for interface env32 failed
[   65.599744] dracut-initqueue[949]: RTNETLINK answers: File exists
~~~
맨 처음 RHCOS를 부팅시킬때 발생하는 에러이다.   
dhcp서버가 제대로 작동하지 않아서 생기는 문제.  

**해결:**  
dhcp서버를 제대로 작동시키던지,  
ip를 스태틱하게 지정해주면 해결된다.   
ex)  
~~~
coreos.inst.install_dev=sda 
coreos.inst.image_url=http://192.168.56.144:8080/rhcos-4.3.18-ppc64le-metal.ppc64le.raw.gz
coreos.inst.ignition_url=http://192.168.56.144:8080/bootstrap.ign 
ip=192.168.56.200::192.168.56.144:255.255.255.0:bootstrap.tests.hololy.local:enp0s3:none nameserver=192.168.56.144
~~~

## 5. dracut-initqueue[941]: Warning: dracut-initqueue timeout

![image](https://user-images.githubusercontent.com/15958325/82970801-217b4580-a00c-11ea-8b8f-a25d8ccd48b2.png)  
부트스트랩 마스터 워커 모두 발생가능하다.  
맨 처음 RHCOS를 부팅시킬때 발생하는 에러이다.  

**해결:**  
원인은 인스톨 파라미터로 집어넣었던 네트워크 인터페이스 이름이 틀렸기 때문이다.  
이 경우, `dracut`모드로 들어가서 `ip a`로 정확한 이름을 확인한다.  

> dracut모드는 timeout에러가 발생한 이후 쫌 오래 기다리면 emergency shell 열겠냐고 알림이 뜬다.  

![image](https://user-images.githubusercontent.com/15958325/82971379-79667c00-a00d-11ea-8b7f-e5872dfd87ab.png)  

## 6. no matches for kind "MachineConfig" in version "machineconfiguration.openshift.io/v1"  

![image](https://user-images.githubusercontent.com/15958325/82971469-b03c9200-a00d-11ea-800f-4c9b4dd2e3c3.png)  
부트스트랩의 bootkube로그를 보다보면 마스터에 etcd가 다 뜨고 난후 MachineConfig를 찾지 못한다는 에러가 계속계ㅔ에에에속 뜬다.  
에러처럼 보이지만 사실 에러가 아니고 마스터가 다 올라올때까지 기다리는 과정이다.  
한 3000번대까지는 기다려보고 계속 안된다고하면 마스터에 문제가 생긴것이다.  
마스터의 kubelet로그를 확인하고 문제를 해결해봐야한다.  

근데 사실 마스터 kubelet로그도 가독성이 좋지못해서 뭐가 문젠지 한눈에 보이지 않는다.  
그래도 몇가지 확인해 볼 점은 다음과 같다.   
1. 네트워크 연결이 정상적인지
2. hostname이 설정한대로 적용되었는지
3. ignition파일을 만든지 24시간이 지나지 않았는지
4. `quay.io`가 정상적으로 동작하는지

> 4번은 일어날 확률이 매우매우 적지만 0은 아니기 때문에 확인해볼 가치가 있다.  
> kubelet로그에서 이미지 pull을 제대로 못하고있다면 
> [quay.io status](https://status.quay.io/)를 확인해보고 정상이아니면 마음놓고 쉬러갑시다.  

## 7. hostname이 localhost로 나오거나 설정한대로 나오지 않는 경우

마스터노드를 비롯한 클러스터 노드들은 hostname으로 자신을 구별하기 때문에 반드시 hostname이 세팅되어있어야 함.  

dns설정 또는 dnsmasq설정을 전부 해줬는데도 불구하고 설정한대로 나오지 않는 경우는,  
1. 라우터문제
2. bastion의 /etc/hosts파일  
두가지정도이다.  

1번은 vm에서 다수의 네트워크인터페이스를 사용하는 경우이다.  
이러한 경우에는 아직 명확한 해결책을 발견하지 못했다.  
그래서 일단 현재는 단일 네트워크인터페이스를 사용하도록 설정하여 문제를 회피했는데,  
다수의 네트워크인터페이스를 반드시 사용해야하는 경우는 추후에 해결책을 찾아서 수정예정

2번은 bastion의 /etc/hosts파일을 초기상태로 되돌리면 해결  

## 8. Domain 변경시 제대로 적용안되는 경우
여러번 설치 재설치 하는 도중에 도메인을 갑자기 변경하고 싶은 마음이 들수도 있습니다. 
제가 그랬거든요.  
여튼 도메인을 변경했는데 제대로 설정이 적용되지 않는경우에는 install용 폴더를 의심해야함  

설치를 진행하면서 생기는 캐시들이 `.openshift_install_state.json`이 파일에 저장되기 때문에 변경사항들이 적용되지 않을 수 있음

설정을 바꿔서 재설치할때에는 설치용폴더를 깨끗하게 삭제한 후에 설치를 진행하면 해결

## 9. Failed to start sdn : node SDN setup failed

![image](https://user-images.githubusercontent.com/15958325/82973272-f1cf3c00-a011-11ea-8b61-bdfd6d0e0af3.png)  

SDN이 뜨지 않는 에러. ovs가 뜨지않아서 생기는 에러이다.  

ovs의 로그를 보면 :   
![image](https://user-images.githubusercontent.com/15958325/82973373-20e5ad80-a012-11ea-8bd5-c89af7a5e00a.png)  

3 Insufficient cpu라는 에러가 뜬다.  

해결:  
vm의 cpu개수를 최소요구사항대로 맞춰준다.  

## 10. Could not update oauthclient "console" (292 of 498): the server is down or not responding  

~~~sh
$ ./openshift-install wait-for install-complete --log-level=debug --dir=dir/
DEBUG OpenShift Installer 4.3.21
DEBUG Built from commit 7bc8168fbba1c831ac1b25c858f4f56cd7468801
DEBUG Fetching Install Config...
DEBUG Loading Install Config...
DEBUG   Loading SSH Key...
DEBUG   Loading Base Domain...
DEBUG     Loading Platform...
DEBUG   Loading Cluster Name...
DEBUG     Loading Base Domain...
DEBUG     Loading Platform...
DEBUG   Loading Pull Secret...
DEBUG   Loading Platform...
DEBUG Using Install Config loaded from state file
DEBUG Reusing previously-fetched Install Config
INFO Waiting up to 30m0s for the cluster at https://api.s.ibmocp4.lab:6443 to initialize...
DEBUG Still waiting for the cluster to initialize: Multiple errors are preventing progress:
* Could not update oauthclient "console" (292 of 498): the server is down or not responding
* Could not update role "openshift-console-operator/prometheus-k8s" (449 of 498): resource may have been deleted
~~~

원인 : 잘모르겠음  

**해결:**  
모든 마스터에 다음 옵션 적용 후 리부트  
~~~sh
$ sudo vi /etc/sysctl.conf
net.ipv4.ip_no_pmtu_disc = 1

$ sudo sysctl -p
$ sudo reboot
~~~

## 11. Cluster operator kube-apiserver Degraded is True with NodeInstaller_InstallerPodFailed
~~~sh
$ ./openshift-install wait-for install-complete --log-level=debug --dir=dir/
DEBUG OpenShift Installer 4.3.21
DEBUG Built from commit 7bc8168fbba1c831ac1b25c858f4f56cd7468801
DEBUG Fetching Install Config...
DEBUG Loading Install Config...
DEBUG   Loading SSH Key...
DEBUG   Loading Base Domain...
DEBUG     Loading Platform...
DEBUG   Loading Cluster Name...
DEBUG     Loading Base Domain...
DEBUG     Loading Platform...
DEBUG   Loading Pull Secret...
DEBUG   Loading Platform...
DEBUG Using Install Config loaded from state file
DEBUG Reusing previously-fetched Install Config
INFO Waiting up to 30m0s for the cluster at https://api.s.ibmocp4.lab:6443 to initialize...
DEBUG Still waiting for the cluster to initialize: Cluster operator authentication is still updating
DEBUG Still waiting for the cluster to initialize: Cluster operator authentication is still updating
DEBUG Still waiting for the cluster to initialize: Cluster operator authentication is still updating
DEBUG Still waiting for the cluster to initialize: Cluster operator authentication is still updating
DEBUG Still waiting for the cluster to initialize: Cluster operator authentication is still updating
INFO Cluster operator authentication Progressing is True with ProgressingWellKnownNotReady: Progressing: got '404 Not Found' status while trying to GET the OAuth well-known https://10.10.14.119:6443/.well-known/oauth-authorization-server endpoint data
INFO Cluster operator authentication Available is False with Available:
INFO Cluster operator insights Disabled is False with :
ERROR Cluster operator kube-apiserver Degraded is True with NodeInstaller_InstallerPodFailed: NodeInstallerDegraded: 1 nodes are failing on revision 5:
NodeInstallerDegraded: no detailed termination message, see `oc get -n "openshift-kube-apiserver" pods/"installer-5-master2.s.ibmocp4.lab" -oyaml`
INFO Cluster operator kube-apiserver Progressing is True with : Progressing: 2 nodes are at revision 3; 1 nodes are at revision 5
FATAL failed to initialize the cluster: Cluster operator authentication is still updating
~~~

마스터에서 installer가 제대로 설치를 마치지 못한 경우.  
원인이 여러개 있을 수 있지만 제 경우는 OOM(out of memory)였습니다.  

마스터가 워커의 롤까지 하게될 경우에 발생할 수 있는데,  
이 경우는 마스터의 리소스를 더 늘려주던가,   
`manifests/cluster-scheduler-02-config.yml` 파일의 `mastersSchedulable`를 False로 바꿔서 마스터와 워커의 롤을 구분지어주면 해결.  

## 12. No container image registry has been configured with the server. Automatic builds and deployments may not function.

이번 에러는 설치 도중이 아니라 설치 후에 나타나는 에러입니다.  
application을 빌드할 때 생기는 에러입니다.  

~~~sh
# 간단한 app을 S2I하는 명령어
$ oc new-app php~https://github.com/sclorg/cakephp-ex \
      --name=cakephp03 -n project-00

...
--> Creating resources ...
    imagestream.image.openshift.io "cakephp03" created
    buildconfig.build.openshift.io "cakephp03" created
    deploymentconfig.apps.openshift.io "cakephp03" created
    service "cakephp03" created
--> Success
    WARNING: No container image registry has been configured with the server. Automatic builds and deployments may not function.
    Build scheduled, use 'oc logs -f bc/cakephp03' to track its progress.
    Application is not exposed. You can expose services to the outside world by executing one or more of the commands below:
     'oc expose svc/cakephp03'
    Run 'oc status' to view your app.
~~~

빌드할 시, 아래와 같은 경고문구가 뜨며,  
~~~
WARNING: No container image registry has been configured with the server. Automatic builds and deployments may not function.
~~~

빌드로그를 살펴보면:  
~~~
$ oc describe build cakephp03-1

...
Error starting build: an image stream cannot be used as build output because the integrated container image registry is not configured
~~~

image registry가 구성되지 않았다는 에러가 뜹니다.  

또 다른 에러로는 GUI화면에서 app을 직접 생성할 경우 발생하는 에러가 있습니다.  
GUI에서 app을 생성하고나서 cli화면으로 pod을 살펴보면 ErrImagePull에러가 뜨며,  
~~~
$ oc get pod
NAME                      READY   STATUS         RESTARTS   AGE
php-00-686b684fb7-m4ltv   0/1     ErrImagePull   0          11s
~~~

describe로 살펴보면
~~~
Events:
  Type     Reason     Age                 From                                  Message
  ----     ------     ----                ----                                  -------
  Normal   Scheduled  <unknown>           default-scheduler                     Successfully assigned project-00/php-00-686b684fb7-m4ltv to worker01.tests.hololy.local
  Normal   Pulling    16s (x4 over 106s)  kubelet, worker01.tests.hololy.local  Pulling image "php-00:latest"
  Warning  Failed     16s (x4 over 105s)  kubelet, worker01.tests.hololy.local  Failed to pull image "php-00:latest": rpc error: code = Unknown desc = Error reading manifest latest in docker.io/library/php-00: errors:
denied: requested access to the resource is denied
unauthorized: authentication required
  Warning  Failed   16s (x4 over 105s)  kubelet, worker01.tests.hololy.local  Error: ErrImagePull
  Normal   BackOff  3s (x6 over 105s)   kubelet, worker01.tests.hololy.local  Back-off pulling image "php-00:latest"
  Warning  Failed   3s (x6 over 105s)   kubelet, worker01.tests.hololy.local  Error: ImagePullBackOff
~~~
unauthorized 에러가 발생합니다.  

이 모든 에러의 원인은 바로 베어메탈의 image-registry를 설정하지 않았을 경우에 발생합니다.  
제대로 설정해주면 아주 잘 돌아갑니다.  
설치 문서에 적혀있긴한데, 저같이 제대로 안읽고 넘어간 사람들을 위해 기록해둡니다.... 

-> [Openshift4.3 Installation on Baremetal](https://gruuuuu.github.io/ocp/ocp4-install-baremetal/#)문서의 Configuring the registry for bare metal(6/12수정)를 참조해주세요.  


# 마치며
제가 겪었던 일부 에러들과 그 해결책들을 적어봤습니다.  

제가 ocp4를 UPI로 설치하면서 느낀점은 진짜 에러로그를 봐서는 이게 뭐가문젠지 한번에 감이 안잡힌다는겁니다.  
`kubelet`이나 `bootkube`로그를 보시면 아시겠지만 에러를 비롯한 모든 로그들이 순식간에 휙휙지나가버리고 설치가 완료될때까지 같은 로그가 반복적으로 로깅되는것을 확인할 수 있습니다.  
그걸 보고있으면 멍해지는 정신은 덤...ㅎㅎ   

덤으로 ocp4가 나온지 얼마안되서 그런지는 몰라도 국내자료가 거의 없는건 물론이고 해외에도 자료가 거의 없습니다. 로깅된 에러들도 에러만 봐서는 명확한 원인을 알 수 없는게 대부분이라 질문해도 정확한 답을 얻기가 힘듭니다.  
이번 포스팅이 후에 설치하는 분들에게 도움이 되었으면 좋겠습니다.

개인적으로는 역대급으로 어려웠던 설치였던것같습니다...근데 그만큼 얻는것도 많았어서 뿌듯하게 마무리 지을 수 있었던것 같네요.  

다음번엔 ocp4 operation 포스팅으로 돌아오겠습니다.

끝!

----