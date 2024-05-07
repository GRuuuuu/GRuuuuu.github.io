---
title: "호다닥 톺아보는 VectorDB 기초"
categories:
  - AI
tags:
  - ComputerScience
  - DataScience
last_modified_at: 2024-05-02T13:00:00+09:00
toc: true
author_profile: true
sitemap:
  changefreq: daily
  priority: 1.0
---

## Overview
지난 게시글에서는 [Vector란 무엇인가?](https://gruuuuu.github.io/ai/what-is-vector/)에 대해서 작성했었습니다.  

>데이터의 묶음은 여러의미의 데이터들로 이루어진 경우가 많은데, 이를 **특정한 순서대로 모아둔 데이터 레코드**를 선형대수에서는 **Vector**라고 부릅니다.  
>그리고 **행렬(Matrix)** 은 이러한 **벡터가 여러개 있는 데이터의 집합**이라고 생각하면 될 것 같습니다.  

Vector의 의미를 알았으니, 이제는 이 Vector를 어떻게 활용할 수 있는지 알아보겠습니다.  

## Embedding이란?

지난 게시글에서 Vector의 예시를 설명할때 plain text를 가지고 표현했었습니다. 하지만 사실 plain text는 인간이 알아보기 쉬운 표현법이지, 기계가 이해하기 쉬운 표현은 아닙니다.  

그래서 텍스트나 이미지같은 비정형 데이터를 기계가 잘 이해할 수 있게 고차원의 벡터 형태로 변환해주는 작업이 필요한데, 이를 **Embedding**이라고 합니다.

### One-Hot Encoding
예전에는 **One-Hot Encoding**이라는 기법을 통해 단어를 숫자벡터로 변환했었습니다.  

예를 들어 `I like rabbit and I hate coriander` 라는 문장을 벡터화한다면 먼저 단어단위로 분해하고(`I`, `like`, `rabbit`, `and`, `I`, `hate`, `coriander`)  
{ 'I' : 1, 'like' : 2, 'rabbit': 3, 'hate':4, 'coriander':5 }으로 정수를 부여하게 됩니다.  
이 과정을 정수 인코딩(Integer Encoding)이라고 합니다.  

>**정수 인코딩(Integer Encoding)**  
>단어를 빈도수 순으로 정렬한 단어집합(vocabulary)을 만들고 빈도수가 높은 순서대로 낮은 숫자부터 정수를 부여  

이렇게 정수를 부여하고 나서, 이를 one-hot vector로 나타내면 아래와 같이 표현할 수 있습니다.  

`I` : [1,0,0,0,0]  
`like` : [0,1,0,0,0]  
`rabbit` : [0,0,1,0,0]  
`hate` : [0,0,0,1,0]  
`coriander` : [0,0,0,0,1]  

이런식으로 간단하게 벡터화를 할 수 있지만, 단어의 개수가 늘어날수록 벡터를 저장하기 위한 공간이 계속 늘어나게 됩니다.  
예를 들어 단어가 10000개라면, 각각의 단어는 10000개의 차원을 가진 벡터가 되겠죠!  
**공간의 활용에 있어서 비효율적**이라는 단점이 있습니다.   

그리고 이렇게 표현하게 되면 단어의 존재는 쉽게 확인할 수 있지만, 각 **단어간 관계성을 파악하기 힘들다**는 단점도 존재합니다.  
특히 단어간 유사도가 중요한 검색시스템같은 환경에서는 큰 문제가 될 것입니다.  
(ex. one-hot vector에서는 book과 books는 서로 다른 단어로 취급)  

### Word Embedding
그래서 이를 보완하기 위해 **단어의 의미**를 다차원 공간에 벡터화하는 방법을 사용하기 시작합니다.  

이와 같이 단어간 의미적 유사성을 벡터화 하는 작업을 **워드 임베딩(Word Embedding)** 이라 부르고, 이렇게 표현된 벡터를 **임베딩 벡터(Embedding Vector)** 라고 부릅니다.  

**비슷한 문맥에서 등장하는 단어들은 비슷한 의미를 가질 것이다~** 라는 가설(Distributional Hypothesis)를 전제로, 비슷한 내용의 단어들을 벡터화 시키면 그 벡터들은 유사한 벡터값을 가지게 됩니다.  

이렇게 하면 **단어의 의미를 여러 차원에다 분산하여 표현할 수 있고, 단어벡터간 유의미한 유사도를 계산할 수 있게 됩니다.**  
>아래 예시에서 `고양이`와 `개`는 의미론적 관계를 반영해 서로 가깝지만 `행복`과 `슬픔`은 반대방향이므로 대조되는 의미임을 알 수 있습니다.  
>~~~
>고양이 [0.2, -0.4, 0.7]
>개 [0.6, 0.1, 0.5]
>사과 [0.8, -0.2, -0.3]
>오렌지 [0.7, -0.1, -0.6]
>행복 [-0.5, 0.9, 0.2]
>슬픔 [0.4, -0.7, -0.5]
>~~~  

그럼 이런 단어들을 어떻게 벡터화시키냐!  
바로 embedding vector를 만드는데 최적화된 모델인 **embedding model**을 사용하여 벡터화하게됩니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/1.png) 

