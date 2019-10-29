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

# Quantum Gates

밑에부터 양자==Qbit라고 하겠습니다.
## Notation
기존의 bit는 0과 1로 표기할 수 있지만 Qbit의 표기는 약간 다릅니다.  

앞전 포스팅에서 언급했던 중첩때문에 Qbit의 상태는 0이다 1이다로 표현할 수 없습니다.  

그래서 추상적인 벡터와 선형 범함수를 표현하는 데 사용하는 `ket-vector`를 표준 표기법으로 사용합니다.  

>0인 상태, 확률이 a일때 : `$$ a | 0> $$`     
>1인 상태, 확률이 b일때 : `$$ b | 1> $$`

bar($$\|$$)와 꺽쇠(>)기호를 사용하여 표기합니다.  

그래서 하나의 Qbit 상태는 다음과 같이 표현될 수 있습니다.  

$$ \Uppsi_{양자}>=\upalpha \bar 0>+\textbeta \bar 1> $$

$$ p(\theta) = \mathbf{\prod}_{i,c}p(\mathbf{\theta}^i(c)) $$
