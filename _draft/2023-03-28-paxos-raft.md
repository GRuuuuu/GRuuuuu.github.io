---
title: "호다닥 톺아보는 합의 알고리즘 : PAXOS, RAFT"
categories: 
  - Integration
tags:
  - Distributed
  - Consensus
  - Algorithm
last_modified_at: 2023-03-28T13:00:00+09:00
author_profile: true
toc: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Distributed System과 Consensus Algorithm
(사진)   
싱글 컴퓨터로는 성능의 향상에 있어 제한이 있습니다. 만약 해당 컴퓨터에 장애가 발생한다고 한다면 꼼짝없이 돌아가던 서비스도 멈추게 될거고요.  

그래서 복잡한 연산을 여러 컴퓨터가 나눠서 수행하고, 하나의 컴퓨터가 망가지더라도 나머지 컴퓨터가 맡아서 처리할 수 있는 분산 환경(**Distributed System**)이 등장하게 됩니다.  

하지만 결국 여러 컴퓨터가 하나의 시스템처럼 동작하려면, 누구하나 어긋남 없이 하나의 상태를 가져야 합니다.  
이런 문제를 해결하기 위해 분산 환경에서 상태를 공유하는 알고리즘이 등장했고, 이를 **Consensus Algorithm**이라고 부릅니다.  

### Fail-Stop과 Byzantine Failure
분산 환경에서 발생할 수 있는 장애는 무궁무진하지만 이 문서에서는 합의와 관련된 부분만 다루도록 하겠습니다.  

크게 두가지 종류가 있습니다.  
- `Fail-Stop` : 단순히 노드가 고장나서 **멈추는 형태**
- `Byzantine Failure` : 고장나서 멈추는 것을 넘어서서 노드가 악의적인 행동을 포함한 **임의의 동작**을 할 수 있다는 문제

**Fail-Stop**형태의 장애를 가정한 대표적인 합의 알고리즘으로는 `Paxos`와 `Raft`가 있고,   
**Byzantine Failure**를 가정한 대표적인 합의 알고리즘으로는 `PBFT`가 있습니다.  

이 문서에서는 `Paxos`와 `Raft`에 대해서 알아보도록 하겠습니다.  

## Paxos
Paxos 알고리즘은 1989년에 처음 공개되었으며 그리스의 팩소스 섬에서 가상의 입법 합의 시스템에 사용된 후 이름지어졌습니다.  

분산 시스템에서 **여러 프로세스 간에 하나의 값에 동의하기 위한 프로토콜**로서, 동시에 여러 개의 값이 제안되지만,  
결국에는 이 중 **하나의 값이 선택**되도록 하는 것이 골자입니다.  
하지만 여러 제안자에 의해 동시에 여러 값의 후보가 제안될 수 있다는 점 때문에 프로토콜의 동작이 복잡해 구현이 어렵다는 단점이 있습니다.  

