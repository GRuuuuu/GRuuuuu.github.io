---
title: "GPU Basics -동작원리와 사용하는 이유에 대해서"
slug: gpu-basics
tags:
  - GPU
  - DataScience
date: 2024-02-05T13:00:00+09:00
---

## Overview
최근 몇 년 간, 천정부지로 치솟은 GPU제조사 NVIDIA의 주식... 그리고 그래픽카드의 되팔이와 끝도없이 높아진 가격들을 지켜보며  
대체 왜? GPU가 어떤 역할을 하기에 코인 채굴이나 AI 연구에 빠질 수 없는 컴포넌트가 된 것일까?? 궁금해했습니다.  

공부해야지 생각만 하다가 최근 동작원리에 대해서 너무나 잘 설명한 영상을 봐서 그 내용을 요약 정리 하려고 합니다.  

Youtube Link : [bRd 3D/GPU는 어떻게 작동할까](https://youtu.be/ZdITviTD3VM?si=a5EvQ969z81ZMPTN)


## GPU의 탄생
GPU(Graphic Processing Unit)
- 컴퓨터 시스템에서 그래픽연산을 빠르게 처리하여 결과값을 모니터에 출력하는 연산장치
- 1980년대 첫 등장

## CPU와 GPU의 차이

- 둘 다 중요한 컴퓨팅 엔진이고, 데이터를 처리한다는 점에서 비슷함
- CPU는 여러 개의 고성능 프로세싱 코어를 갖고 있으며 **복잡한 연산을 빠르게** 처리하도록 설계됨
- 반면 GPU는 수천개의 성능이 높지 않은 프로세싱 코어를 갖고 있으며 **단순하지만 많은 연산**을 수행하도록 설계
- 예를 들어 수백개의 단순한 연산을 초등학생 100명과 1명의 공학박사가 해결한다고 생각하면됨

![1](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/1.png)  

## 그래픽 연산이란?
알다시피 CPU는 컴퓨터의 핵심 엔진이며 고성능의 프로세싱 코어를 갖고 있습니다.  
그러나 단순 계산에 특화된 GPU가 대체 왜 사용되는 것일까요?  

일단 GPU가 탄생하게 된 그 배경에서부터 알아봐야 할 것 같습니다.  
이름에서 알 수 있듯이 GPU는 그래픽 연산에 특화되어 그 결과값을 모니터에 출력하는 역할을 합니다.  

그렇다면 그래픽 연산이란 무엇일까요?  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/2.jpg)   

모니터에 뿌려지는 이미지들은 Pixel이라는 작은 점들로 이루어져 있습니다.  
현재 가장 범용적으로 사용되는 해상도인 1920x1080의 Pixel 수는 200만개 정도 입니다.  

동영상의 경우는 Pixel들이 모인 이미지가 빠르게 표시되는데 이 때의 이미지들을 Frame이라고 부릅니다.  

1초에 30프레임이면 컴퓨터가 1초에 계산해야하는 Pixel의 개수는 6000만개정도가 되겠죠!  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/3.png)   
물론 이 계산을 CPU가 처리해 줄 수도 있겠지만, 효율적이지 않습니다.  
수백 수천만개의 단순 연산을 몇 개의 고성능 코어로 돌리게 되기 때문에 정말 빠르게 처리해야하는 중요한 작업들이 딜레이될 수도 있습니다.  

3D그래픽은 어떨까요?   

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/4.jpg)   

이 경우 조금 더 복잡한 연산이 들어가게 되는데, 하나의 정점데이터에는 좌표값(position), 방향(normal), 이미지 좌표(texture coordinate) 등 여러 정보가 포함됩니다.  

거기다 게임같은 경우 실시간으로 3D모델이 끊임없이 움직이게 될 것입니다.  
그러므로 계속해서 변하는 정점 데이터를 계산해줘야 합니다!  

