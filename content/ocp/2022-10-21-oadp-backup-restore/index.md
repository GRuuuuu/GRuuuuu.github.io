---
title: "OpenShift API for Data Protection(OADP)를 사용한 Backup/Restore"
slug: oadp-backup-restore
tags:
  - Kubernetes
  - Openshift
  - Backup
  - Restore
date: 2022-10-21T13:00:00+09:00
---

## Overview
이번 문서에서는 **OpenShift API for Data Protection**를 사용하여 Openshift 클러스터의 Resource와 PV를 백업하는 방법과 복구하는 방법에 대해서 기술하겠습니다.  

## OpenShift API for Data Protection (OADP)

**OpenShift API for Data Protection**은 (이하 OADP) Kubernetes의 모든 리소스들과 내부 이미지들을 namespace단위로 백업&복구가 가능한 오퍼레이터입니다.  
오픈소스인 [Velero](https://velero.io/docs/v1.9/) (Openshift 4.11기준 v1.9)를 기반으로 동작하고, PV 백업&복구는 snapshot기능 혹은 [Restic](https://restic.readthedocs.io/en/latest/)을 사용하여 동작합니다.  

- 클러스터의 모든 리소스 백업가능
- 필터링을 통해 원하는 리소스만 백업가능
- 백업파일들은 오브젝트스토리지에 저장
- PV 백업&복구
    - volume snapshot을 지원하지 않는 Cloud Provider를 사용할 경우, 혹은 NFS를 pv로 사용하고 있을 경우엔 `Restic`으로 백업

### 사용 가능한 OADP plugin
>참고 -> [OADP features and plug-ins](https://docs.openshift.com/container-platform/4.11/backup_and_restore/application_backup_and_restore/oadp-features-plugins.html)  

기본적으로는 `Velero`의 plugin을 제공하고, 커스텀 [plugin](https://velero.io/docs/v1.9/custom-plugins/)도 만들어서 사용할 수 있습니다.  

추가로는 Openshift Virtualization 백업에 대한 plugin도 지원합니다.  

OADP plug-in|Function|Storage location|
---|---|---
`aws`|Kubernetes object/volume snapshot|AWS S3/AWS EBS
`azure`|Kubernetes object/volume snapshot|Azure Blob storage/Azure Managed Disks
`gcp`|Kubernetes object/volume snapshot|Google Cloud Storage/Google Compute Engine Disks
`openshift`|Openshift Container Platform의 리소스들(필수 plugin)|Object Store
`kubevirt`|Openshift Virtualization의 리소스들(ex. vm disk)|Object Store
`csi`|CSI volume snapshot|CSI snapshot을 지원하는 Cloud storage

## Backup & Restore

### 1. OADP operator 설치
Operator Hub에서 OADP operator를 설치합니다.
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/2.png)   


### 2. S3 storage secret 생성
리소스 백업과 PV snapshot 저장을 위한 S3 스토리지의 Secret을 생성해야 합니다.  

~~~
$ cat << EOF > ./credentials-velero
[default]
aws_access_key_id=<ACCESS_KEY>
aws_secret_access_key=<SECRET_KEY>
EOF
~~~

secret 생성
~~~
$ oc create secret generic cloud-credentials -n openshift-adp --from-file cloud=credentials-velero
~~~

이름은 반드시 `cloud-credentials`라는 이름으로 생성하여야 하며,   

만약 리소스백업과 snapshot의 위치를 다르게 설정할거면 secret을 두개 만들어야 합니다.  
snapshot은 `cloud-credentials`라는 이름의 secret을 참조하게 되고  
리소스백업의 경우 커스텀 이름으로 참조 가능합니다.  

뒤에서 `DataProtectionApplication`(DPA)를 만들 때 `backupLocations.velero.credential`에 명시해주면 됩니다.  
~~~yaml
apiVersion: oadp.openshift.io/v1alpha1
kind: DataProtectionApplication
metadata:
  name: <dpa_sample>
  namespace: openshift-adp
spec:
...
  backupLocations:
    - velero:
        provider: <provider>
        default: true
        credential:
          key: cloud
          name: <custom_secret> 
        objectStorage:
          bucket: <bucket_name>
          prefix: <prefix>
~~~


### 3. DataProtectionApplication 배포하기
>⚠ 이 문서에서는 `Velero`를 이용한 namespace별 백업, 그리고 CSI snapshot기능이 아닌 `Restic`으로 백업하는 것을 다루고 있습니다.  
>더 자세한 옵션을 확인하려면 공식문서 참조 -> [Installing the Data Protection Application](https://docs.openshift.com/container-platform/4.11/backup_and_restore/application_backup_and_restore/installing/installing-oadp-ocs.html#oadp-installing-dpa_installing-oadp-ocs)   
> 참고2 -> [Backup Storage Locations and Volume Snapshot Locations Customization](https://github.com/openshift/oadp-operator/blob/master/docs/config/bsl_and_vsl.md)

~~~yaml
apiVersion: oadp.openshift.io/v1alpha1
kind: DataProtectionApplication
metadata:
  name: velero-sample
  namespace: openshift-adp
spec:
  backupLocations:
    - velero:
        config:          # S3 storage 정보
          insecureSkipTLSVerify: 'true'  # insecure connections
          profile: default
          region: {REGION}
          s3ForcePathStyle: 'true'    # force velero to use path-style convention
          s3Url: 'https://{URL}'
        credential:
          key: cloud
          name: cloud-credentials
        default: true     # 이 S3 configuration을 default로 사용
        objectStorage:
          bucket: {BUCKET_NAME}
          prefix: {PATH_PREFIX}       #s3스토리지에 저장될 백업파일의 prefix
        provider: aws     # aws provider means use s3 client 
  configuration:
    restic:
      enable: true        # true로 해줘야 나중에 PV백업할때 Restic사용가능
    velero:
      defaultPlugins:     # 사용할 플러그인들. 문서 상단의 OADP plugins 참조
        - openshift       # 필수
        - csi
        - aws
  snapshotLocations:
    - velero:
        config:
          profile: default
          region: {REGION}
        provider: aws
~~~

배포 후, `openshift-adp`의 모든 pod들이 정상적으로 `Running`상태여야 합니다.
~~~
$ oc get all -n openshift-adp
~~~

### 4. 테스트를 위한 샘플 app 배포
백업&복구 테스트를 위해 PV를 붙여둔 nginx pod를 하나 배포해보겠습니다.  

namespace 생성
~~~
$ oc new-project backup-test
~~~

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx # has to match .spec.template.metadata.labels
  serviceName: "nginx"
  replicas: 1
  minReadySeconds: 10 # by default is 0
  template:
    metadata:
      labels:
        app: nginx # has to match .spec.selector.matchLabels
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.8
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
        persistentVolumeClaimRetentionPolicy:
            whenDeleted: Delete
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: <STORAGECLASS_NAME>
      resources:
        requests:
          storage: 1Gi
~~~

SCC 부여  
~~~
$ oc adm policy add-scc-to-user anyuid-z default

clusterrole.rbac.authorization.k8s.io/system:openshift:scc:anyuid added: "default"
~~~

Route 생성  
~~~
$ oc expose svc nginx
~~~

PV동작확인을 위한 sample index 페이지 작성  
~~~
$ oc exec -it web-0 -- /bin/bash

root@web-0:/# echo hellohello! > /usr/share/nginx/html/index.html
~~~

확인:  
~~~
$ oc exec -it web-0 -- cat /usr/share/nginx/html/index.html
hellohello!
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/8.png)  

### 5. Backup

클러스터 전체 백업이 아니라, 특정 namespace만 백업하고, Restic으로 PV까지 같이 백업해보도록 하겠습니다.  

~~~
$ oc get VolumeSnapshotLocations -n openshift-adp
NAME              AGE
velero-sample-1   9d
~~~

~~~yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: backup-test
  namespace: openshift-adp
spec: 
  includeNamespaces:                     # 백업하고자 하는 namespace list
  - backup-test
  storageLocation: velero-sample-1       # DPA 생성시 지정한 storage location 이름
  ttl: 720h0m0s
    defaultVolumesToRestic: true         # PV백업시 Restic 사용 옵션
~~~

생성하면 다음과 같이 status를 확인할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/9.png)  

백업했던 파일들의 storage location으로 가보면 파일들이 저장되고 있는 모습을 확인할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/3.png)  

Backup status가 성공으로 바뀌고나면 복구 테스트를 위해 namespace와 pv를 삭제해줍니다.  

~~~
$ oc delete project backup-test
~~~

### 6. Restore

~~~yaml
apiVersion: velero.io/v1
kind: Restore
metadata:
  name: restore2
  namespace: openshift-adp
spec:
  backupName: backup-test  # 복구할 backup CR의 이름
  includedResources: []    # 복구할 리소스들, 명시하지 않으면 all
  excludedResources:       # 복구에서 제외할 리소스들 (일반적으로 아래 리스트는 제외)
  - nodes
  - events
  - events.events.k8s.io
  - backups.velero.io
  - restores.velero.io
  - resticrepositories.velero.io
  restorePVs: true         # 이 옵션이 true이면 PV까지 같이 복구
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/10.png)  

