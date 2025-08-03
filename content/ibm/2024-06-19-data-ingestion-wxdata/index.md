---
title: "watsonx.data에서 Data Ingestion하기"
slug: data-ingestion-wxdata
tags:
  - DB
  - DataScience
date: 2024-06-26T13:00:00+09:00
---

## Overview 
watsonx.data에서 스키마와 테이블을 생성하고 데이터를 적재하는 방법에 대해서 살펴보도록 하겠습니다.  

## Environment
Openshift : `4.15.x`  
CP4D : `5.0.0`  
WatsonX.data : `2.0.0`   


## Data Ingestion
### 1. GUI로 넣기 (feat. presto)

DataManager 탭에서 원하는 카탈로그에 스키마를 작성합니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/1.png)

생성한 스키마에서 "파일에서 테이블 작성"을 클릭  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/2.png)

그 다음, 테이블에 집어넣을 데이터를 찾아 업로드합니다.    
Escape character, Field delimiter, Line delimiter를 수정하여 자신의 데이터 파일에 맞는 형식으로 파싱할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/3.png)

업로드가 완료되면 시스템에서 자동으로 컬럼의 타입을 유추해서 지정해주는데요, 사용자가 직접 타입을 수정해줄 수도 있습니다.  

다음으로 해당 데이터를 넣을 카탈로그, 스키마, 생성할 테이블의 이름을 적고 나면,   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/4.png)

구성 정보와 함께 DDL 커맨드가 같이 보입니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/5.png)


작성하기를 누르면 Presto Query로 테이블 생성과 동시에 데이터도 적재됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/6.png)

사실 권장되는 방법은 위의 과정에서 DDL까지만 얻고, 테이블 껍데기만 만들어서 spark로 데이터를 ingestion 하는 것입니다.  
이렇게 함으로써 더 정확한 타입 지정을 해줄 수 있기 때문입니다.  


### 2. GUI로 넣기 (feat. spark)

Query space로 이동하여, 위에서 생성했던 DDL로 테이블 껍데기를 먼저 생성합니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/7.png)

DataManager > 수집작업 > 작성   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/8.png)  

작업을 돌릴 spark 엔진을 선택하고, resource를 설정해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/9.png)

다음으로는 ingest하고자 하는 파일을 선택하고   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/10.png)

Encoding, Escape character, Field delimiter등을 설정해준 뒤,  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/11.png)

어떤 카탈로그, 스키마, 테이블에 데이터를 ingest할 것인지 정의해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/12.png)  

그럼 spark작업의 status를 확인할 수 있고,    
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/13.png)  

성공적으로 완료되면 테이블에 데이터가 잘 적재된 것을 확인할 수 있습니다.   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/14.png)   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/15.png)   


만약 에러가 났다면 spark의 로그를 확인해봐야 합니다.  
wx.data의 GUI에서는 자세한 로그를 확인할 수가 없고, spark의 시스템 버킷으로 가서 확인해봐야 합니다.  

`analytics engine`을 사용한다면 cpd 인스턴스 페이지의 인스턴스 스토리지 볼륨 참고,     
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/16.png)     


`native spark engine`을 사용한다면 wx.data의 인프라페이지의 엔진 세부정보 > volume을 참고  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/18.png)  


volume이름을 확인했다면 해당 볼륨의 path로 이동하여 `{spark engine id}/{spark job id}/logs` 밑의 `spark-driver-~~~-stdout` 파일을 다운로드받아 내용을 확인해보면 됩니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/17.png)       



### 3-1. CURL로 spark job 돌리기 (feat. Analytics Engine)

gui를 접근하지 못한다거나, batch 작업을 돌려야 하는 경우 curl로도 spark job을 실행시킬 수 있습니다.  

아래 코드를 참고하여 돌리길 원하는 spark 코드를 작성합니다.  

Sample code -> [link](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/curl-spark-sample.py)   

> **주의!**    
> ceph나 minio같은 (path style) 버킷을 사용한다면, `.config("spark.hadoop.fs.s3a.bucket.{BUCKET_NAME}.path.style.access", "true")` 해당 옵션을 반드시 `true`로 변경해줄 것,  
> 반대로 virtual hosted style의 AWS S3, IBM Cloud Object Storage 등의 s3 storage들은 `false`여야 합니다.  

그 다음으로, spark engine에 대해 권한이 있는 유저의 API KEY가 필요합니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/19.png)    

