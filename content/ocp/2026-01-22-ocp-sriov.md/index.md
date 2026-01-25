---
title: "MultiNode LLM Workload를 위한 SR-IOV 네트워크 구성하기 (feat. Infiniband)"
tags:
  - Openshift
  - Networking
  - AI
date: 2026-01-23T13:00:00+09:00
---

## Overview
LLM이 산업계에 본격적으로 사용되기 시작한지도 벌써 몇년이 지났습니다.  
Hybrid Cloud의 중요성을 말하며, MSA 구조가 중요하다!라고 말한지 얼마되지 않았는데 이제는 거기에 LLM까지 들어오니 인프라의 중요성이 더욱 부각되는 것 같습니다.  

일반적인 Kubernetes의 워크로드와 LLM, 그것도 멀티노드 LLM 추론, 학습은 특히 네트워킹 부분에서 많은 차이점이 있습니다.  

이번 포스팅에서는 멀티노드 LLM 추론, 학습을 위한 네트워크 구성중 Infiniband SR-IOV를 활용한 네트워킹을 알아보겠습니다.  

## MultiNode LLM Workload
LLM workload는 상당히 복잡하고 많은 레이어를 통해 이뤄집니다.  

**Training**은 수십억개의 데이터를 모으고 정제한 뒤, 토큰화(Tokenization)하고 Transformer를 통해 다음 단어의 확률을 계산하고 예측과 정답의 차이를 구한 뒤, 역전파(Backpropagation)로 각 가중치의 기울기를 계산하여 업데이트합니다. 이 과정을 데이터 전체에 대해 수십-수백번 반복하게 되죠.  

**Inference**는 학습이 완료된 모델의 가중치를 그대로 사용해 새로운 입력에 대한 출력을 생합니다. 수십~수백억 파라미터를 가지고 있어 계산량은 여전히 많습니다.  

이렇게 복잡한 계산이 필요한 LLM workload를 최적의 성능을 내게 하려면 어떤 고려사항들이 있어야 할까요?  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-22-ocp-sriov.md/1.png)  

일반적인 **Kubernetes 워크로드**가 짧은 request/response로 이뤄지고, 각 pod가 독립적으로 동작하며 패킷을 주고받는 반면에,  

**LLM Inference**에서는 :  
- 길고 지속적인 **stream**
- GPU간 동기화된 **Collective Communication**(집단 통신) -NCCL(NVIDIA Collective Communications Library)
- GPU의 모든 스레드는 SIMT(Single Instruction Multiple Thread)형태로 처리되며 모든 스레드가 실행되고 다음 Instruction이 실행되는 **Lock-Step**으로 수행됨

또한 **LLM Training/Tuning**에서는:  
- 매 Step이 **All-Reduce** 기법으로 이뤄짐 (여러노드에서 계산한 값을 병합하고, 그 결과를 모든 노드에 전달됨)

상기 특징들을 갖고 있습니다.  

때문에 수십개의 패킷들이 왔다갔다 할텐데, 하나의 패킷이라도 늦게되면 전체 Step에 영향을 주게 됩니다.  
그래서 LLM workload에서는 네트워크의 Latency보다는 **Jitter**가 더 치명적입니다.  
하나의 노드라도 RTT(Rount Trip Time - 패킷의 왕복시간)가 튀게되면 다른 GPU들은 계속 idle상태로 놀게 되는것이죠. 그게 심해지면 NCCL Timeout에 걸려 전체 프로세스가 Fail될수도 있습니다.  

Inference에서는 네트워크가 불안정하면 성능이 나빠지는 문제이겠지만,  
Training/Tuning에서는 짧게는 몇시간~몇일의 Job이 아예 깨지는 문제가 될 수 있기때문에 네트워크를 주의해서 구성해야합니다.  

> **Latency vs Jitter**  
> `Latency` : 네트워크내에서 발생하는 지연, 하나의 엔드포인트에서 다른 엔드포인트로 이동하는데 걸리는 시간  
> `Jitter` : 네트워크에서 데이터 패킷의 전송 지연시간이 변동하는 현상. 패킷이 도착하는 시간이 일관되지 않고 불규칙함

