---
title: "Openshift Authentication"
slug: ocp4-authentication
tags:
  - Kubernetes
  - Openshift
date: 2020-06-27T13:00:00+09:00
---

## Overview
이번 포스팅에서는 openshift 에서 유저를 추가해보고 권한을 부여하는 방법에 대해 기술하겠습니다.  

# Prerequisites
- Openshift v4이상 클러스터

# 1. Authentication
유저가 ocp 클러스터에 접근하려면 OAuth서버를 통해 인증을 받아야 합니다.  
API나 웹 콘솔을 통해 OAuth서버의 인증을 요청할 수 있고, OAuth토큰을 받게 됩니다.  
그리고 그 **토큰은 유저의 API Request에 포함되어 그 유저의 자격증명을 가능**하게 해줍니다.  
보통 한번 이 토큰을 받게되면 24시간동안 유지되고 그 이후에는 다시 토큰을 받아야 합니다.  

현재 내가 사용하고 있는 계정이 무엇인지는 `whoami` 명령어로 확인가능합니다.  
~~~sh
$ oc whoami 

kube:admin
~~~

그리고 현재 사용되고 있는 토큰은 아래와 같이 확인 가능합니다.    
~~~sh
$ oc --user=admin get oauthaccesstokens


NAME                                          USER NAME    CLIENT NAME                    CREATED                EXPIRES                         REDIRECT URI                                                                                SCOPES
j-o4QaTtLw7eNYstIxi7kAudBcN8VBaY0Q81JxMuCGQ   kube:admin   openshift-challenging-client   2020-02-24T05:02:54Z   2020-02-25 05:02:54 +0000 UTC   https://oauth-openshift.apps.cluster-7b67.sandbox1327.opentlc.com/oauth/token/implicit      user:full
~~~

> **주요 커맨드**  
>~~~
>oc whoami  //shows current user
>oc whoami --show-console  //shows cluster web console URL
>oc whoami --show-server  //shows cluster API URL
>oc whoami --show-token  //shows current OAuth token
>~~~

# 2. Local Password Authentication Configuration
Openshift에 유저를 추가하는 방식은 크게 두가지 방식이 있습니다.  
1. HTPasswd로 추가
2. LDAP로 추가

해당 문서에서는 HTPasswd로 추가하는 방법을 설명드리겠습니다.  

현재 유저가 system admin인지 확인합니다.
~~~sh
$ oc whoami

system:admin
~~~

필요한 패키지 설치 :  
~~~sh
$ yum install httpd-tools
~~~

이제 생성할 유저의 정보가 담긴 파일을 생성하고 유저를 추가해줍니다.  
~~~sh
# 만들 유저의 정보가 담긴 파일 생성
$ touch htpasswd

# 유저 정보
# htpasswd -Bb htpasswd {username} '{password}'
$ htpasswd -Bb htpasswd a 'abc123'
$ htpasswd -Bb htpasswd b 'abc123'
$ htpasswd -Bb htpasswd c 'abc123'
~~~

파일을 열어보면 각 유저의 인증 정보가 담겨있는 것을 확인하실 수 있습니다.  
~~~sh
$ cat htpasswd

a:$2y$05$r12U.EbPMrQ7mH5Z6SFJhuTtKZSOX.vCxxr0hw1TKpWGCNGCQVq1G
b:$2y$05$HVk3tFvVDXC4AND0KaSuMeGrdrhHh1Es9Kx5TrwDTmIY5tSMIurS6
c:$2y$05$ZOz/Wljqpic2bF9coenqUeqkAiGtAyDjk2Vmy7fer9Y.kdOkrLkT2
~~~

생성한 시크릿을 openshift-config에 추가시켜줍니다.  
~~~sh
$ oc --user=admin create secret generic htpasswd \
    --from-file=htpasswd -n openshift-config

