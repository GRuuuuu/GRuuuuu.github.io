---
title: "[Quantum for Developers] 양자 게이트"
categories: 
  - Quantum Computing
tags:
  - Quantum
  - Computing
  - Physics
last_modified_at: 2019-10-29T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Overview
지난 글에서 양자의 특징을 배웠으니 이제 그걸가지고 유의미한 결과를 만들어내려면 기존 컴퓨터에서 사용하던 논리게이트와 유사한 **양자게이트**를 사용할 줄 알아야 합니다.   

> [[Quantum for Developers] Quantum의 특징](https://gruuuuu.github.io/quantum%20computing/quantum/)  

그래서 이번 글에서는 대표적인 양자게이트를 소개하도록 하겠습니다.  

> **[참고문헌]**  
> [SNUON_컴퓨터과학이 여는 세계_12.2 양자현상을 수학으로 표현하기_이광근](https://youtu.be/QAtGLcualF4)  
> [Wiki : Quantum logic gate](https://en.wikipedia.org/wiki/Quantum_logic_gate)  
> [IBM Q Experience : Introduction to Quantum Circuits](https://quantum-computing.ibm.com/support/guides/introduction-to-quantum-circuits?page=5cae6f7735dafb4c01214bbe#the-pauli-operators)



# Quantum Bit
게이트에 대해서 말하기 전에, 퀀텀비트 줄여서 **Qubit**라고 부르는 비트에 대해서 짚고 넘어가도록 하겠습니다.  

## Notation
기존의 bit는 0과 1로 표기할 수 있지만 Qubit의 표기는 약간 다릅니다.  

앞전 포스팅에서 언급했던 중첩때문에 Qubit의 상태는 0이다 1이다로 표현할 수 없습니다.  

![image](https://user-images.githubusercontent.com/15958325/67742442-65e73880-fa5f-11e9-85b9-4a0f8a1f3670.png)    

그래서 추상적인 벡터와 선형 범함수를 표현하는 데 사용하는 `ket-vector`를 표준 표기법으로 사용합니다.  

> 확률이 $$\alpha^{2}$$일때, 0인 상태 : $$ \alpha \vert \mathsf{0}\rangle $$     
> 확률이 $$\beta^{2}$$일때, 1인 상태 : $$ \beta \vert \mathsf{1}\rangle $$

bar($$ \vert $$)와 꺽쇠($$\rangle$$)기호를 사용하여 표기합니다.  

그래서 하나의 Qubit 상태는 다음과 같이 표현될 수 있습니다.  

$$ \vert\psi_{양자}\rangle=\alpha \vert \mathsf{0}\rangle+\beta \vert \mathsf{1}\rangle $$  

행렬로 나타내면 다음과 같이 표현될 수 있습니다.  

$$ \left[\begin{array}{cc} \alpha \\ \beta \end{array}\right] $$  

마찬가지로 두개의 Qubit(A,B)의 상태도 다음과 같이 나타낼 수 있습니다.  

$$ \vert AB \rangle=\upsilon_{00} \vert 00\rangle+\upsilon_{01}\vert01\rangle+\upsilon_{10}\vert10\rangle+\upsilon_{11}\vert11\rangle \rightarrow \left[\begin{array}{cc} \upsilon_{00} \\ \upsilon_{01} \\ \upsilon_{10}\\ \upsilon_{11} \end{array}\right] $$  

## Probability
다시 Qubit 하나를 봅시다.  
$$ \alpha \vert \mathsf{0}\rangle+\beta \vert \mathsf{1}\rangle $$  

$\alpha$ 는 다음과 같이 나타낼 수 있습니다.  

$$\alpha = x+yi$$  
이때 i는 복소수입니다. 
>복소수는 제곱했을때 -1이 되는 수    

앞전 문서에서 음의 확률도 있다고 언급했었는데 정확히는 음의 방향

그래서 0이 나타날 확률 :  
$$\alpha^{2}=(x+yi)^{2}=(x-yi)^{2}=x^{2}+y^{2}$$  
이렇게 됩니다.  




# Quantum gate
## Pauli gate

Qubit를 그림으로 나타내면 위 사진과 같이 벡터로 표현될 수 있습니다.  

너무 어렵게 생각하지 마시고 0과 1이 나올 수 있는 확률은 방향을 가지고 있다고 생각하시면 됩니다.  

파울리 X,Y,Z게이트는 Qubit를 X축 Y축 Z축으로 회전시키는 게이트 입니다.

### Pauli-X gate
고전 컴퓨터에서의 Not Gate역할을 하는 게이트입니다.  

>**양자게이트 :**   
>
>![image](https://user-images.githubusercontent.com/15958325/67742215-c4f87d80-fa5e-11e9-8148-5ac322bd0544.png)

행렬식 :  
$$ X = \left[\begin{array}{cc} 
0 & 1\\ 
1 & 0 
\end{array}\right
]$$

$$  $$