~~~sh
#echo "<username>:<api_key>" | base64

$ echo "user:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" |base64
<base64-encoded-user-api-pair>

$ export TOKEN=<base64-encoded-user-api-pair>
~~~

Spark job 실행 :   
~~~sh
$ curl -k -X POST https://{SPARK_ENGINE_ENDPOINT}/spark_applications -H "Authorization: ZenApiKey $TOKEN" -X POST -d '{
    "application_details": {
        "application": "/mnts/{CPD_PV_PATH}/{SPARK_APP_FILENAME}",
        "conf": {
            "spark.driver.extraClassPath": "/opt/ibm/connectors/iceberg-lakehouse/iceberg-3.3.2-1.2.1-hms-4.0.0-shaded.jar",
            "spark.sql.catalogImplementation": "hive",
            "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark.sql.iceberg.vectorization.enabled": "false",
            "spark.sql.catalog.{CATALOG_NAME}": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.{CATALOG_NAME}.type": "hive",
            "spark.sql.catalog.{CATALOG_NAME}.uri": "thrift://ibm-lh-lakehouse-hive-metastore-svc.cpd-inst-operand.svc.cluster.local:9083",
            "spark.hive.metastore.client.auth.mode": "PLAIN",
            "spark.hive.metastore.client.plain.username": "{USERNAME}}",
            "spark.hive.metastore.client.plain.password": "{PASSWORD}",
            "spark.hive.metastore.use.SSL": "true",
            "spark.hive.metastore.truststore.type": "JKS",
            "spark.hive.metastore.truststore.path": "file:///opt/ibm/jdk/lib/security/cacerts",
            "spark.hive.metastore.truststore.password": "changeit"
        }
    },
    "volumes": [{
        "name": "{CPD_NAMESPACE}::{CPD_PV_NAME}",
        "mount_path": "/mnts/{CPD_PV_PATH}",
        "source_sub_path": ""
    }]
}'
~~~

빠진 부분을 잘 채워서 실행시키면 GUI에서 spark job을 실행시켰던 것 처럼, spark engine에서 실행되고 있는 job의 status와 로그들을 확인할 수 있습니다.  

### 3-2. CURL로 spark job 돌리기 (feat. Native Spark)
Watsonx.data 2.0.0부터 spark engine을 native로 지원하기 시작했습니다!    
native spark는 wxdata에 등록되고 spark에 연결된 스토리지와 카탈로그의 credential정보들은 자동으로 default configuration에 등록됩니다.  

때문에 CURL과 python application에 적어야 할 configuration의 개수가 현저히 줄었는데요,  

sample python app:  
~~~py
from pyspark.sql import SparkSession
import os
from datetime import datetime

def init_spark():
    spark = SparkSession.builder.appName("lh-hms-cloud").enableHiveSupport().getOrCreate()
    return spark

def create_database(spark,bucket_name,catalog):
    spark.sql(f"create database if not exists {catalog}.ivttestdb LOCATION 's3a://{bucket_name}/'")
    
    
def list_databases(spark,catalog):
    # list the database under lakehouse catalog
    spark.sql(f"show databases from {catalog}").show()

def basic_iceberg_table_operations(spark,catalog):
    # demonstration: Create a basic Iceberg table, insert some data and then query table
    print("creating table")
    spark.sql(f"create table if not exists {catalog}.ivttestdb.testTable(id INTEGER, name VARCHAR(10), age INTEGER, salary DECIMAL(10, 2)) using iceberg").show()
    print("table created")
    spark.sql(f"insert into {catalog}.ivttestdb.testTable values(1,'Alan',23,3400.00),(2,'Ben',30,5500.00),(3,'Chen',35,6500.00)")
    print("data inserted")
    spark.sql(f"select * from {catalog}.ivttestdb.testTable").show()



def clean_database(spark,catalog):
    # clean-up the demo database
    spark.sql(f'drop table if exists {catalog}.ivttestdb.testTable purge')
    spark.sql(f'drop database if exists {catalog}.ivttestdb cascade')

def main():
    try:
        spark = init_spark()
        
        create_database(spark,"<bucket_name>","<catalog_name>")
        list_databases(spark,"<catalog_name>")
        basic_iceberg_table_operations(spark,"<catalog_name>")
        
        
    finally:
        # clean-up the demo database
        clean_database(spark,"<catalog_name>")
        spark.stop()

