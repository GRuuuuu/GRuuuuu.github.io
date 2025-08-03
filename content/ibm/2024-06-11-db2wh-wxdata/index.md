---
title: "watsonx.data에 Db2 warehouse 붙이기"
slug: db2wh-wxdata
tags:
  - DB
  - DataScience
date: 2024-06-11T13:00:00+09:00
---

## Overview
Db2 warehouse와 watsonx.data를 연결하여,  
watsonx.data에서 만든 Iceberg테이블을 Db2 warehouse에서 쿼리할 수 있고,  
Db2 warehouse에서 만든 테이블을 watsonx.data의 spark나 presto engine으로 쿼리할 수 있게 세팅하는 방법에 대해서 다루도록 하겠습니다.  

>참고문서   
>[IBM Db2 Warehouse/Accessing watsonx.data](https://www.ibm.com/docs/en/db2-warehouse?topic=tables-accessing-watsonxdata)  
>[How to integrate Db2 with watsonx.data](https://community.ibm.com/community/user/datamanagement/blogs/kelly-schlamb/2024/02/15/db2-watsonx-data-integration)  
>[Multi-engine interoperability in a data lakehouse](https://medium.com/@ausclifford/multi-engine-interoperability-in-a-data-lakehouse-4ed9819dd296)

## Environment
Openshift : `4.15.x`  
CP4D : `5.0.0`  
WatsonX.data : `2.0.0`   
Db2 warehouse : `s11.5.9.0` (24.06.10 기준 반드시 standalone Db2wh를 사용할 것, cpd위의 Db2wh는 안됨)   

## STEP
### 1. [wxdata] catalog 만들기
컴포넌트추가 > add storage  

정보를 입력하고 연결테스트를 한 뒤, 카탈로그를 생성해줍니다.   

<img width="1130" alt="image" src="https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/18c5aa7f-cb2e-4796-bca3-e4f085fc58bd">  

![image](https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/2f382006-6741-41e8-a4e4-6a8c14a32f19)  

그리고 샘플 스키마와 데이터를 집어넣어 줍니다!   

아래에서 쓸 스키마 이름 : `test_schema`
테이블 이름 : `policy_risk`

### 2. [Db2wh] instance 생성
Db2wh instance 생성을 위해 Openshift Operator Catalog를 추가합니다  
~~~
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: ibm-operator-catalog
  namespace: openshift-marketplace
spec:
  displayName: "IBM Operator Catalog" 
  publisher: IBM
  sourceType: grpc
  image: icr.io/cpopen/ibm-operator-catalog
  updateStrategy:
    registryPoll:
      interval: 45m
~~~

db2 operator 설치, namespace는 db2 instance를 올릴 namespace를 선택하여 설치해야 합니다.  
![image](https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/bfecf8e9-37c4-49c0-a321-feae458d5554)  

오퍼레이터 설치가 완료되면 `Db2UInstance`로 Db2wh를 생성해줍니다.  

~~~
apiVersion: db2u.databases.ibm.com/v1
kind: Db2uInstance
metadata:
  name: db2wh-test
spec:
  account:
    privileged: true
  environment:
    authentication:
      ldap:
        enabled: true
    databases:
    - dbConfig:
        APPLHEAPSZ: "25600"
        LOGPRIMARY: "50"
        LOGSECOND: "35"
        STMTHEAP: 51200 AUTOMATIC
      name: BLUDB
    dbType: db2wh
    instance:
      dbmConfig:
        DIAGLEVEL: "2"
      registry:
        DB2_4K_DEVICE_SUPPORT: "ON"
        DB2_ATS_ENABLE: "NO"
        DB2_DISPATCHER_PEEKTIMEOUT: "2"
        DB2_OBJECT_STORAGE_SETTINGS: "OFF"
    partitionConfig:
      dataOnMln0: true
      total: 2
      volumePerPartition: true
  license:
    accept: true
  nodes: 1
  podTemplate:
    db2u:
      resource:
        db2u:
          limits:
            cpu: 8
            memory: 32Gi
  storage:
  - name: meta
    spec:
      accessModes:
      - ReadWriteMany
      resources:
        requests:
          storage: 10Gi
      storageClassName: ocs-storagecluster-cephfs
    type: create
  - name: data
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 100Gi
      storageClassName: ocs-storagecluster-ceph-rbd
    type: template
  - name: backup
    spec:
      accessModes:
      - ReadWriteMany
      resources:
        requests:
          storage: 10Gi
      storageClassName: ocs-storagecluster-cephfs
    type: create
  - name: tempts
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 10Gi
      storageClassName: ocs-storagecluster-ceph-rbd
    type: template
  - name: archivelogs
    spec:
      accessModes:
      - ReadWriteMany
      resources:
        requests:
          storage: 100Gi
      storageClassName: ocs-storagecluster-cephfs
    type: create
  version: s11.5.9.0-cn1
~~~

### 3. [Db2wh] s3 storage alias 등록

이제 Db2wh와 연동할 wxdata의 메타스토어의 s3버킷을 등록해줘야합니다.  

db2u pod(`c-{name}-db2u-0`)로 이동, `db2inst1` 유저로 로그인해서 db2 interactive mode로 접속합니다.  
~~~
sh-4.4$ su - db2inst1
Last login: Mon Jun 10 13:16:37 UTC 2024
[db2inst1@c-db2wh-testtest-db2u-0 - Db2U db2inst1]$ db2
~~~

DB연결 :  
~~~
db2 => connect to bludb

   Database Connection Information

 Database server        = DB2/LINUXX8664 11.5.9.0
 SQL authorization ID   = DB2INST1
 Local database alias   = BLUDB
~~~

storage alias 등록:  
~~~
CALL SYSIBMADM.STORAGE_ACCESS_ALIAS.CATALOG(
   'watsonxdemostorage',                 /* Alias name     */
   'S3',                                 /* Storage type   */
   'https://s3.us-east-1.amazonaws.com', /* S3 URL         */
   '<ACCESSKEY>',                        /* Access key     */
   '<SECRETKEY>',                        /* Secret key     */
   'bigdata-watsonx-demo',               /* Bucket name    */
   '',                                   /* Path to subfolder if required */
   'U',                                  /* Grantee type  */
   'db2inst1');                          /* Granted user */
~~~

예시:  
~~~
db2 => call sysibmadm.storage_access_alias.catalog('bucket-test', 'S3', 'https://s3-openshift-storage.apps.endpoint.com', '{access-key}', '{secret-key}', '{bucket-name}',  null,null, null);

  Return Status = 0
~~~

등록된 스토리지 확인:  
~~~
db2 => list storage access

 Node Directory

Node 1 entry:

ALIAS=bucket-test
VENDOR=S3
SERVER=https://s3-openshift-storage.apps.endpoint.com
USERID=****
CONTAINER=bucket-name
OBJECT=
DBUSER=
DBGROUP=SYSADM
DBNAME=BLUDB   

 Number of entries in the directory = 1

DB20000I  The LIST STORAGE ACCESS command completed successfully.
~~~

> **등록된 storage alias를 제거하려면:**  
>~~~
>call sysibmadm.storage_access_alias.uncatalog('{alias-name}');
>~~~

### 4. [Db2wh] wxdata의 metastore 정보 등록

wxdata의 metastore 정보를 Db2wh에 등록합니다.  

~~~
CALL SYSHADOOP.REGISTER_EXT_METASTORE('{metastore-name}', 'type=watsonx-data,uri=thrift://{HMS Thrift URL}',?,?);
~~~

연결 시 SSL사용할건지 여부 체크, true라면 metastore의 tls secret을 같이 등록해줘야합니다.  
~~~
CALL SET_EXT_METASTORE_PROPERTY('{metastore-name}', 'use.SSL', 'true', ?, ?)
CALL SET_EXT_METASTORE_PROPERTY('{metastore-name}', 'ssl.cert', '{/path/to/cert}', ?, ?);
~~~

> **metastore의 TLS certificate 가져오기**  
>~~~
>oc get secret ibm-lh-tls-secret -o yaml | grep " ca.crt" | sed 's/ \+[.a-z]\+: //' | base64 -d
>~~~

authentication mode 설정, 등록할 유저는 wxdata에서 metastore admin권한을 가진 유저여야만 합니다.   

<img width="1127" alt="image" src="https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/ddf0c7be-33d1-45f6-b806-ccc1038c4858">   

~~~
CALL SET_EXT_METASTORE_PROPERTY('{metastore-name}', 'auth.mode', 'PLAIN', ?, ?)
CALL SET_EXT_METASTORE_PROPERTY('{metastore-name}', 'auth.plain.credentials', 'userid:password', ?, ?)
~~~

등록된 설정 확인하기  
~~~
call ext_metastore_properties('{metastore-name}');
~~~

### (Optional) S3 storage path style 옵션 추가하기
Default로는 IBM COS나 AWS S3스토리지를 사용하게 되어있기 때문에  `https://{bucketname}.{endpoint}` 요런식으로 api를 날리는데,  
ceph나 minio를 사용하는 경우 Default설정을 사용하게 되면 에러가 납니다.   

<img width="748" alt="image" src="https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/86cbd8ca-a677-4c6f-97c6-92b76eac899e">   

bigsql의 자세한 에러로그는 `../../bigsql/c-db2wh-khjang-db2u-0/logs/bigsql-node-0.log` 여기서 확인 가능합니다.  

<img width="844" alt="image" src="https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/1b03c38c-0e71-4e0f-b86f-999b60c366db">     

`https://{bucketname}.{endpoint}` 이렇게 날리던 것을 `https://{endpoint}/{bucketname}`으로 바꿔주어야 합니다.  


~~~
$ bigsql-config -coreSite -set fs.s3a.bucket.{bucketname}.path.style.access=true

(optional)
$ bigsql-config -coreSite -set fs.s3a.bucket.{bucketname}.connection.ssl.enabled=false
~~~

수정된 구성정보는 아래 파일에서 확인가능합니다.  
~~~
$ vi /etc/hadoop/conf/core-site.xml
~~~

수정한 뒤, bigsql을 재시작해주면 끝  
~~~
$ bigsql stop
$ bigsql start
~~~

### 5. [Db2wh] metastore 동기화하기

~~~
CALL EXT_METASTORE_SYNC('{metastore-name}', '{schema-name}', '{table-name}',
'{exist-action}', '{error-action}', NULL)
~~~

`exist-action` : 동기화 하려는 스키마가 이미 Db2 카탈로그에 존재할 때의 액션  
- ERROR : error  
- REPLACE : 기존 테이블을 drop하고 새로운 테이블로 import  
- SKIP : 테이블 import를 스킵  

`error-action` : 에러났을때  
- CONTINUE : 안멈추고 에러 로깅  
- STOP : 에러나면 멈춤  


예시 :   
~~~
db2 => call ext_metastore_sync('wxd-hms', 'test_schema', '.*', 'SKIP', 'CONTINUE', NULL);


  Result set 1
  --------------

  OBJSCHEMA   OBJNAME     OBJATTRIB TYPE STATUS DETAILS                     
  ----------- ----------- --------- ---- ------ ----------------------------
  TEST_SCHEMA POLICY_RISK -         T    OK     Sync from external metastore
  TEST_SCHEMA POLICY_RISK -         T    OK     -                           

  2 record(s) selected.

  Return Status = 0
~~~

### 6. [Db2wh] SELECT & INSERT 해보기

Db2wh에서 wxdata에서 만들었던 테이블 데이터들을 잘 가져온 것을 확인할 수 있습니다.  
~~~
db2 => select char(make_model,20) as make_model from test_schema.policy_risk where LAST_NAME='Stanhope';

MAKE_MODEL          
--------------------
Volkswagen Golf     

  1 record(s) selected.
~~~

다음으로는 Db2wh에서 INSERT쿼리를 통해 데이터를 삽입해보겠습니다.  
~~~
db2 => insert into test_schema.policy_risk values ('',1,'db2whtest',1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'',1);
DB20000I  The SQL command completed successfully.
~~~
wxdata에서도 Db2wh에서 삽입한 데이터를 쿼리할 수 있습니다.  
![image](https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/c2177e84-a6f8-42a0-a585-efcdf8727089)   


### 6. [Db2wh] Table만들기

~~~
create datalake table {SCHEMA_NAME}.{TABLE_NAME} (c1 char(10)) stored as parquet stored by iceberg location 'db2remote://{S3_ALIAS_NAME}//{SCHEMA_NAME}/{TABLE_NAME}' tblproperties('iceberg.catalog'='{METASTORE_NAME}');
~~~

예시 :   
~~~
db2 => create datalake table test_schema.db2table (c1 char(10)) stored as parquet stored by iceberg location 'db2remote://bucket-test//test_schema/db2table' tblproperties('iceberg.catalog'='wxd-hms');
DB20000I  The SQL command completed successfully.
~~~

xdata에서도 확인할 수 있습니다.  
![image](https://github.com/GRuuuuu/hololy-img-repo/assets/15958325/34a9f7fd-e621-4a39-b706-e93039ea014a)   


## Troubleshooting

### Internal error connecting to Hive metastore
~~~
ERROR  Internal error connecting to Hive metastore (see logs for details): The statement failed because a Hadoop component encountered an error. Component receiving the error: "BIGSQL UDF". Component returning the error: "HIVE". Hadoop log identifier: "[BSL-0-7f15584a8]'. Reason: ""Unable to instantiate org.apache.hadoop.hive.metastore.HiveMetaStoreClient".".
~~~

bigsql의 상태가 모두 정상인지 확인
~~~
$ bigsql status
SERVICE              HOSTNAME                               NODE      PID STATUS
Big SQL Master       c-db2wh-testtest-db2u-0.c-db2wh-testtest-db2u-internal    0  1055122 DB2 Running
Big SQL Worker       c-db2wh-testtest-db2u-0.c-db2wh-testtest-db2u-internal    1  1055124 DB2 Running
Standalone Metastore c-db2wh-testtest-db2u-0.c-db2wh-testtest-db2u-internal    -  1060097 Available (listening)
Big SQL Scheduler    c-db2wh-testtest-db2u-0.c-db2wh-testtest-db2u-internal    -  1084683 Available
~~~

그래도 에러가 발생한다면 metastore configuration 시 CA를 제대로 추가했는지 확인  

(ex. `call set_ext_metastore_property('wxd-hms', 'ssl.cert', '/mnt/blumeta0/home/db2inst1/ca.crt', ?, ?);`)

### Table "xxx" cannot be synced. No storage access has been configured for yyyyy/zzzzz

S3 alias 추가가 제대로 되었는지 확인

### Error while creating table (see logs for details): Failed to open input stream for file: s3a://xxxx/yyy/metadata/zzz.metadata.json

`ext_metastore_sync`를 했을 때 발생하는 에러, 정상대로면 수 초안에 결과가 나와야하는게 정상이지만 거의 10분가까이 아무런 output을 내지 않다가 에러를 뱉는다.  

가장 먼저 확인해봐야할 것은 bigsql의 로그:  
`../../bigsql/c-xxxx-db2u-0/logs/bigsql-node-0.log`

만약 아래와 비슷한 에러가 발생한다면  
~~~
Certificate for <bucket-name.endpoint.com> doesn't match any of the subject alternative names: [*.apps.endpoint.com, endpoint.com, api.endpoint.com]
~~~

s3스토리지의 타입이 무엇인지 확인하고 위의 가이드를 따라 path style을 설정해줘야한다.  

설정 이후 `bigsql stop`/`bigsql start`은 잊지말기  

### native zStandard library not available: this version of libhadoop was built without zstd support

>참고 : [How to change compression when writing parquet files using pyspark #4914](https://github.com/apache/iceberg/issues/4914)

Db2 `11.5.9`에서 `zstd`알고리즘으로 압축된 데이터는 지원하지 않기때문에 발생하는 에러.  

최초 Table을 만들때 `lz4`, `snappy`, `gzip` 중 하나로 압축 알고리즘을 정해야 한다.  
(spark configuration으로 설정하는 것은 제대로 반영이 되지 않음, 반드시 table property로 줄 것)

예시)  
~~~python
def create_table_from_parquet_data(spark):
    # load parquet data into dataframce
    df = spark.read.option("header",True).parquet("file:///mnts/files/ddd.parquet")
    # write the dataframe into an Iceberg table
    df.writeTo("catalog.schema.table").tableProperty("write.parquet.compression-codec","gzip").create()
~~~

~~~python
def ingest_from_csv_temp_table(spark):
    # load csv data into a dataframe
    csvDF = spark.read.option("header",True).csv("file:///mnts/files/sss.csv")
    csvDF.createOrReplaceTempView("tempCSVTable")
    # load temporary table into an Iceberg table
    spark.sql('create or replace table catalog.schema.table using iceberg TBLPROPERTIES (\'write.parquet.compression-codec\' = \'gzip\') as select * from tempCSVTable ')
~~~

----