사람이 embedding vector를 확인하고 의미를 파악하기는 어려우나, 서로 다른 단어나 문서로부터 추출된 **embedding vector들간의 거리를 계산하면 이들간의 의미적 관계를 파악**할 수 있습니다.  

또한 embedding model을 어떤걸 사용하느냐에 다라 embedding vector의 값과 차원이 다르게 표현됩니다.  
따라서 usecase에 맞게 embedding model을 선택하는 것도 중요합니다!   

>위에서는 텍스트만 예시로 들었지만, 이미지도 벡터화 시켜서 임베딩시킬 수 있습니다!   
>아래 이미지는 `mnist`(숫자손글씨 이미지세트)  
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/2.png)   
> - 색상 및 질감과 같은 이미지의 시각적 특징을 캡쳐
> - 모델이 이미지 분류나 객체 감지같은 컴퓨터 비전 작업을 수행할 수 있게 함  

이처럼 임베딩은 복잡한 패턴이나 관계를 효율적으로 계산하고 발견하는데 도움을 줍니다.  

## VectorDB란?
임베딩 모델을 통해서 나온 수백 수천 수만개의 벡터들... 방대한 양의 고차원 데이터를 벡터형태로 보관 & 쿼리하기 위한 Database의 필요성이 대두되기 시작했고, 그렇게 `VectorDB`가 탄생하게 되었습니다.  

한마디로 VectorDB는 **임베딩을 통해 생성된 고차원의 벡터 데이터들을 효율적으로 저장하고, 조회할 수 있도록 설계된 데이터베이스** 라고 보시면 됩니다.  

쿼리와 정확히 일치하는 행을 찾는 기존의 RDBMS와 다르게, **벡터간의 거리나 유사도를 기반으로 쿼리와 가장 유사한 벡터**를 찾습니다.  

수천개의 다차원 벡터사이 거리 메트릭을 비교하는 것은 시간이 많이 소요될 수 있기때문에 VectorDB는 정확도와 속도사이 균형을 유지하는 것이 중요합니다.  

아래 표는 VectorDB가 vector를 저장할 때의 과정을 도식화 한 장표입니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/3.png)  

### 1. Indexing
더 빠른 탐색을 가능하게 하는 자료구조로 벡터를 매핑하는 과정입니다.  
여러 `ANNS(Approximate Nearest Neighbors Search)알고리즘`을 활용합니다.  
기본 개념은 **정확한 결과보다 타겟과 유사한 값들을 검색하는 것**이라고 보시면 됩니다.  

몇가지 알고리즘을 간단히 소개하고 넘어가겠습니다.  

