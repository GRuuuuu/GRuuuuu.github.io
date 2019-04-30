# Request

## 1.step3에 대한 설명

## 2.예제 코드설명

### Template
index를 추가할때 기본적으로 적용될것  

의미있는 분석을 효과적으로 하기 위해서는 자료의 의미, 즉 자료형에 대한 고려가 필요하며, 개별 자료를 어떻게 다룰 것인지에 대한 정의가 필요하다.  

`${es_url}` : elasticsearch url  
`${PRI_SHARD_NUM}` : primary shard 수  
`${REP_SHARD_NUM}` : replica 수  

~~~json
curl -XPUT http://${es_url}/_template/sys_user_mapping -s -d
{
    "template": "sys_user_mapping",
    "order": 1,
    "settings":{
        "number_of_shards": "'${PRI_SHARD_NUM}'",
        "number_of_replicas": "'${REP_SHARD_NUM}'"
    },
    "mappings": {
        "_default_": {
            "_all":{"enabled": false},
            "date_detection" : true,
            "numeric_detection" : true,
            "dynamic_templates":[
                {
                    "str":{
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping":{
                            "type": "string",
                            "index" : "not_analyzed"
                        }
                    }
                }
            ]
        }
    }
}
~~~

`order` : 숫자가 높은게 낮은거 overriding  
`_default_` : es 8.0부터 deprecated . 적용할 index의 이름을 기입하도록하자.  
`_all` : 얘도 deprecated. disable해놓으면 field명없이는 검색이 안됨. ex) name : ddd  
`date_detection` : 사전에 지정한 날짜 포맷에 일치하면 date필드에 추가함.  
> `dynamic_date_formats`의 기본값은 다음과 같음.  
>"strict_date_optional_time","yyyy/MM/dd HH:mm:ss Z||yyyy/MM/dd Z"  
> ex) test : "2019/04/21" 하면 `date`필드에 추가됨
> 
>`date_detection`를 false로 해두면   
> ex) test : "2019/04/21" 하면 `text`필드에 추가됨

`numeric_detection` : 숫자를 숫자필드에 추가
>enable했을때  
> "my_float":   "1.0",  -> float 필드  
> "my_integer": "1"  -> long 필드

`dynamic_templates` : custom mapping을 가능하게함  
`index` : `analyze`는 string의 언어분석이 필요할때, `not_analyzed`는 단순검색만할때(빠름)  
`match` : 변경사항을 적용할 필드이름     
`match_mapping_type` : json파서가 탐지할수있는 타입. 기본적으로 json파서는 long과 integer를 구분하지 못함. 숫자나오면 long으로 처리함.   
>이거를 integer로 구분하기위해서는 다음과 같이 사용함.  
>~~~json
>"mappings": {
>    "dynamic_templates": [
>      {
>        "integers": {
>          "match_mapping_type": "long",
>          "mapping": {
>            "type": "integer"
>          }
>        }
>      },
>...
>~~~  

**정리** : 이 템플릿 이름은 `sys_user_mapping`이고 기본 템플릿을 오버라이딩 할것임.  
인덱스가 생길때 `shard`와 `replica`의 개수를 정의하고,  
`field`명을 통해 검색하게하고, 날짜와 숫자를 각 필드에 포함되게 하고,  
모든 필드에서 string을 발견하면 string으로 처리하고 string분석하지 않음.  

>언어분석이라는건 공백단위로 분석한다는것

### Type: Cubes
차트의 틀을 정의한 document.  

>아래 json쿼리의 내용은 위 템플릿 json쿼리와 다르게 LE에서 정의한 속성들을 사용하고있기때문에 LE 공식 document에서 직접 언급하지 않는이상 100% 확신할 수 없습니다.  

cubes 예시로 flexlm_license_usage_util_demo의 json 쿼리를 설명  
~~~json
curl -XPUT "http://${es_url}/model/cubes/flexlm_license_usage_util_demo" -H 'Content-Type: application/json' -d'
{
    "id": "flexlm_license_usage_util_demo",
    "metadata": {
      "version": "10.1"
    },
    "dataSets": [
      {
        "id": "ds1",
        "datasource": "ds1",
        "source": "flexlm_license_usage",
        "provider": {
          "id": "elasticsearch",
          "args": {
            "index": "flexlm_license_usage*"
          }
        },
        ...
      }
    ]
}
~~~
`id`: flexlm_license_usage_util_demo라는이름의 document를 생성.  
`dataSets` : `datasource`의 정보를 담고있는 배열  
`datasource` : ds1이라는 이름의 `datasource`의 정보를 정의할것.  
>datasource는 LE를 설치할때 자동으로 생성됨.  
>위치는 `SERVER_TOP/config/config.json`에 정의됨.  
>![image](https://user-images.githubusercontent.com/15958325/56945461-40d24580-6b62-11e9-9265-358225ae572a.png)  

`source`: 사용할 source의 이름은 flexlm_license_usage  
`provider` : 실제 data를 제공해주는 제공자  
-> `index` : provider(ES)에서 가져올 data를 담고있는 index이름. 위의 코드에선 앞의 prefix가 "flexlm_license_usage"와 일치하면 ok  

아래 코드는 위에서 불러온 data에 대해 어떤 field를 가져오고, LE에서는 어떻게 보여줄지를 정의함.    
~~~json
"fields": [
    {
    "id": "id_timestamp",
    "name": "Time stamp",
    "field": "time_stamp",
    "role": "dimension",
    "dataType": "date",
    "agg": {
        "id": "date_histogram",
        "selector": "buckets",
        "arg": {
        "interval": "1h"
        }
    },
    "granularityId": "hour",
    "granularities": [
        {
        "id": "day",
        "name": "Day",
        "format": "yyyy-MM-dd"
        },
        {
        "id": "hour",
        "name": "Hour",
        "format": "yyyy-MM-dd HH"
        }
    ]
    },
    ...
~~~
`id` : fields 배열 인자의 id  
`name` : LE에 display되는 이름  
`field` : datasource에서 가져올 field  
`role` : 해당 필드는 어떤 종류인지    
> role은 총 두가지 종류가 있음.  
> dimension :    
> measure :   

`agg` : 


~~~json
{
    "id": "id_sampling_count",
    "name": "Samping Count",
    "role": "measure",
    "field":"time_stamp_utc",
    "dataType": "numeric",
    "agg": {
        "id": "countd"
    },
    "outputFormat": {
        "maximumFractionDigits": 0
    }
},
~~~
`maximumFractionDigits` : 소숫점아래자리 몇자리 나오게할건지 (default는 0 -정수)  


### Type: Visualizations
차트 자체를 정의하고있는 document.   
즉 차트내용.  