secret/htpasswd created
~~~
![image](https://user-images.githubusercontent.com/15958325/85921059-1722c480-b8b4-11ea-97ac-2c29a8cabe7e.png)  

클러스터에 적용 :    
~~~yaml
# oauth-config.yaml
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
  - name: Local Password
    mappingMethod: claim
    type: HTPasswd
    htpasswd:
      fileData:
        name: htpasswd
~~~

~~~sh
$ oc replace -f oauth-config.yaml

oauth.config.openshift.io/cluster replaced
~~~

제대로 적용되었는지 확인해보겠습니다.  
웹 GUI로 이동해서 `kubeadmin`말고 `Local Password`항목을 선택합니다.  
~~~sh
$ oc whoami --show-console
~~~
![image](https://user-images.githubusercontent.com/15958325/85921098-78e32e80-b8b4-11ea-8ba5-9a6477e5c5c5.png)  

만들었던 유저로 로그인!  
![image](https://user-images.githubusercontent.com/15958325/85921100-7c76b580-b8b4-11ea-86e6-3f807940c815.png)

성공!

# 3. RBAC (Role Based Access Control)
Openshift의 프로젝트(namespace)는 여러개의 application을 가질 수 있으며, 프로젝트 단위로 사용자가 할당되게 됩니다.  
프로젝트를 업무단위로 볼 수도 있으며, 사용자 그룹으로도 볼 수 있습니다. 이는 어떻게 서비스 아키텍처를 설계하느냐에 다라 다릅니다.  

![image](https://user-images.githubusercontent.com/15958325/85921467-7df5ad00-b8b7-11ea-9b2e-30b66bdeff0c.png)  

위 그림은 두명의 사용자가 서로 다른 Role을 가진 상황입니다.  

첫번째 사용자는 ProjectD에 대한 `self-provisioner`역할을 지녔기 때문에 ProjectD에 대한 관리자 역할만 할 수 있습니다. 그 외 다른 프로젝트나 클러스터 리소스에 대한 관리는 불가능합니다.  
두번째 사용자는 `cluster-admin`권한을 가진 사용자 입니다. 클러스터에 대한 모든 권한을 가지기 때문에 모든 프로젝트, 리소스들을 관리할 수 있습니다.  

이렇듯 사용자에 역할을 분담하여 리소스에 대한 관리 권한을 부여하는 방식을 RBAC(Role Based Access Control)이라고 합니다. Openshift에서는 RBAC방식을 통해 권한 관리를 하고 있습니다.  

다시 정리하면, 사용자와 역할(Role)을 **별개로 선언**하여 그 두가지를 **Binding**하여 사용자에게 **권한을 부여**하는 방식입니다.  

>**Background++**  
> - Rules : 객체의 집합에 허용되는 동사의 집합 (ex, user는 pod을 **create**할 수 있음)  
> - Roles : Rule들의 집합  
> - Bindings : 유저/그룹과 role을 연결  


![image](https://user-images.githubusercontent.com/15958325/85922711-6969e280-b8c0-11ea-9dc2-b946762455d1.png)  

Openshift에서 권한관리는 크게 두가지로 나뉩니다.  
- **Cluster RBAC** : **클러스터 전체**에 대한 권한 관리
  - ClusterRole : 클러스터 전체에 존재
  - ClusterRoleBinding : ClusterRole만 참조가능
- **Local RBAC** : 해당 **프로젝트(namespace)에만 적용**되는 권한 관리
  - LocalRole : 단일프로젝트에만 존재
  - LocalRoleBinding: ClusterRole과 LocalRole 모두 참조 가능

그리고 사용할 수 있는 Role의 Default종류는 다음과 같습니다.  

|Role|Description|
|---|---|
|admin|클러스터 내 Resource(ResourceQuotas, LimitRange, custom resource type)을 제외한 모든 리소스를 관리가능|
|basic-user|project와 user에 대한 기본적인 정보만 얻을 수 있음|
|**cluster-admin**|모든 리소스 타입 관리 가능|
|edit|프로젝트 수정가능, 하지만 role관련 기능은 보지도 수정도 불가(oc exec, oc rsh도 불가)|
|self-provisioner|유저의 default role, 프로젝트를 생성할 수 있으며 생성한 프로젝트의 admin이 됨|
|sudoer|oc --as=system:admin을 통해 임시 root권한을 얻은 사용자|
|system:image-puller|프로젝트에서 이미지 pull 가능|
|system:image-pusher|프로젝트에서 이미지 push 가능|
|view|프로젝트 보기만 가능|

>추가로 Openshift의 Default Group은 다음과 같습니다.  
>
>|Group|Description|
>|--|--|
>|system:authenticated|인증된 유저|
>|system:authenticated:oauth|OAuth를 통해 인증된 유저|
>|system:cluster-admins|ocp처음 설치할때 built-in된 유저(kubeadmin, system:admin)|
>|system:serviceaccounts|ocp클러스터 내 모든 서비스어카운트|
>|system:serviceaccounts:NAMESPACE|특정 프로젝트(namespace)의 서비스어카운트|
>|system:unathenticated|Anonymous,인증되지 않은 request|


## 3.1 유저 그룹 생성 & 관리자권한 부여
그럼 지금부터는 2챕터에서 생성했던 유저들을 그룹으로 관리하고, 일부 유저에게는 클러스터 관리자 권한을 부여해보도록 하겠습니다.  

>**background++**  
>클러스터를 맨 처음 설치할때 클러스터 관리자로 kubeadmin이라는 아이디가 부여됩니다.  
>테스트 환경에서는 그대로 사용해도 문제되지 않지만 되도록이면 LDAP든 HTPasswd방법을 사용해서 유저를 직접생성, 관리자권한을 부여해주는것을 권장합니다.  

시스템 관리자로 로그인  
~~~sh
$ oc login -u system:admin
~~~

`local-admin`그룹과 `projectA`그룹을 생성해서, `local-admin` 그룹에게만 클러스터 관리자 권한을 부여해주겠습니다.  

두 그룹 생성(`new`) :  
~~~sh
$ oc adm groups new local-admin

group.user.openshift.io/local-admin created


$ oc adm groups new projectA

group.user.openshift.io/projectA created
~~~

각 그룹에 유저 추가(`add-users`) :   
~~~sh
$ oc adm groups add-users local-admin a

group.user.openshift.io/local-admin added: "a"


$ oc adm groups add-users projectA b

group.user.openshift.io/projectA added: "b"
~~~

생성한 그룹을 확인합니다.  
~~~sh
$ oc get groups
~~~
![image](https://user-images.githubusercontent.com/15958325/85923176-e77bb880-b8c3-11ea-9219-46ed1838e0a7.png)  
현재 `local-admin`그룹에는 유저 "`a`"가, `projectA`그룹에는 유저 "`b`"가 들어가 있습니다.  

그럼 `local-admin`그룹에 클러스터 관리자 권한을 부여해주겠습니다.(`add-cluster-role-to-gruop`)  
~~~sh
$ oc adm policy add-cluster-role-to-group cluster-admin local-admin-xx

clusterrole.rbac.authorization.k8s.io/cluster-admin added: "local-admin"
~~~

부여해주었으니 이제 제대로 권한을 받았는지 확인해보겠습니다.  

`local-admin`그룹의 a유저로 로그인 :  
~~~sh
$ oc login -u a -p abc123
~~~
![image](https://user-images.githubusercontent.com/15958325/85923229-5ce78900-b8c4-11ea-965b-d07d1e4f87ce.png)  
access할 수 있는 프로젝트의 개수가 늘어난 것을 보니 제대로 부여받은 것 같습니다.  

모든 verb와 resource에 권한이 있는지도 체크해보겠습니다.  
~~~sh
# auth can-i {verb} {resource}
$ oc auth can-i foo bar

Warning: the server doesn't have a resource type 'bar'
yes
~~~

## 3.2 일반 유저의 프로젝트 생성 권한 제한
위에서 총 두가지 그룹을 만들었습니다. 클러스터 관리자 역할 그룹인 `local-admin`, 그리고 일반 유저 그룹인 `projectA`그룹입니다.  

이 projectA는 현재 아무런 처리를 하지 않았으므로, default권한인 `self-provisioner`권한을 지니고 있을 것입니다.  
> `self-provisioner` : 가장 default권한이며 프로젝트 생성권한을 가짐. 

이번 챕터에서는 이 일반유저의 프로젝트 생성권한을 제한해보도록 하겠습니다.  

먼저 아무 처리도 하지 않은 `ProjectA`그룹의 유저 "`b`"가 정상적으로 프로젝트를 생성할 수 있는지 확인해보겠습니다.  

~~~sh
# 유저 b로 로그인
$ oc login -u b -p abc123

# b가 프로젝트를 생성 할 수 있는지 확인
$ oc new-project test
~~~
![image](https://user-images.githubusercontent.com/15958325/85923330-06c71580-b8c5-11ea-8788-0141a2ae5a10.png)  

생성가능합니다! 정리를 위해 만든 프로젝트는 삭제해주도록 하겠습니다.  
~~~sh
$ oc delete project test
~~~

그룹 `ProjectA`의 권한을 수정하기위해 클러스터 관리자로 로그인합니다.(admin권한이 필요하므로)  
~~~sh
$ oc login -u a -p abc123
~~~

먼저 `self-provisioner` **clusterrole**을 살펴보면 프로젝트 생성권한이 있다는 것을 확인할 수 있습니다.  
~~~sh
$ oc describe clusterrole self-provisioner
~~~
![image](https://user-images.githubusercontent.com/15958325/85923371-5ad1fa00-b8c5-11ea-89df-854f36cbfd8c.png)  

그리고 이 clusterrole이 연결된 대상을 확인해보면 :   
~~~sh
$ oc get clusterrolebinding self-provisioners -o yaml
~~~
![image](https://user-images.githubusercontent.com/15958325/85923389-7ccb7c80-b8c5-11ea-8c04-4e9d7addad33.png)  
`system:authenticated:oauth`그룹(일반유저)와 연결이 되어있다는 것을 확인할 수 있습니다.  

이제 autoupdate기능을 잠시 false로 바꿔두겠습니다. 이 기능은 role이나 rolebinding이 실수로 변경되었을 때 기본값으로 복구시키는 역할을 해줍니다.  
~~~sh
$ oc annotate clusterrolebinding self-provisioners --overwrite 'rbac.authorization.kubernetes.io/autoupdate=false'

clusterrolebinding.rbac.authorization.k8s.io/self-provisioners annotated
~~~

clusterrolebinding을 확인해보면 autoupdate가 false로 바뀐 것을 확인 가능합니다.  
~~~sh
$ oc get clusterrolebinding self-provisioners -o yaml
~~~
![image](https://user-images.githubusercontent.com/15958325/85923650-d3d25100-b8c7-11ea-91f8-94fcaeec304e.png)  

autoupdate를 꺼준다음, `self-provisioners`에서 일반유저(`system:authenticated:oauth`)그룹을 제외해주겠습니다.  
~~~sh
$ oc adm policy remove-cluster-role-from-group self-provisioner system:authenticated:oauth

clusterrole.rbac.authorization.k8s.io/self-provisioner removed: "system:authenticated:oauth"
~~~
![image](https://user-images.githubusercontent.com/15958325/85923790-1183a980-b8c9-11ea-86bf-5c0ea033e50a.png)  

확인해보면 일반유저그룹이 `self-provisioners`에서 사라진 것을 확인할 수 있습니다.  
이는 다시 말하면, 일반유저그룹이 `self-provisioner`권한을 사용하지 못한다는 의미입니다.  
즉 일반유저가 프로젝트의 생성권한을 잃어버린 것이죠.  
~~~sh
# 유저b로 로그인
$ oc login -u b -p abc123 


# 프로젝트생성 -> 안됨
$ oc new-project test-xx

Error from server (Forbidden): You may not request a new project via this API.
~~~

그럼 이번엔 특정 그룹(`ProjectA`)에만 `self-provisioner` 권한을 부여해보겠습니다.  

~~~sh
# cluster-admin계정으로 로그인
$ oc login -u a -p abc123 


# self-provisioner권한을 projectA에게만 부여
$ oc adm policy add-cluster-role-to-group self-provisioner projectA-xx

clusterrole.rbac.authorization.k8s.io/self-provisioner added: "projectA"
~~~

clusterrolebinding 리스트를 보면 새롭게 self-provisoner가 생성된 것을 확인가능합니다.  
~~~sh
$ oc get clusterrolebinding -A
~~~
![image](https://user-images.githubusercontent.com/15958325/85923891-b0a8a100-b8c9-11ea-9dfe-a17a3c557433.png)  

여기서 노란색으로 표시한 `self-provisioner`아래 `self-provisioners`가 뭔지 헷갈리실겁니다.  
self-provisioners는 클러스터가 처음 구성될 때 self-provisioner라는 clusterrole과 모든 일반유저(`system:authenticated:oauth`)를 연동하기 위한 clusterrolebinding입니다.  

자세히 보면 projectA그룹이 바인딩 된 것을 확인할 수 있습니다.  
~~~sh
$ oc get clusterrolebinding self-provisioner -o yaml
~~~
![image](https://user-images.githubusercontent.com/15958325/85923930-08dfa300-b8ca-11ea-91a9-2b5f2e06057b.png)  

다시 `ProjectA`그룹의 유저 "`b`"로 로그인해보고 프로젝트를 생성해보겠습니다.  
~~~sh
$ oc login -u b -p abc123

$ oc new-project test-b2
~~~
![image](https://user-images.githubusercontent.com/15958325/85923968-417f7c80-b8ca-11ea-832e-f6e0c04e7de1.png)  
잘 생성됩니다.  

시간순으로 정리하면, 
- self-provisioner role : 일반유저에게 부여되는 default role이며 프로젝트생성권한을 가짐
- self-provisioner**s**는 ocp클러스터가 처음 구성될 때 생긴 clusterrolebinding이며, 일반유저에게 self-provisioner권한을 부여해주는 역할
1. self-provisioenr**s**에서 일반유저를 삭제
2. 일반유저는 프로젝트를 생성할 수 없게 됨
3. self-provisioner라는 새로운 clusterrolebinding을 생성
4. 바인딩되는 그룹으로 projectA를 추가
5. 여전히 일반 유저는 프로젝트를 생성할 수 없지만, ProjectA그룹의 유저는 프로젝트를 생성할 수 있음

### Clean up
~~~sh
# 만든 프로젝트 삭제
$ oc delete project test-b2

project.project.openshift.io "test-b2" deleted
~~~

~~~sh
# autoupdate를 원래대로
$ oc login -u a


$ oc annotate clusterrolebinding self-provisioners --overwrite 'rbac.authorization.kubernetes.io/autoupdate=true'

clusterrolebinding.rbac.authorization.k8s.io/self-provisioners annotated
~~~

~~~sh
# apiserver를 삭제해서 재시작하게함
$ oc delete pod -n openshift-apiserver --all

pod "apiserver-hskpl" deleted
~~~

~~~sh
# clusterrolebinding 보면 없앴던 oauth가 돌아와 있음
$ oc get clusterrolebinding self-provisioners -o yaml

...
  kind: ClusterRole
  name: self-provisioner
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:authenticated:oauth
~~~

----