if __name__ == '__main__':
    main()
~~~

sample curl command :    
~~~
curl --request POST \
  --url https://{spark_endpoint}/applications \
  --header 'Authorization: ZenApiKey {Your ZenApiKey}' \
  --header 'Content-Type: application/json' \
  --header 'LhInstanceId: {wxdata instance id}' \
  --data '{
  "application_details": {
    "application": "/mnts/{CPD_PV_PATH}",
    "conf": { 
            "spark.hive.metastore.client.plain.username": "xxx",
            "spark.hive.metastore.client.plain.password": "ddd",
            "spark.hadoop.wxd.cas.apiKey": "ZenApiKey {Your ZenApiKey}"
    }
  },
  "volumes": [
    {
      "name": "{CPD_NAMESPACE}::{CPD_PV_NAME}",
      "mount_path": "/mnts/{CPD_PV_PATH}"
    }
  ]
}'
~~~




### 4. vscode extension 사용하기
> native spark engine만 사용가능

vscode marketplace에서 watsonx.data 검색 후 설치   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/20.png)     

Setting에서 필요한 값들을 기재해줍니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/21.png)     
Host의 경우 CP4D 메인 url만 넣어도 됩니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/22.png)     
ssh key는 로컬 pc에 존재하는 ssh key, 없으면 만들어서 경로를 적어줍니다.  

그리고 왼쪽 상단바에 위치한 빙글빙글버튼을 누르고나서 CP4D의 apikey를 넣으면 아래 사진처럼 현재 watsonx.data에 연결된 spark 엔진들을 확인할 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/23.png)      

연결하고자하는 스파크 엔진을 더블클릭하면 아래와 같이 Spark Lab 구성 정보가 뜨게 되고, 원하는 리소스를 기재한 뒤, 앞선 설정에서 등록했던 private key의 public key를 넣어줍니다.   
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/24.png)     

연결 완료!  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-06-16-wxdata-data-ingestion.md/25.png)     

다음으로는 python 파일을 `/work`밑에 생성하고, 터미널을 열어서 `python ddd.py`로 실행하면 선택한 스파크엔진으로 job이 돌아가게 됩니다!  

에러가 나면 바로 터미널에서 확인할 수 있고 로그도 바로바로 확인할 수 있어서 개발용도로 적합한 것 같습니다.  

## Troubleshooting
### Unable to execute HTTP request: Certificate for <...> doesn't match any of the subject alternative names

원인 : s3 storage의 path 스타일 차이 때문

bucket이름이 ddd라면  
AWS S3나 IBM COS -> `ddd.endpoint.com` 이런식의 virtual host path 이고  
Ceph나 minio -> `endpoint.com/ddd` 이런식으로 표현됩니다.  

때문에 뒷단의 스토리지를 어떤 녀석을 고르느냐에 따라 spark config를 다르게 해주어야 합니다.  

AWS S3나 IBM COS ->  `spark.hadoop.fs.s3a.bucket.{버킷이름}.path.style.access = false`   
Ceph나 minio -> `spark.hadoop.fs.s3a.bucket.{버킷이름}.path.style.access = true`  

### Unable to calculate a request signature: Server returned HTTP response code: 401 for URL: https://ibm-lh-lakehouse-cas-svc:3500/cas/v1/signature
native spark engine에서 job을 돌릴 시 발생하는 에러   

spark configuration에 추가 :  
~~~
.config("spark.hive.metastore.client.plain.username","ddd") \
.config("spark.hive.metastore.client.plain.password","ddd") \
~~~

### Unable to calculate a request signature: Server returned HTTP response code: 422 for URL: https://ibm-lh-lakehouse-cas-svc.cpd-inst-operand.svc.cluster.local:3500/cas/v1/signature: Unable to calculate a request signature: Server returned HTTP response code: 422 for URL: https://ibm-lh-lakehouse-cas-svc.cpd-inst-operand.svc.cluster.local:3500/cas/v1/signature
native spark engine에서 job을 돌릴 시 발생하는 에러
 
spark configuration에 이녀석을    
`.config("spark.hadoop.wxd.cas.apiKey", "<zenapikey>")`   

이렇게 바꿔보자 :   
`.config("spark.hadoop.wxd.cas.apiKey", "ZenApiKey <your ZenApiKey>")`

----