이 연산은 여러 정보가 포함된 데이터, 즉 **행렬**의 형태로 나타나게 되고,  
이는 행렬의 곱셈 형태로 실시간 계산이 되게 됩니다.  

## 대량 데이터 처리가 빠른 GPU
![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/5.png)     
위 그림은 CPU와 GPU의 구조를 개략적으로 나타낸 그림입니다.  
CPU에서 논리 연산을 수행하는 장치를 ALU(Arithmetic Logic Unit, 산술 논리 연산 장치)라고 부르는데, 요놈이 많을 수록 동시에 계산할 수 있는 수가 많아집니다.  

CPU같은 경우는 복잡한 수식을 처리하거나 명령어 하나로 계산여러개를 한꺼번에 한다거나 각종 제어처리를 위한 부분이 많습니다.  

반면 GPU는 독립적인 연산 여러개를 빠르게 수행하기 위해 이런 부분을 삭제하고 수천개의 ALU를 가지고 있습니다.  

GPU에서는 순차적인 계산(A->A'->A'')을 처리하는데에는 효율이 떨어지고(나머지 코어들이 놀고 있기 때문), **서로 독립적인 대량의 데이터를 처리**할 때 매우 효과적인 특성을 갖고 있습니다.  

## OpenCL vs CUDA
사람들은 이러한 특성을 사용하여 그래픽 처리뿐만 아니라 다른 영역에도 적용해보자! 라고 고민하기 시작했습니다.  

그러나 그래픽이 처리되는 방식으로 데이터를 처리하려니 바꿔줘야하는 부분들이 있고,  
행렬연산이 일반적인 계산에 적합하지 않을 때가 있기 때문에 
`OpenCL`이나 `CUDA`같은 언어가 등장했습니다.  

**OpenCL vs CUDA**  
- 기능 비슷, 코딩스타일도 C와 비슷
- `OpenCL`은 NVIDIA, AMD 모두 동작가능, CPU에서 디버깅도 가능
- `CUDA`는 NVIDIA GPU에서만 사용가능  

## GPU가 데이터를 처리하는 방식
GPU가 독립적인 대량의 데이터를 처리하는데 특화된 녀석이라는 것을 알았으니, 이제는 실제로 데이터가 어떻게 처리되는지 알아보겠습니다.  

GPU의 코어 하나는 한 번에 하나의 스레드를 처리할 수 있습니다.  
그렇다면 스레드의 개수만큼 코어가 존재하는것이 이상적일 것입니다.  
하지만 현실적으로는 불가능에 가깝죠!   

1000000개의 스레드가 있다고 생각해봅시다.  
우리가 가진 GPU의 코어는 1000개이구요.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/7.png)     
스레드를 1000개의 묶음으로 묶으면 한 묶음에 1000개의 스레드가 있을 것이고,  
코어를 10개씩 묶으면 하나에 100개의 코어가 존재할 것입니다.  

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/8.png)     
또 이 스레드 묶음에서 100개씩 묶어준다면 100개의 코어에서 한 번에 처리가 가능해집니다.  
이때의 단위를 Nvidia에서는 `Warp`, AMD에서는 `Wavefront`라고 부릅니다.  

`Warp`&`Wavefront`는 같은 명령어로 동시에 동작 가능한 스레드의 집합을 의미하고, 이런 동작을 **Single Instruction Multi Thread**(SIMT)라고 부릅니다.  

## ML, Blockchain

![](https://raw.githubusercontent.com/GRuuuuu/hololy-img-repo/main/2024/2024-02-05-gpu-basics.md/6.png)     
머신러닝에서는 대량의 데이터가 입력되고 연산되어 값을 도출하는데,  
이는 곱하기와 더하기를 반복하는 단순 계산들이어서 GPU를 활용하기에 좋습니다.  

또한 비트코인의 채굴방식도 정해진 해시값이 나올 때까지 임의의 숫자를 더하는 단순계산이므로 GPU를 활용하면 연산속도가 높아지게 됩니다.  

----