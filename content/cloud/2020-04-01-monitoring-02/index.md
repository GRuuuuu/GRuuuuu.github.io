---
title: "Kubernetes Monitoring - Prometheus 실습"
slug: monitoring-02
tags:
  - Container
  - Cloud
  - Kubernetes
  - Monitoring
  - Prometheus
date: 2020-03-31T13:00:00+09:00
---

## Overview
이번 포스팅에서는 쿠버네티스 클러스터의 메트릭들을 프로메테우스로 수집하고 web UI를 통해 시각화 시키는 작업을 해보겠습니다.  

참고 링크 : [쿠버네티스 시작하기(11) - Prometheus & Node-Exporter & AlertManager 연동](https://twofootdog.tistory.com/17)

# Prerequisites
먼저 쿠버네티스 클러스터를 생성해주세요.  

참고링크 : [호롤리한하루/Install Kubernetes on CentOS/RHEL](https://gruuuuu.github.io/cloud/k8s-install/)  

> 본 실습에서 사용한 spec :   
>`OS : CentOS v7.6`  
>`Arch : x86` 
>
>`Kubernetes` : `v1.16.2`  
>`Master` : 4cpu, ram16G (1개)  
>`Node` : 4cpu, ram16G (2개)  

# Step
## 1. Prometheus 배포
### namespace
제일먼저 해줘야 할 것은 프로메테우스관련 오브젝트들이 사용할 namespace를 생성해 주는 것입니다.  
~~~sh
$ kubectl create ns monitoring
~~~

### Cluster Role
다음으로는 프로메테우스 컨테이너가 **쿠버네티스 api에 접근할 수 있는 권한**을 부여해주기 위해 `ClusterRole`을 설정해주고 `ClusterRoleBinding`을 해줍니다.  
생성된 ClusterRole은 monitoring namespace의 기본 서비스어카운트와 연동되어 권한을 부여해줍니다.  
~~~yaml
# prometheus-cluster-role.yaml

apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  name: prometheus
  namespace: monitoring
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: default
  namespace: monitoring
~~~

### Configmap
프로메테우스가 기동되려면 환경설정파일이 필요한데 해당 환경설정 파일을 정의해주는 부분입니다.  

data 밑에 `prometheus.rules`와 `prometheus.yml`를 각각 정의하게 되어있습니다.    
- **prometheus.rules** : 수집한 지표에 대한 알람조건을 지정하여 특정 조건이 되면 AlertManager로 알람을 보낼 수 있음
- **prometheus.yml** : 수집할 지표(metric)의 종류와 수집 주기등을 기입

~~~yaml
# prometheus-config-map.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-server-conf
  labels:
    name: prometheus-server-conf
  namespace: monitoring
data:
  prometheus.rules: |-
    groups:
    - name: container memory alert
      rules:
      - alert: container memory usage rate is very high( > 55%)
        expr: sum(container_memory_working_set_bytes{pod!="", name=""})/ sum (kube_node_status_allocatable_memory_bytes) * 100 > 55
        for: 1m
        labels:
          severity: fatal
        annotations:
          summary: High Memory Usage on {{ $labels.instance }}
          identifier: "{{ $labels.instance }}"
          description: "{{ $labels.job }} Memory Usage: {{ $value }}"
    - name: container CPU alert
      rules:
      - alert: container CPU usage rate is very high( > 10%)
        expr: sum (rate (container_cpu_usage_seconds_total{pod!=""}[1m])) / sum (machine_cpu_cores) * 100 > 10
        for: 1m
        labels:
          severity: fatal
        annotations:
          summary: High Cpu Usage
  prometheus.yml: |-
    global:
      scrape_interval: 5s
      evaluation_interval: 5s
    rule_files:
      - /etc/prometheus/prometheus.rules
    alerting:
      alertmanagers:
      - scheme: http
        static_configs:
        - targets:
          - "alertmanager.monitoring.svc:9093"

    scrape_configs:
      - job_name: 'kubernetes-apiservers'

        kubernetes_sd_configs:
        - role: endpoints
        scheme: https

        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

        relabel_configs:
        - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
          action: keep
          regex: default;kubernetes;https

      - job_name: 'kubernetes-nodes'

        scheme: https

        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

        kubernetes_sd_configs:
        - role: node

        relabel_configs:
        - action: labelmap
          regex: __meta_kubernetes_node_label_(.+)
        - target_label: __address__
          replacement: kubernetes.default.svc:443
        - source_labels: [__meta_kubernetes_node_name]
          regex: (.+)
          target_label: __metrics_path__
          replacement: /api/v1/nodes/${1}/proxy/metrics


      - job_name: 'kubernetes-pods'

        kubernetes_sd_configs:
        - role: pod

        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
          action: replace
          regex: ([^:]+)(?::\d+)?;(\d+)
          replacement: $1:$2
          target_label: __address__
        - action: labelmap
          regex: __meta_kubernetes_pod_label_(.+)
        - source_labels: [__meta_kubernetes_namespace]
          action: replace
          target_label: kubernetes_namespace
        - source_labels: [__meta_kubernetes_pod_name]
          action: replace
          target_label: kubernetes_pod_name

      - job_name: 'kube-state-metrics'
        static_configs:
          - targets: ['kube-state-metrics.kube-system.svc.cluster.local:8080']

      - job_name: 'kubernetes-cadvisor'

        scheme: https

        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

        kubernetes_sd_configs:
        - role: node

        relabel_configs:
        - action: labelmap
          regex: __meta_kubernetes_node_label_(.+)
        - target_label: __address__
          replacement: kubernetes.default.svc:443
        - source_labels: [__meta_kubernetes_node_name]
          regex: (.+)
          target_label: __metrics_path__
          replacement: /api/v1/nodes/${1}/proxy/metrics/cadvisor

      - job_name: 'kubernetes-service-endpoints'

        kubernetes_sd_configs:
        - role: endpoints

        relabel_configs:
        - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
          action: replace
          target_label: __scheme__
          regex: (https?)
        - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
          action: replace
          target_label: __address__
          regex: ([^:]+)(?::\d+)?;(\d+)
          replacement: $1:$2
        - action: labelmap
          regex: __meta_kubernetes_service_label_(.+)
        - source_labels: [__meta_kubernetes_namespace]
          action: replace
          target_label: kubernetes_namespace
        - source_labels: [__meta_kubernetes_service_name]
          action: replace
          target_label: kubernetes_name
~~~

### deployment
프로메테우스 이미지를 담은 pod을 담은 deployment controller

~~~yaml
# prometheus-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-deployment
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus-server
  template:
    metadata:
      labels:
        app: prometheus-server
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest
          args:
            - "--config.file=/etc/prometheus/prometheus.yml"
            - "--storage.tsdb.path=/prometheus/"
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: prometheus-config-volume
              mountPath: /etc/prometheus/
            - name: prometheus-storage-volume
              mountPath: /prometheus/
      volumes:
        - name: prometheus-config-volume
          configMap:
            defaultMode: 420
            name: prometheus-server-conf

        - name: prometheus-storage-volume
          emptyDir: {}
~~~

### node exporter
프로메테우스가 수집하는 메트릭은 쿠버네티스에서 기본으로 제공하는 system metric만 수집하는게 아니라 그 외의 것들도 수집하기 때문에 수집역할을 하는 에이전트를 따로 두어야 합니다.  

그 역할을 해주는게 `node-exporter`이고 각 노드에 하나씩 띄워야 하므로 `DaemonSet`으로 구성해주도록 합니다.  

~~~yaml
# prometheus-node-exporter.yaml

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
  labels:
    k8s-app: node-exporter
spec:
  selector:
    matchLabels:
      k8s-app: node-exporter
  template:
    metadata:
      labels:
        k8s-app: node-exporter
    spec:
      containers:
      - image: prom/node-exporter
        name: node-exporter
        ports:
        - containerPort: 9100
          protocol: TCP
          name: http
---
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: node-exporter
  name: node-exporter
  namespace: kube-system
spec:
  ports:
  - name: http
    port: 9100
    nodePort: 31672
    protocol: TCP
  type: NodePort
  selector:
    k8s-app: node-exporter
~~~

### Service 
마지막으로 프로메테우스 pod을 외부로 노출시키는 서비스를 구성해줍니다.  
~~~yaml
# prometheus-svc.yaml

apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
  namespace: monitoring
  annotations:
      prometheus.io/scrape: 'true'
      prometheus.io/port:   '9090'
spec:
  selector:
    app: prometheus-server
  type: NodePort
  ports:
    - port: 8080
      targetPort: 9090
      nodePort: 30003
~~~

### 배포
한 번에 배포 :  
~~~sh
$ kubectl apply -f prometheus-cluster-role.yaml
$ kubectl apply -f prometheus-config-map.yaml
$ kubectl apply -f prometheus-deployment.yaml
$ kubectl apply -f prometheus-node-exporter.yaml
$ kubectl apply -f prometheus-svc.yaml
~~~

prometheus pod도 정상적으로 동작하고, 현재 실습환경은 노드가 2개이므로 node-exporter도 2개 뜬 것을 확인할 수 있습니다.  
~~~sh
$ kubectl get pod -n monitoring

NAME                                     READY   STATUS    RESTARTS   AGE
node-exporter-99w2v                      1/1     Running   0          18s
node-exporter-f9q7f                      1/1     Running   0          18s
prometheus-deployment-7bcb5ff899-h4rb7   1/1     Running   0          65s
~~~


`ip:30003`로 접근해보면 prometheus의 web ui로 접근할 수 있습니다.  
쿠버네티스의 다양한 metric들을 그래프로 확인할 수 있습니다.  

<img src="https://user-images.githubusercontent.com/15958325/78095208-58204f80-7411-11ea-9b91-1bc9b4333dac.png" width="600px">    

<img src="https://user-images.githubusercontent.com/15958325/78095301-8aca4800-7411-11ea-9e0a-2ef09899ffce.png" width="600px">  

<img src="https://user-images.githubusercontent.com/15958325/78095372-b77e5f80-7411-11ea-8156-63984076c8d3.png" width="600px">    

상단 메뉴의 Status > Targets를 들어가보면, 프로메테우스가 현재 모니터링하고있는 타겟을 확인할 수 있습니다.  
근데 이 중 `kube-state-metrics`가 (0/1 up)으로 아직 올라가지 않은 것으로 표시됩니다.  
<img src="https://user-images.githubusercontent.com/15958325/78095419-dbda3c00-7411-11ea-8b5b-2a417259f2ca.png" width="600px">   

`kube-state-metrics`는 쿠버네티스 클러스터 내 오브젝트(예를들면 Pod)에 대한 지표정보를 생성하는 서비스입니다.  
따라서 Pod 상태정보를 모니터링하기 위해서는 kube-state-metrics가 떠 있어야 합니다.   

### Kube State Metrics 배포
첫번째로 배포할 것은 ClusterRole과 ClusterRoleBinding입니다.  

~~~yaml
# kube-state-cluster-role.yaml

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kube-state-metrics
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kube-state-metrics
subjects:
- kind: ServiceAccount
  name: kube-state-metrics
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kube-state-metrics
rules:
- apiGroups:
  - ""
  resources: ["configmaps", "secrets", "nodes", "pods", "services", "resourcequotas", "replicationcontrollers", "limitranges", "persistentvolumeclaims", "persistentvolumes", "namespaces", "endpoints"]
  verbs: ["list","watch"]
- apiGroups:
  - extensions
  resources: ["daemonsets", "deployments", "replicasets", "ingresses"]
  verbs: ["list", "watch"]
- apiGroups:
  - apps
  resources: ["statefulsets", "daemonsets", "deployments", "replicasets"]
  verbs: ["list", "watch"]
- apiGroups:
  - batch
  resources: ["cronjobs", "jobs"]
  verbs: ["list", "watch"]
- apiGroups:
  - autoscaling
  resources: ["horizontalpodautoscalers"]
  verbs: ["list", "watch"]
- apiGroups:
  - authentication.k8s.io
  resources: ["tokenreviews"]
  verbs: ["create"]
- apiGroups:
  - authorization.k8s.io
  resources: ["subjectaccessreviews"]
  verbs: ["create"]
- apiGroups:
  - policy
  resources: ["poddisruptionbudgets"]
  verbs: ["list", "watch"]
- apiGroups:
  - certificates.k8s.io
  resources: ["certificatesigningrequests"]
  verbs: ["list", "watch"]
- apiGroups:
  - storage.k8s.io
  resources: ["storageclasses", "volumeattachments"]
  verbs: ["list", "watch"]
- apiGroups:
  - admissionregistration.k8s.io
  resources: ["mutatingwebhookconfigurations", "validatingwebhookconfigurations"]
  verbs: ["list", "watch"]
- apiGroups:
  - networking.k8s.io
  resources: ["networkpolicies"]
  verbs: ["list", "watch"]
~~~

위의 ClusterRole과 연동될 서비스어카운트를 생성해줍니다.  
~~~yaml
# kube-state-svcaccount.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube-state-metrics
  namespace: kube-system
~~~

kube-state-metrics의 deployment도 구성해줍니다.  

~~~yaml
# kube-state-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: kube-state-metrics
  name: kube-state-metrics
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kube-state-metrics
  template:
    metadata:
      labels:
        app: kube-state-metrics
    spec:
      containers:
      - image: quay.io/coreos/kube-state-metrics:v1.8.0
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          timeoutSeconds: 5
        name: kube-state-metrics
        ports:
        - containerPort: 8080
          name: http-metrics
        - containerPort: 8081
          name: telemetry
        readinessProbe:
          httpGet:
            path: /
            port: 8081
          initialDelaySeconds: 5
          timeoutSeconds: 5
      nodeSelector:
        kubernetes.io/os: linux
      serviceAccountName: kube-state-metrics
~~~

마지막으로 kube-state-metrics의 서비스를 생성해주고 :   
~~~yaml
# kube-state-svc.yaml

apiVersion: v1
kind: Service
metadata:
  labels:
    app: kube-state-metrics
  name: kube-state-metrics
  namespace: kube-system
spec:
  clusterIP: None
  ports:
  - name: http-metrics
    port: 8080
    targetPort: http-metrics
  - name: telemetry
    port: 8081
    targetPort: telemetry
  selector:
    app: kube-state-metrics
~~~

배포해주면 끝입니다.  
~~~sh
$ kubectl apply -f kube-state-cluster-role.yaml
$ kubectl apply -f kube-state-deployment.yaml
$ kubectl apply -f kube-state-svcaccount.yaml
$ kubectl apply -f kube-state-svc.yaml
~~~

~~~sh
$ kubectl get pod -n kube-system

NAME                                       READY   STATUS    RESTARTS   AGE
...
kube-state-metrics-59bd4d9d-nbfrq          1/1     Running   0          50s
~~~

다시 프로메테우스의 웹으로 돌아가서 `Target`을 확인해보면 `kube-state-metrics`가 정상적으로 실행되고 있는 것을 확인할 수 있습니다.

<img src="https://user-images.githubusercontent.com/15958325/78097313-efd46c80-7416-11ea-8d49-4b3c8aaab7cb.png" width="600px">  

## 2. Grafana 연동
그라파나는 수집 지표 정보를 분석 및 시각화 시키는 오픈소스 툴입니다.  
주로 데이터를 시각화 하기 위한 대시보드로 주로 사용됩니다.  

위에서 모니터링툴인 프로메테우스를 사용해 쿠버네티스의 metric들을 수집하는 것까지 했는데 이번엔 그라파나를 붙여서 프로메테우스의 데이터들을 시각화시켜보도록 하겠습니다.  

먼저 그라파나 pod과 svc를 생성해줍니다.  
~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      name: grafana
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - name: grafana
          containerPort: 3000
        env:
        - name: GF_SERVER_HTTP_PORT
          value: "3000"
        - name: GF_AUTH_BASIC_ENABLED
          value: "false"
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "true"
        - name: GF_AUTH_ANONYMOUS_ORG_ROLE
          value: Admin
        - name: GF_SERVER_ROOT_URL
          value: /
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
  annotations:
      prometheus.io/scrape: 'true'
      prometheus.io/port:   '3000'
spec:
  selector:
    app: grafana
  type: NodePort
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 30004
~~~

~~~sh
$ kubectl apply -f grafana.yaml

$ kubectl get pod -n monitoring
NAME                                     READY   STATUS    RESTARTS   AGE
grafana-799c99855d-kxhkm                 1/1     Running   0          16s
node-exporter-99w2v                      1/1     Running   0          66m
node-exporter-f9q7f                      1/1     Running   0          66m
prometheus-deployment-7bcb5ff899-h4rb7   1/1     Running   0          67m
~~~

### datasource 추가

`ip:30004`로 접속해보면 다음 화면을 보실 수 있습니다.  
이제 그라파나와 프로메테우스를 연동시켜줄겁니다.  

`Add data source`로 이동 :  
<img src="https://user-images.githubusercontent.com/15958325/78097949-aa18a380-7418-11ea-9292-e9dffcefaf43.png" width="600px">  

시계열 데이터모델을 지원하는 여러 db를 확인할 수 있고, 우리는 프로메테우스를 사용할 것이니 프로메테우스를 선택 :     
<img src="https://user-images.githubusercontent.com/15958325/78098151-26ab8200-7419-11ea-8860-1f0988ab7fac.png" width="600px">   


연동할 프로메테우스의 정보를 기입해주어야 합니다.  
url은 서비스의 internal ip를 참고해서 적어주도록 합니다.  
~~~sh
$ kubectl get svc -n monitoring

NAME                 TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
grafana              NodePort   10.101.152.163   <none>        3000:30004/TCP   6m43s
prometheus-service   NodePort   10.101.196.111   <none>        8080:30003/TCP   73m
~~~

<img src="https://user-images.githubusercontent.com/15958325/78098229-5fe3f200-7419-11ea-99be-f9c49d8e4cbc.png" width="500px">  

Save & Test 버튼을 눌렀을 때 "Data source is working"메세지가 떠야합니다.  

<img src="https://user-images.githubusercontent.com/15958325/78098290-99b4f880-7419-11ea-9514-88293010390d.png" width="400px">  

해당 메세지가 뜨면 연동은 성공!  

연동을 했으니 프로메테우스의 데이터들을 시각화 해줄 dashboard를 만들어야합니다.  
PromQL을 통해 사용자가 직접 원하는 대시보드를 만들수도있지만,  
남이 만든것을 쉽게 가져다가 사용할수도 있습니다.  

### dashboard 추가 

이번 실습에서는 PromQL을 작성하는게 아니라 다른사람이 만든 대시보드를 import해보도록 하겠습니다.  

[Grafana](https://grafana.com/)페이지로 이동 ->  

Grafana > Dashboard로 이동해서 kubernetes를 검색합니다.  

아무거나 마음에 드는것을 고르고 copy id를 눌러 대시보드의 id를 복사합니다.  

<img src="https://user-images.githubusercontent.com/15958325/78098569-6d4dac00-741a-11ea-8379-c3e260a7615f.png" width="600px">   

그라파나 UI로 돌아와서 Import Dashboard로 이동해 복사한 번호를 붙여넣기 합니다.  

<img src="https://user-images.githubusercontent.com/15958325/78098629-9c641d80-741a-11ea-8cf6-dcc60869a614.png" width="600px">   

<img src="https://user-images.githubusercontent.com/15958325/78098633-9ec67780-741a-11ea-8c22-ef75ddccdaba.png" width="600px">   

항목입력해주고 Import해주면 예쁜 dashboard를 확인할 수 있습니다!   

<img src="https://user-images.githubusercontent.com/15958325/78098636-a128d180-741a-11ea-9f1c-af6c6ca7fd8d.png" width="600px">   

> Deployment memory usage가 N/A로 뜨는 이유는 해당 dashboard의 PromQL이 저희의 prometheus와 맞지 않아서인데요... PromQL을 수정해주면 잘 뜬다고 하는데 한번 도전해보시기 바랍니다.  

## 마치며
이렇게 쿠버네티스-프로메테우스-그라파나 가 완성되었습니다.  
모니터링 구조의 기초 뼈대는 갖춰진 셈이니 이제 상황과 요구에 맞게 추가하시고 수정하시면 될 것 같습니다.  

----
