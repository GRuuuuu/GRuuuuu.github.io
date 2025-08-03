---
title: "[Resolved] No valid client certificate is found but the server is not responsive"
slug: ocp-cert-issue
tags:
  - Openshift
  - Certificate
  - Container
date: 2024-10-12T13:00:00+09:00
---


## Environment
OS : `RedHat CoreOS 4.16`   
Openshift : `v4.16`     

## ERROR

Cluster가 무언가의 이유로 1일 이상 down되었을 시, 각 노드의 certificate가 만료가 되고 재발급을 위해 마스터노드에 csr승인요청을 보내는데 이 승인요청을 제대로 처리해주지 못한다면 아래와 같은 에러들을 kubectl journal로그에서 확인할 수 있습니다.  

### No valid client certificate is found but the server is not responsive. A restart may be necessary to retrieve new initial credentials.

이걸 해결해주려면 `oc login`을 통해서 csr들을 승인해주어야 하는데...  
server에 연결할 수 없다며 에러를 뱉어내는 경우가 있습니다.  
~~~
Unable to connect to the server: EOF
~~~

이럴 때는 마스터노드에 직접 접속하여 커맨드를 날리는 방법으로 해결하시면 됩니다.  

마스터노드 아무거나 접속:  
~~~
# ssh core@master01
# sudo su 
~~~

`KUBECONFIG` 설정:
~~~
# export KUBECONFIG=/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/lb-int.kubeconfig
~~~

그럼 마스터노드에서 oc 커맨드를 사용할 수 있게됩니다.  
~~~
[root@master0 core]# oc get csr
NAME        AGE     SIGNERNAME                                    REQUESTOR                                                                   REQUESTEDDURATION   CONDITION
csr-29pxq   13m     kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   <none>              Pending
csr-2tpbj   28m     kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   <none>              Pending
csr-2vn7c   142m    kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   <none>              Pending
csr-2xd78   5m59s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   <none>              Pending
...
~~~
확인해보니 난리가 났습니다... csr 몇십개가 떠있네요  


Pending상태인 녀석들을 전부 승인해주고나면 문제 해결입니다.   
~~~
# oc get csr -o name | xargs oc adm certificate approve
~~~

----