정리하면 Kubernetes에서는 Ingress/Egress(North-South)가 중요하고 Service Mesh와 API중심이었지만,  
멀티노드 LLM 워크로드에서는 Pod to Pod. 즉, East-West 통신이 중요합니다.  

### on Kubernetes(Openshift)
자 그러면 이제 Kubernetes의 네트워크 구조에 대해서 생각해봅시다.  

기본적으로 Kubernetes는 pod들이 물리계층의 네트워크를 직접 관리하지 않고, **추상화된 Overlay 네트워크 계층 위에서 동작**합니다.  
Overlay네트워크 위에서 동작한다는 의미는... 실제 물리 네트워크의 MTU값과 오버레이 MTU값이 불일치하고, 캡슐화를 위한 헤더가 추가로 붙어 오버헤드를 일으킬 수 있다는 뜻이며... 즉 **Jitter를 일으킬 확률이 높아진다는 뜻**입니다.  

그래서 Kubernetes의 Pod들은 서로 Ip로 통신하며 Underlying network에 대해서는 신경쓰지 않아도 되었지만,   
MultiNode LLM workload의 경우엔 NIC종류, Switch Topology, RDMA capability 등 세부적인 네트워크 제어가 필요합니다.  

## SR-IOV

SR-IOV(Single Root I/O Virtualization)는 NIC 하드웨어의 Queue/Offload/DMA를 이용해 패킷 전송 경로에서 소프트웨어 레이어를 최소화하기 때문에 Latency나 Overhead, Jitter등을 크게 줄여줄 수 있습니다.  

따라서 LLM서빙처럼 네트워크 지연과 일관된 처리량이 중요한 경우에는 SR-IOV를 활성화하는 옵션을 생각해볼 수 있습니다.   

>참고 : [호다닥 톺아보는 네트워크 가상화(feat. DPDK, SR-IOV)](https://gruuuuu.hololy.org/linux/network-virtualization/)  


## Infiniband
Infiniband는 HPC환경에서 고속, 저지연 상호 연결을 위해 설계된 네트워크 상호 연결 기술입니다.  
최신 버전은 최대 400Gbps의 속도를 지원하기때문에 고속네트워크를 필요로 하는 MultiNode LLM workload에는 필수라고 할 수 있겠습니다.  

>그러나 Infiniband는 Mellanox를 NVIDIA가 인수하면서 경쟁이 사라진 독점기술이고 고가의 가격때문에 쉽사리 도입하기 쉽진 않습니다.  
>그리고 예전에는 Ethernet보다 Infiniband가 월등하게 성능이 좋았기 때문에 장점이 있었지만, 요새는 Ethernet의 대역폭도 Infiniband 못지않게 올랐기 때문에 굳이 고가의, 벤더종속성이 심한 Infiniband를 왜 사용하냐는 말들도 나오고 있기도 합니다.  

### RDMA(Remote Direct Memory Access)
그럼 이제 Infiniband를 분산컴퓨팅의 강자로 만들게 한 RDMA라는 기술에 대해서 알아보도록 하겠습니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/refs/heads/main/2026/2026-01-22-ocp-sriov.md/2.png)  

**RDMA(Remote Direct Memory Access)** 는 OS나 CPU의 개입 없이 한 서버의 메모리에서 다른 서버의 메모리로 데이터를 직접 전송하는 기술입니다.  
이는 데이터 복사 과정을 제거하고(**zero-copy**), 커널영역을 우회하여(**Kernel-Bypass**) 성능을 극대화시킬 수 있다는 뜻입니다.  
위에서 언급했듯이, 이는 MultiNode LLM Workload에서 반드시 필요한 부분이죠!   

당연히 수신/송신측의 NIC가 모두 RDMA를 지원해야 가능한 통신기법이긴합니다.  

>**RoCE(RDMA over Converged Ethernet)**  
>RDMA를 Ethernet환경에서도 사용할 수 있게 하는 프로토콜

## Infiniband 네트워크 구성하기 - Openshift
그럼 드디어! Infiniband를 SR-IOV로 Openshift의 서브 네트워크를 구성하여 pod끼리 RDMA통신 실습을 해보겠습니다.  

