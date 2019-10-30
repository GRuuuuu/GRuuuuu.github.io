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

> 확률진폭이 $$\alpha$$일때, 0인 상태 : $$ \alpha \vert \mathsf{0}\rangle $$     
> 확률진폭이 $$\beta$$일때, 1인 상태 : $$ \beta \vert \mathsf{1}\rangle $$

bar($$ \vert $$)와 꺽쇠($$\rangle$$)기호를 사용하여 표기합니다.  

그래서 하나의 Qubit 상태는 다음과 같이 표현될 수 있습니다.  

$$ \vert\psi_{양자}\rangle=\alpha \vert \mathsf{0}\rangle+\beta \vert \mathsf{1}\rangle $$  

행렬로 나타내면 다음과 같이 표현될 수 있습니다.  

$$ \left[\begin{array}{cc} \alpha \\ \beta \end{array}\right] $$  

마찬가지로 두개의 Qubit(A,B)의 상태도 다음과 같이 나타낼 수 있습니다.  

$$ \vert AB \rangle=\upsilon_{00} \vert 00\rangle+\upsilon_{01}\vert01\rangle+\upsilon_{10}\vert10\rangle+\upsilon_{11}\vert11\rangle \rightarrow \left[\begin{array}{cc} \upsilon_{00} \\ \upsilon_{01} \\ \upsilon_{10}\\ \upsilon_{11} \end{array}\right] $$  

## Probability Amplitude
위에서 확률진폭이라는 단어가 등장했죠? 여기에 대해서 잠시 짚고 넘어가겠습니다.  

양자역학에서의 확률진폭은 제곱이 확률 밀도인 복소수 스칼라 물리량입니다.  
다시 말해서 **확률진폭^2=확률** 입니다.   

그런데 이 확률진폭은 **복소수**(제곱했을때 -1이 되는 수)의 형태로 나타납니다.  
이말인 즉슨, **확률이 마이너스**가 될 수 있다는 뜻이죠.  

> Why  
>왜 확률은 확률진폭의 제곱인지, 확률진폭은 복소수의 형태로 나타나는지는 양자가 파동성을 갖고 있기 때문이라고 합니다. >>잘모름<<

다시 Qubit 하나를 봅시다.  
$$ \alpha \vert \mathsf{0}\rangle+\beta \vert \mathsf{1}\rangle $$  

확률진폭 $\alpha$ 는 다음과 같이 나타낼 수 있습니다.  
$$\alpha = x+yi$$  
이때 $i$는 복소수입니다. 

그래서 0이 나타날 확률은 $\alpha$의 제곱이 될거고 다음과 같이 표현될 수 있습니다.  
$$\alpha^{2}=(x+yi)^{2}=(x-yi)^{2}=x^{2}+y^{2}$$  

또한 확률이기 때문에 $\alpha$와 $\beta$의 합은 1입니다.  

----

이것만 보면 잘 이해가 안되니 예를 들어서 보겠습니다.  

하나의 Qubit의 상태가 다음과 같다고 할 때 :  
$$ r_{0}\vert0\rangle+r_{1}\vert1\rangle $$  

$r_{0}$과 $r_{1}$을 다음과 같이 정의 :  
$$ r_{0} = 0.3+0.3i $$  
$$ r_{1} = 0.9+0.1i $$  

그러면 0이 나타날 확률은 $r_{0}$의 제곱이고, 1이 나타날 확률도 $r_{1}$의 제곱입니다.  

$$ \Vert r_{0} \Vert^{2}= 0.3^{2}+0.3^{2}=0.18$$  
$$ \Vert r_{1} \Vert^{2}= 0.9^{2}+0.1^{2}=0.82$$  

이렇게 되면 1이 나올 확률(82%)이 훨씬 크니 1이 자주 보이겠죠?  

또한 확률의 합도 1!  
$$ \Vert r_{0} \Vert^{2}+\Vert r_{1} \Vert^{2}=1 $$

>정리하면)  
>- 확률진폭^2=확률
>- 확률진폭은 복소수 -> 음의 확률 가능
>- 확률의 합은 1

# Quantum gate
지금부터 대표적인 양자게이트 몇가지를 소개해드리도록 하겠습니다.  

## Hadamard (H) gate
Qubit의 초기상태에서 0과 1의 상태를 동시에 가질 수 있도록, 중첩을 시켜주는 gate입니다.  

**양자게이트 :**  
![image](https://user-images.githubusercontent.com/15958325/67822542-10b13280-fb04-11e9-89ca-67e32d636a94.png)

**행렬식 :**  
$$ H = \frac{1}{\sqrt{2}}\left[\begin{array}{cc} 
1 & 1\\ 
1 & -1 
\end{array}\right
]$$

single Qubit에 적용 :  



## Pauli gate

파울리 X,Y,Z게이트는 Qubit를 X축 Y축 Z축으로 회전시키는 게이트 입니다.

### Pauli-X gate
고전 컴퓨터에서의 Not Gate역할을 하는 게이트입니다.  

**양자게이트 :**   
![image](https://user-images.githubusercontent.com/15958325/67742215-c4f87d80-fa5e-11e9-8148-5ac322bd0544.png)

행렬식 :  
$$ X = \left[\begin{array}{cc} 
0 & 1\\ 
1 & 0 
\end{array}\right
]$$

$$  $$