>**References :**  
>- [Pinecone/What is a Vector Database?](https://www.pinecone.io/learn/vector-database/)  
>- [Pinecone/Nearest Neighbor Indexes for Similarity Search](https://www.pinecone.io/learn/series/faiss/vector-indexes/)  
>- [Understanding similarity or semantic search and vector databases](https://medium.com/@sudhiryelikar/understanding-similarity-or-semantic-search-and-vector-databases-5f9a5ba98acb)

#### a. Flat Index (No Optimization)
별도의 Indexing 기법 없이 벡터를 저장하는 방법입니다.  

저장된 모든 벡터들과 유사도를 계산해 가장 높은 유사도를 지닌 벡터를 찾는 방법으로 검색하게 됩니다.  

일반적으로 10000~50000개 정도의 벡터에서 적당한 성능과 높은 정확성을 얻을 수 있는 방법이지만, 이보다 데이터가 많아진다면 속도가 느려진다고 합니다.  

#### b. Random Projection
랜덤한 벡터를 만들어 원래 벡터와 내적 -> 차원이 줄어들지만 원래 벡터와의 유사성은 유지할 수 있고 고차원의 원래 벡터보다 탐색속도가 빨라질 수 있습니다.  
다만 Approximation임을 명심해야 합니다.  

> 대체 어떻게 원 벡터와 내적시키면 차원이 줄어드는지 모르는 사람들을 위한 한장요약:   
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/4.png)  
>3차원상 노란점(1,2,3)을 2차원상의 파란 면에 정사영 시킨다고 했을 때의 예제입니다.  

#### c. PQ(Product Quantization)
원 벡터를 균등하게 몇 개의 서브 벡터로 쪼개고, 각 서브 벡터들을 Quantization하여 크기를 줄이는 방법입니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/5.png)  

빠르고 정확도도 좋으며 큰 데이터셋에서 사용하기 좋은 기법이라고 합니다.  

>**Quantization(양자화)란?**   
>일반적으로 Quantization이란 lower preciision bits로 매핑하는 것을 의미합니다.  
>예를 들어 우리가 소숫점을 표현할때에는 Float32의 경우, 총 32bit를 사용하고  
>이를 정수형인 Int8, 총 8bit로 표현한다면 그 경향은 비슷하겠지만 표현할 수 있는 숫자의 범위가 상대적으로 제한될 것입니다.  
>![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/6.png)  
>즉, 값을 표현하는데 사용하는 bit수를 줄임으로써 정확도는 다소 떨어지겠으나, 메모리 사용량을 절감시키고, 계산 소요 시간을 줄일수 있다는 장점이 있습니다.  

#### d. LSH(Locality-Sensitive Hashing)

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/7.png)  

벡터들을 Hashing함수에 한번 돌려서 Bucket에 매핑하는 기법입니다.  

유사도 검색을 할 때에도 쿼리문에 대한 벡터를 동일한 Hashing함수를 사용하여 같은 Bucket에 있는 벡터들하고만 비교하여 찾는 방식으로 동작합니다.  

전체 데이터와 비교하는 것이 아니라 Bucket에 있는 데이터들 사이에서만 찾기 때문에 빠르게 검색이 가능합니다.  

Bucket이 많을수록 좋은 결과를 낼 테지만, 더 많은 메모리가 필요할 것입니다.  

#### e. HNSW(Hierarchical Navigable Small World graph)
이름 그대로, 주어진 벡터들을 가지고 n개의 레이어를 가진 그래프를 생성합니다.  
각 벡터 엣지간 거리는 그 벡터들 사이의 유사도를 나타낸다고 보시면 됩니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/8.png)  

1. 최상위 레이어의 임의의 노드에서 탐색을 시작하고, 가장 가까운 노드로 이동
2. 현재 레이어에서 더 가까워질 수 없다면 하위 레이어로 이동
3. 모든 벡터가 존재하는 최하위 레이어에 도달할 때까지 반복
4. 쿼리 벡터와 유사도가 가장 높은 벡터 발견!  

레이어를 나눔으로써 검색 시 local minimum에 빠지는 것을 방지할 수 있고, 속도와 정확도도 높아 큰 데이터셋에서 쓰기 좋은 기법입니다.   

