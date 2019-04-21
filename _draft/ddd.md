
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



## 2. 사용자 매핑 데이터를 csv파일에서 elasticsearch로 가져오기

${logstash_dir}/bin/logstash -f indexer/user_map.conf
   
Note:
   - `user_map.conf`는 csv파일에서 elasticsearch로 데이터를 로드하는걸 정의해주는 파일. 
   
   - `testdata.csv`에 정의된 column은 user_map.conf의 필터섹션과 일치해야함.

   - 위 커맨드는 csv데이터를 `sys_user_mapping` 인덱스로 가져옴.
	 
   - csv를 다시 로드하려면 es에서 `sys_user_mapping` 인덱스를 삭제하고 `user_map.conf`에 의해 정의된 `.opsition`파일도 삭제. 
 

## 3. Configure related loader to combine user mapping info loaded in step 2 into new sampling data.
   e.g. $explorer_node_dir/conf/dataloader/lsbacct.xml
   add following section:
   ---------------------------------
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
	----------------------------------

    Note: this only applies to new data in index of flexlicusage loader	(flexlm_license_usage-%{yyyymm} in es).
