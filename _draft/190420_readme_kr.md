
## 1. index 생성을 위한 template정의
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
                        "match_mapping_type": "text",
                        "mapping":{
                            "type": "text",
                            "analyzer": "keyword"
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

>언어분석이라는건 공백단위로 분석한다는거심

## 2. 사용자 매핑 데이터를 csv파일에서 elasticsearch로 가져오기

${logstash_dir}/bin/logstash -f indexer/user_map.conf
   
Note:
   - `user_map.conf`는 csv파일에서 elasticsearch로 데이터를 로드하는걸 정의해주는 파일. 
   
   - `testdata.csv`에 정의된 column은 user_map.conf의 필터섹션과 일치해야함.

   - 위 커맨드는 csv데이터를 `sys_user_mapping` 인덱스로 가져옴.
	 
   - csv를 다시 로드하려면 es에서 `sys_user_mapping` 인덱스를 삭제하고 `user_map.conf`에 의해 정의된 `.opsition`파일도 삭제. 
 
>맵핑은 색인의 문서를 여러 논리적 그룹으로 나누고 필드의 특성, 이를테면 필드의 검색 가능성 또는 토큰화 여부, 즉 별개의 단어로 분리되는지 여부 등을 지정합니다.

## 3. 로더 구성
2단계에서 로드된 사용자 매핑 정보를 새로운 샘플링데이터로 합쳐야함.

e.g. $explorer_node_dir/conf/dataloader/lsbacct.xml  

add following section:
~~~xml
<Dependencies>
	<Dependency Name="sys_user_mapping">
        <Keys>
            <Key Name="user_name"/>
        </Keys>
        <Values>
    	    <Value Name="department_name"/>
        </Values>
	</Dependency>
</Dependencies>
~~~

Note: this only applies to new data in index of flexlicusage loader	(flexlm_license_usage-%{yyyymm} in es).   
flexlicusage 로더에 의해 생기는 index의 새로운 데이터에만 적용됨.


## 4. Report customization description

report_model.sh에 es_url 수정하고 스크립트 실행시킴.   
es의 report모델을 업데이트함.

expolorer gui화면으로가면 새로운 차트가 생긴것을 확인할 수 있음.  

-------------------------------------------------
Update report model to add user mapping fields (department, etc) to dimensions/filters  
사용자 매핑 필드(department 등)를 report 모델에 업데이트함.  

a) explorer gui에서 관련 차트를 찾고 url에 표시된 doc id를 사용해서 es에서 모델정의를 검색함
~~~   
e.g. curl -XGET http://${es_url}/model/doc/flexlm03
~~~

시각화 모델에는 cube정보(es에서 데이터검색할때 쓰는)와 차트 레이아웃이 포함되어있음.  
차트 레이아웃 : (chart type, filters, controls (time period, dimensions, measures), etc)  
dimension/measure/filter을 추가해야하는 경우, 필터를 추가하고, b단계로 이동. (필터추가 어디다가?)
   
b) 시각화된 모델에서 cube정보를 찾고, 정의를 수정함  

~~~
GET /model/doc/flexlm_license_usage_util
~~~  

수정한 definition을 복사하고 es로 업데이트하여 차트 definition 업데이트  
   