이렇게 복구 status가 성공으로 뜨고나면, 삭제되었던 namespace인 `backup-test`와 내부 리소스들, 그리고 PV까지 정상적으로 복구된 모습을 확인할 수 있습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/11.png)  

PV복구 확인:  
~~~
$ oc exec -it web-0 -c nginx -- cat /usr/share/nginx/html/index.html
hellohello!
~~~

## Appendix 

### 1. Schedule Backup

Backup CR은 단발성이기 때문에 한번 배포하고나면 끝이지만, 규칙적으로 백업을 설정해둘 수도 있습니다.  

schedule backup에는 cron식을 사용합니다.  

~~~yaml
kind: Schedule
apiVersion: velero.io/v1
metadata:
  name: schedule
  namespace: openshift-adp
spec: 
  schedule: 0 1 * * *       # 매일 새벽1시에 백업
  template:
    hooks: {}
    includedNamespaces:
    - backup-test
    storageLocation: velero-sample-1
    defaultVolumesToRestic: true 
    ttl: 720h0m0s
~~~

>Openshift cluster의 내부 time이 server time과 다를 수도 있으므로 `openshift-adp-controller-manager` pod의 터미널을 통해 시간을 알아내는 것도 방법입니다.  
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/12.png)  

schedule 백업은 `schedule-{time}`의 이름으로 생성됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/4.png)  

