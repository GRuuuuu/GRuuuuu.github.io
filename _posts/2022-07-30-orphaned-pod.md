---
title: "[kubelet] orphaned pod ... found, but error not a directory occurred when trying to remove the volumes dir"
categories: 
  - ERROR
tags:
  - Kubernetes
  - Podman
  - Container
last_modified_at: 2022-07-30T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Environment
`OS : RedHat CoreOS 4.10`   
`Openshift : 4.10`  
`Kubernetes : v1.23.5`  

## ERROR

~~~
Jul 28 01:14:12 worker3.test.testtest.com hyperkube[2197]: E0728 01:14:12.868554    2197 kubelet_volumes.go:245] "There were many similar errors. Turn up verbosity to see them." err="orphaned pod \"de12fb00-45b4-49a4-98b5-ac87f5884532\" found, but error not a directory occurred when trying to remove the volumes dir" numErrs=1
~~~



### 원인
장비를 강제 리부팅(hard reboot)시켰을 시 나타나는 문제.  

노드가 내려갔다가 다시 올라오면서, 기존의 volume path를 지우지 못하고 disk에 그대로 남아있는 경우에 발생한다.  

### Solution
#### 1. 에러 로그의 pod id 복사

~~~
de12fb00-45b4-49a4-98b5-ac87f5884532
~~~

#### 2. pod volume path로 이동
~~~
cd /var/lib/kubelet/pods/de12fb00-45b4-49a4-98b5-ac87f5884532/volumes/kubernetes.io~csi/pvc-123dfdf8-0bae-4fd6-828d-5d5ef935b306/
~~~

`vol_data.json` 파일을 삭제. 

`vol_data.json` 안에는 해당 pod가 가지고있던 volume에 대한 정보가 존재한다.  
~~~
{
  "attachmentID": "csi-ae66f698baee8f1182608d3d572fdde66bbc29f49e88621752da5d675d8d303d",
  "driverName": "openshift-storage.rbd.csi.ceph.com",
  "nodeName": "worker1.test.testtest.com",
  "specVolID": "pvc-121a4d51-f258-4496-8cb3-39dcd87128fc",
  "volumeHandle": "0001-0011-openshift-storage-0000000000000001-cf6c2cb0-f37b-11ec-b44c-0a580a800218",
  "volumeLifecycleMode": "Persistent"
}
~~~

### 3. 확인
json파일을 삭제하고나면 pod자체 폴더가 지워진다.  
![image](https://user-images.githubusercontent.com/15958325/181877856-d7cafa73-2647-4cdf-9515-11b76ad1a35c.png)  

journal log도 살펴보면
~~~
Jul 28 01:14:14 worker3.test.testtest.com hyperkube[2197]: E0728 01:14:14.867716    2197 kubelet_volumes.go:245] "There were many similar errors. Turn up verbosity to see them." err="orphaned pod \"de12fb00-45b4-49a4-98b5-ac87f5884532\" found, but error not a directory occurred when trying to remove the volumes dir" numErrs=1
Jul 28 01:14:16 worker3.test.testtest.com hyperkube[2197]: I0728 01:14:16.868557    2197 kubelet_volumes.go:160] "Cleaned up orphaned pod volumes dir" podUID=de12fb00-45b4-49a4-98b5-ac87f5884532 path="/var/lib/kubelet/pods/de12fb00-45b4-49a4-98b5-ac87f5884532/volumes"
~~~

말끔하게 사라진 에러!  

----