#### f. IVF (Inverted file index)

일반적으로 Inverted Index란 책 맨 뒤에 있는 색인을 생각하시면 됩니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/11.png)  

맨 처음에는 책의 개요와 목차가 있지만, 책 마지막에는 책에 나왔던 단어들의 리스트와 그 단어가 위치한 페이지를 확인할 수 있는 부분이 있죠!  

컴퓨터세상에서는 DB에 데이터를 저장할 때 데이터에서 테이블이나 raw data인 문서의 위치로의 매핑을 같이 저장하는 것을 Inverted Index 혹은 Inverted File이라고 부릅니다.  

VectorDB에서의 IVF알고리즘은 **Clustering** + **Inverted File** 이라고 보시면 됩니다.  

벡터들을 `K-means` 와 같은 Clustering 알고리즘을 통해 N개의 Cluster로 나누어, vector의 indexd와 각 cluster의 centroid id를 cluster별 **inverted list** 형태로 저장하게 됩니다.  

검색 쿼리가 주어지면, 그 쿼리가 포함되는 cluster를 찾고, 해당 cluster의 inverted list 내 벡터들에 대해 검색을 수행하게 됩니다.  

근데 쿼리 벡터가 클러스터에 가장자리에 존재한다면, 아래 사진과 같이 청록색 클러스터의 벡터가 더 가까움에도 불구하고 쿼리벡터가 위치한 빨간색 클러스터의 벡터들에서만 검색을 시도할 것입니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/12.png)  

이를 방지하기 위해 `nprobe`라는 파라미터를 도입했고, `nprobe`의 값에 따라 검색할 클러스터의 개수를 지정해줄 수 있습니다.  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/9.png)  
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-05-02-vector-store.md/10.png)  

`LSH`와 `HNSW`알고리즘과 마찬가지로 `IVF`도 검색할 공간을 줄여 검색 속도를 높이는 방법입니다.  
검색할 공간을 줄인다는 의미는, 모든 데이터를 확인하는 것이 아니라 일부만 확인하는 것이므로 검색속도와 정확도를 위해 파라미터 조정이 반드시 필요합니다.  

### 2. Querying
앞의 Indexing 알고리즘을 어떻게 하느냐에 따라 검색 방법이 달라집니다.  

Querying 단계에서는 검색 쿼리가 들어왔을 때, 설정한 Indexing 알고리즘에 따라 유사도 검색을 실행하는데   
이 때 유사도 검색을 어떤 방식으로 할것이냐! 를 결정하는 부분입니다.  

크게 세가지 방법이 있습니다.  

a. **Cosine Similarity** : 두 벡터간의 각도를 측정, -1~1사잇값으로 1에 가까울수록 유사한 벡터, -1에 가까울수록 정 반대의 벡터  
b. **Euclidean distance(L2)** : 두 벡터 사이의 직선거리, 0~무한대 사잇값으로 0에 가까울수록 유사한 벡터, 값이 커질수록 다른 벡터  
c. **Dot Product**(내적) : 두 벡터 사이의 내적, -∞에서 ∞사잇값으로 양수는 같은 방향, 음수는 반대방향

### 3. Filtering
마지막 Filtering단계에서는 결과값, 혹은 메타데이터의 필터링을 통해 원하는 결과값을 얻어내는 단계입니다.  

크게 두가지로 나뉩니다.  
a. **Pre-filtering** : Vector Search 이전에 수행, 탐색 공간을 줄이는 장점이 있지만, metadata filter 기준에 맞지 않은 결과는 무시될 수 있고 쿼리 프로세싱을 느리게 만들 수 있음   
b. **Post-filtering** : Vector search 이후에 수행, 모든 결과를 고려해 필터링할 수 있지만, 오버헤드로 쿼리프로세싱을 느리게 만들수있음  

## VectorDB 종류
지금까지 VectorDB의 기본적인 동작원리와 개념들에 대해서 알아봤습니다.  