스토리지에 저장되는 이름도 schedule이 붙습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/5.png)  

### 2. ODF를 사용하고 있을 때의 PV 백업
ODF는 `ceph`를 기반으로 동작하기 때문에, csi snapshot기능을 이용한 백업이 가능합니다.  

ODF를 배포하게 되면 자동으로 `storageClass`와 `VolumeSnapshotClass`가 정의됩니다.  

우리가 해줘야 할 것은, `VolumeSnapshotClass`에 label을 한 줄 추가해주는 것입니다.  

~~~
$ oc get volumesnapshotclass
NAME                                        DRIVER                                  DELETIONPOLICY   AGE
ocs-storagecluster-cephfsplugin-snapclass   openshift-storage.cephfs.csi.ceph.com   Delete           140d
ocs-storagecluster-rbdplugin-snapclass      openshift-storage.rbd.csi.ceph.com      Delete           140d
~~~

snapshot을 뜰 class모두에 아래와 같은 label을 추가해주시면 됩니다.  
~~~
velero.io/csi-volumesnapshot-class: "true"
~~~

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/13.png)   

그리고 Backup CR은 위와 동일하게, `restic`부분만 제외해서 올려주시면 됩니다.  
~~~yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: backup
  namespace: openshift-adp
  labels:
    velero.io/storage-location: velero-sample-1
spec:
  defaultVolumesToRestic: false
  storageLocation: velero-sample-1
  ttl: 720h0m0s
  volumeSnapshotLocations:
    - velero-sample-1
~~~


## 마지막 재밌는 기능
OADP는 velero를 기반으로 만들어진 오퍼레이터라, velero가 지원하는 기능은 공식문서에 적혀있지 않더라도 사용할 수 있습니다.  

그 중 재밌는 기능이 Cloud migration입니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2022/2022-10-21-oadp-backup-restore/6.png)  
>참고1 :  [How Velero Works](https://velero.io/docs/main/2022/how-velero-works/#object-storage-sync)  
>참고2 : [Cluster migration](https://velero.io/docs/main/2022/migration-case/)

velero는 백업한 리소스들을 S3호환 스토리지에 저장해두는데, single source of truth(SSOT)에 의거하여 S3 스토리지의 파일들을 지속적으로 체크합니다.  

S3스토리지에는 backup config들과 리소스 파일들이 저장되어 있습니다.  

예를 들어 velero가 지켜보다가 S3스토리지에는 A백업에 대한 리소스가 있는데 Kubernetes 클러스터에는 A백업이 없다면 자동으로 싱크를 맞춰줍니다.  

> **Single Source Of Truth?**  
>단일 진실 공급원(SSOT)은 정보 시스템 설계 및 이론중 하나로 정보와 스키마를 오직 하나의 출처에서만 생성 또는 편집하도록 하는 방법론
>
>단일 출처를 통해 데이터를 생성하고 편집하고 접근하므로 데이터의 정합성을 지키고 잘못된 데이터 유통을 방지하고 모두가 동일한 데이터를 참고하도록 함

이것이 velero로 하여금 **Cloud Migration**을 가능하게 하는 기본 원리입니다.  

old cluster에서 백업을 떠두고, new cluster에서 **동일한 S3 스토리지**를 storage location으로 사용하게 되면  
velero가 자동으로 싱크를 맞춰서 **new cluster에서 old cluster의 백업파일을 복구**할 수 있게됩니다.  

다만, 시스템 `namespace`라던지 PV는 cluster 설정에 의존하는 경우가 있으므로 복구할때에 몇가지 설정에 주의해야 합니다. (ex. `region`, `storageclass` 등)  

최근에 직접 테스트해봤는데 생각보다 편하고 깔끔하게 잘 올라와서 좋았던 기억이 있습니다.  

----