사실 글을 쓰는 저도 100% 이해했다고 말하긴 어렵지만, 아래 영상을 보고 제가 이해한 내용을 최대한 쉽게 풀어써보고자 합니다.  
> 참고한 영상 : [Google TechTalks: The Paxos Algorithm](https://youtu.be/d7nAGI_NZPk)  

### Overview
(사진)  
1. Paxos알고리즘은 총 세개의 역할을 정의합니다.  
    - `Proposer` : 특정 값을 제안함
    - `Accepter` : `Proposer`에게 온 값들중에 하나를 선택함  
    - `Learner` : `Accepter`에 의해 합의된 값을 전달받음 
2. 각 paxos 노드는 과반수의 `Accepter`개수를 알고있음 (`Accepter`가 3이면 과반은 2, 과반이 동의하면 나머지 하나의 의견은 묵살)
3. `Accepter`들은 한번 특정 값을 받아들이게 되면 (다수의 `Accepter`가 동의해서 commit이 되면) 그 값은 변하지 않는다 (`Proposer`가 새로운 값을 제안해도 무시함)  
4. **Paxos알고리즘의 목표는 단 하나의 consensus를 이루는 것!**  

### Basic Paxos
그럼 실제로 Paxos알고리즘을 통해 어떤식으로 합의가 이루어지는지 보도록 하겠습니다.  

#### Proposer가 1개일 경우

(사진)  

1. **PREPARE** : `Proposer`가 어떤 값을 제안하기 위해 제안번호(ID)를 먼저 `Accepter`들한테 보냄
2. **PROMISE** : `Accepter`는 제안한 번호(ID)이하의 값을 받지 않겠다고 약속 (ex. 5가오면 5이하의 숫자는 무시됨)  

(사진)  

3. **ACCEPT** : 다수의 `Accepter`가 동일한 ID의 **PROMISE**메세지를 `Proposer`에게 보냈다면 `Proposer`는 해당 ID와 VALUE를 `Accepter`에게 보냄   

(사진)  

4. **ACCEPTED** : `Accepter`는 메세지(ID,VALUE)를 받고 ID가 마지막으로 약속한 값인 경우에만 VALUE를 받아들이고 VALUE를 `Proposer`와 `Learner`에게 전파한다
만약 마지막으로 약속한 값이 아닐경우 `Accepter`는 메세지를 무시할 수 있고, 거절응답을 P에게 보낼 수 있음
5. 합의완료

#### Proposer가 여러개일 경우
만약 다른 `Proposer`가 network latency등의 이유로 합의된 값을 받지 못하고 새로 제안했을 경우  

(사진)  

1. `Proposer2`는 제안번호4를 `Accepter`에게 보냄
2. 하지만 이미 `Accepter`는 제안번호5를 승인한 전적이 있음 -> 4<5이므로 reject  

(사진)

3. `Proposer2`는 더 높은 제안번호 6을 보냄 
4. `Accepter`는 5보다 더 높은 제안번호인 6을 승인함
5. 이미 이전에 5,cat이라는 제안을 합의했기때문에 `Accepter`는 새로받은 제안번호에 합의했던 value인 cat을 붙여서 약속 메세지를 보냄
6. `Proposer2`는 받은 value와 승인된 제안번호와 함께 ACCEPT REQUEST를 보냄

(사진)  

7. `Accepter`는 요청을 보고 이미 위에서 합의된 value가 아니라면 무시/거절, 합의된게 맞다면 value 전파


그래서 한장으로 정리하면 아래와 같은 도식이 그려지게 됩니다.  
(사진)  
>Image from "[Google TechTalks: The Paxos Algorithm](https://youtu.be/d7nAGI_NZPk)"

이 외에도 여러 if시나리오가 있지만, 이 문서에서는 그렇게 deep하게 다루지는 않을 생각입니다.  
관심이 있으신 분들은 아래 링크를 참조해주시기 바랍니다!   
>참고링크  
>- [paxos wiki](https://ko.wikipedia.org/wiki/%ED%8C%A9%EC%86%8C%EC%8A%A4_(%EC%BB%B4%ED%93%A8%ED%84%B0_%EA%B3%BC%ED%95%99))  
>- [ETRI - Blockchain and Consensus Algorithm](https://ettrends.etri.re.kr/ettrends/169/0905169005/0905169005.html#!po=56.2500)  
>- [Google TechTalks: The Paxos Algorithm](https://youtu.be/d7nAGI_NZPk)  

## Raft
위의 Paxos알고리즘을 보시면 아시겠지만 한 번 합의를 이루는 절차가 꽤나 복잡합니다.  
절차가 복잡하니 이해가 어렵고 구현이 어려워, 실제로 Paxos를 구현한 라이브러리가 거의 없었고 일부 분산 시스템이 내부적으로 사용하는 정도 였다고 합니다.  

하지만 분산 시스템이 주류가 되고 있는 요즈음, 더욱 알기 쉽고 구현하기 쉬운 합의 알고리즘에 대한 요구사항은 높아져왔고  

2014년 USENIX에서 "In Search of an Understandable Consensus Algorithm"라는 논문이 발표되고 **Raft**라는 알고리즘이 등장하게 됩니다.  

Raft는 논문 제목에서 알 수 있듯이 "이해 가능한" 합의 알고리즘을 만드는 데 초점을 두고 있습니다.  

> 논문의 저자들은 Paxos와 Raft중 어떤게 더 이해하기 쉽고 구현하기 쉽겠느냐고 스탠포드대학 컴퓨터공학과 학생들에게 survey를 진행했고, 결과는 다음과 같았다고 한다..!!!   
>(사진)  

그럼 지금부터 Paxos와 동일한 결과와 효율성을 지니고 있지만 구조(방법)는 Paxos와 다른! Raft 알고리즘에 대해 알아보도록 하겠습니다.  

### 상태
Raft알고리즘 상에서 분산 시스템의 모든 노드들은 세가지 상태 중 하나를 가지게 됩니다.  
- `Leader` : 리더는 클라이언트의 모든 요청을 수신받고, 로컬에 로그를 적재하고 모든follwer에게 전달
- `Follwer` : 클라이언트로 받은 요청을 리더로 redirect 시켜주고, 리더의 요청을 수신하여 처리하는 역할
- `Candidate` : 새로운 리더를 선출하기 위해 후보가 된 상태

Paxos에서 각 노드가 역할이 정해져있었던 것과 다르게 Raft에서는 상태만 변할 뿐이지 고정된 역할이 없습니다.  

### 1. 리더 선출(Leader Election)
분산 시스템에서 각 노드들은 내부적으로 임기를 가지고 있습니다.  
대통령 선거하듯이 1대, 2대 이런식으로요.  

(사진)  
리더로 선출된 노드는 주기적으로 비어있는 `AppendEntries`라는 RPC프로토콜을 사용해 follower들에게 자신이 살아있다는 것을 알립니다.  
(새로운 엔트리를 follower에게 전파할때도 동일한 프로토콜 사용)  

(사진)  

각 노드는 150ms~300ms 사이의 랜덤하게 할당된 타임아웃 시간이 존재하고,  
follower는 특정 시간동안 리더한테서의 신호를 받지 못하면 자신이 리더가 되기위해 반란을 일으킵니다.   

(사진)  

1. 저장된 임기번호(term)을 1증가시키고 새로운 선거를 진행
2. 본인이 스스로 후보(candidate)가 되어 자신에게 투표를 진행하고 다른 follower들에게 투표요청 `RequestVote` RPC 프로토콜을 사용해 함수를 호출한다

그렇게 투표가 시작되면 아래 세가지 결과중 하나를 얻게 됩니다.   
1. 과반수의 투표를 얻어 리더로 당선
2. 동일한 시점에 후보가 된 다른 노드가 리더가 됨 -> 리더가 되지못한 candidate는 follower로 상태를 변경하고 새로운리더를 등록함
3. 승자 없이 투표종료(동률이거나 모든 노드가 자신에게 투표했을 경우 발생) -> 이경우 임기를 1증가시키고 다시 투표요청

### 2. 로그 복제(Log Replication)
리더가 정해지고 나서는 시스템의 모든 변경사항이 리더를 통하게 됩니다.   
각 변경사항은 로그엔트리(log Entries)에 저장되고 다른 follower들에게 복제됩니다.  

**로그 엔트리**
- Term : 임기
- Index : log 저장할때의 번호 (1부터시작함)
- Data

(사진)  

1. 클라이언트가 리더에게 변경사항을 보냄
2. 변경사항은 리더의 로그엔트리에 저장됨

(사진)

3. `AppendEntries` RPC를 호출해서 log를 전달
4. Follower는 새로받은 로그를 저장하고 성공 응답을 보냄  
>
>**AppendEntries RPC Arguments:**
>~~~
>term: 현재 leader의 임기
>leaderId : leader id
>prevLogIndex : 바로 이전의 log index
>prevLogTerm : 바로 이전의 log index에 기록된 임기(term)
>entries[] : 저장할 로그 엔트리 (비어있으면 heartbeat용)
>leaderCommit : 현재 leader의 commitIndex
>~~~
>
>#### `AppendEntries` **상세 동작 순서:**  
>1. Follower가 갖고 있는 현재임기(`currentTerm`)보다 전달받은 `term`이 낮으면(`term`<`currentTerm`) -> **return false**
>2. 전달받은 `prevLogIndex`에 해당하는 엔트리가 없다면 -> **return false** (ex. leader의 index는 3인데 복사하려는 follower의 index가 1이어서 `prevLogIndex`인 2에 해당하는 entry가 없는 경우)
>3. 이미 존재하는 엔트리가 새로운 엔트리와 충돌이 발생할 경우(같은index지만 다른term일 경우) -> **기존 엔트리 삭제**
>4. **새로운 엔트리를 추가**
>5. "새로 추가된 엔트리의 index"와 "leader의 commitIndex"중 작은 값을 follower의 commitIndex에 set

(사진)

5. 과반수 follower의 응답을 받았으면 리더는 자신의 로그엔트리를 커밋하고 클라이언트에 응답을 보냄
6. follower들한테도 변경사항이 커밋되었음을 알림 -> follower들 자신의 로그엔트리 커밋  


### Leader Completeness 
아래 사진의 경우에서는  
(사진)  
과반수의 노드(여기선 3개의 노드)에 복제되었으므로 커밋된 것으로 간주하고, 이를 **Committed Entries**(여기서는 7)라고 칭합니다.   

한 번 커밋된 엔트리는 다음 임기의 리더들에게 반드시 포함될 것을 보장하는데, 이를 **Leader Completeness**라고 합니다.  

이게 어떻게 보장될 수 있을까요?

다시한번 `AppendEntries`의 동작을 되짚어보겠습니다.  

리더는 새로운 엔트리를 다른 서버로 전파할 때 `AppendEntries` RPC를 호출합니다.  
문제 없이 성공한다면 로그엔트리를 복사하고, 실패한다면 인덱스 값을 1씩 감소시켜서 성공할 때까지 반복하고 성공한다면 로그를 복사합니다.  

그것을 과반수의 follower들에게 전파를 성공한다면 위에 언급한 것처럼 commit을 하게 됩니다.  

여기서 살펴봐야 할 것은 두가지 입니다.     
1. **Election Restriction**  
    - Candidate는 Leader가 되려면 **과반수** 노드의 투표가 있어야 함
    - `RequestVote` RPC에는 Candidate의 마지막 로그의 index와 term이 파라미터로 포함되어있는데, 요청을 받은 투표자(Follower)의 index나 term이 더 높으면 요청을 거절함
2. **Commit Rules**
    - Raft에서는 반드시 **현재 임기의 로그**가 복제되어야만 커밋으로 간주한다.  

#### 어디선가 새로운 리더가 등장?
(사진)  
> 박스안의 숫자는 임기를 의미합니다.   

노드1~4번은 
네트워크의 단절등의 이유로 5번노드가 분리되어서













7. 5.4.3 Safety argument
Given the complete Raft algorithm, we can now argue more precisely that the Leader Completeness Property holds (this argument is based on the safety proof; see Section 8.2). We assume that the Leader Completeness Property does not hold, then we prove a contradiction. 

Suppose the leader for term T (leaderT) commits a log entry from its term, but that log entry is not stored by the leader of some future term. Consider the smallest term U > T whose leader (leaderU) does not store the entry.

1. The committed entry must have been absent from leaderU’s log at the time of its election (leaders never delete or overwrite entries).

2. leaderT replicated the entry on a majority of the cluster, and leaderU received votes from a majority of the cluster. 
Thus, at least one server (“the voter”) both accepted the entry from leaderT and voted for leaderU, as shown in Figure 9. The voter is key to reaching a contradiction. 

3. The voter must have accepted the committed entry from leaderT before voting for leaderU; otherwise it would have rejected the AppendEntries request from leaderT (its current term would have been higher than T).

4. The voter still store larger than the voter’s. Moreover, it was larger than T, since the voter’s last log term was at least T (it contains the committed entry from term T). The earlier leader that created leaderU’s last log entry must have contained the committed entry in its log (by assumption). Then, by the Log Matching Property, leaderU’s log must also contain the committed entry, which is a contradiction.

8. This completes the contradiction. Thus, the leaders of all terms greater than T must contain all entries from term T that are committed in term T.

9. The Log Matching Property guarantees that future leaders will also contain entries that are committed indirectly, such as index 2 in Figure 8(d).
Given the Leader Completeness Property, it is easy to prove the State Machine Safety Property from Figure 3 and that all state machines apply the same log entries in the same order (see [29]).