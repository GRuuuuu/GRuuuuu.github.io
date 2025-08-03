---
title: "[Quantum for Developers] IBM Q Experience"
slug: quantum_experience
tags:
  - Quantum
  - Computing
  - Physics
date: 2019-11-01T13:00:00+09:00
series: ["Quantum for Developers"]
series_order: 3
---

## Overview
이번문서에서는 직접 양자 게이트들을 GUI환경에서 실습해볼수있는 환경인 **IBM Q Experience**의 **Circuit Composer**와 양자프로그래밍에 필요한 SDK인 **Qiskit**에 대해 간단히 알아보도록 하겠습니다.  

각 gate에 대해서는 알고있다는 것을 전제로 진행하겠습니다.  
>[[Quantum for Developers] 양자 게이트](https://gruuuuu.github.io/quantum/quantum_gate/)  

# IBM Q Experience
IBM에서는 일반 유저들이 양자컴퓨팅을 실제로 사용해볼수있게 양자컴퓨터 몇대를 클라우드로 오픈해두고 있습니다.  

[IBM Q Experience](https://quantum-computing.ibm.com/)  

가입하고, 메뉴를 보시면   
![image](https://user-images.githubusercontent.com/15958325/67997272-cd3afd80-fc96-11e9-9950-32ce1c789b89.png)  

Tools에 **Circuit Composer**와 **Qiskit Notebooks**라고 쓰인게 보이실 겁니다. 각 도구들로 프로그래밍을 할 수 있습니다.   

그리고 오른쪽 화면을 보시면   
![image](https://user-images.githubusercontent.com/15958325/67997333-2145e200-fc97-11e9-8d4c-103fb4ab2e70.png)  
유저가 사용할 수 있는 양자컴퓨터의 수와 양자컴퓨터들의 사용현황을 보여주고 있습니다.  

우선 **Circuit Composer**로!   

## Circuit Composer

먼저 새로운 Circuit을 생성합니다.  
![image](https://user-images.githubusercontent.com/15958325/67997425-69fd9b00-fc97-11e9-9a5e-afa8707e56c7.png)  


새로 생성하게되면 다음과 같이 줄여러개와 네모들이 보이게 됩니다.      
![image](https://user-images.githubusercontent.com/15958325/67997463-97e2df80-fc97-11e9-8cb8-d4e855c9506a.png)   

각 컴포넌트를 소개하자면 :   
- 네모 : Gate
- 줄 : q는 Qubit, c는 Classical bit

Qubit가 너무 많으니 좀 줄여봅시다.  

왼쪽 탭의 "</>"를 눌러주세요.  
 ![image](https://user-images.githubusercontent.com/15958325/67997723-ce6d2a00-fc98-11e9-8867-b0fa1313b71c.png)  
이게 바로 옆그림의 소스입니다.  

5개에서 2개씩으로 줄여줍시다.  
![image](https://user-images.githubusercontent.com/15958325/67997808-1d1ac400-fc99-11e9-98b3-5e3d5a1c7147.png)  
바꾸자마자 바로 변경되었습니다.  

그리고 왼쪽 탭의 차트 부분을 눌러보면 다음과 같이 00만 나오게 됩니다. Qubit의 초기상태가 0이기 때문입니다.  
![image](https://user-images.githubusercontent.com/15958325/67997847-49cedb80-fc99-11e9-9ad0-edce6a1e5579.png)    

그럼 이제 H 게이트를 추가하고 CNOT 게이트도 추가해봅시다.  
![image](https://user-images.githubusercontent.com/15958325/67997900-869ad280-fc99-11e9-93ef-40881153d599.png)  
두개의 Qubit가 서로 얽혀진 것을 확인할 수 있습니다.  

이렇게 실시간으로 시뮬레이팅된 결과를 눈으로 직접 확인해볼 수 있습니다.  

마지막으로 measure 아이콘을 끌어서 Qubit의 관찰값을 Classical bit에 옮기는 작업을 해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/68002338-c1a60180-fcab-11e9-9dc1-ffa770d5abdf.png)  


그럼 양자컴퓨터에 실제로 돌려봅시다.  
![image](https://user-images.githubusercontent.com/15958325/67997951-d8435d00-fc99-11e9-98f9-b33a16084a0d.png)  
이름을 지정해주고, 저장한 뒤에 RUN을 눌러줍니다.  

![image](https://user-images.githubusercontent.com/15958325/67997973-f27d3b00-fc99-11e9-972a-945badbe929e.png)  
어떤 양자컴퓨터에 돌릴건지, 얼마나 shot을 쏠건지를 정하라고 나옵니다.  

>**shot이란?**  
>양자는 중첩상태이고 관찰을 통해 하나의 결과만 받게 되는데 그 결과는 확률에 의해 나오게 됩니다.  
>그럼 더 많이 관찰하게 되면 확률적으로 정확도가 높아지겠죠.  

현재는 양자컴퓨터의 자원이 부족하기 때문에 최대한 큐가 없는곳으로 작업을 넣어둔 뒤에 기다려 줍시다.   
![image](https://user-images.githubusercontent.com/15958325/68002388-f7e38100-fcab-11e9-974f-250b3fb575cf.png)  

Queue상태에 들어가있다고 상태가 뜨고 클릭해보면 상세정보들을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/68002448-3ed17680-fcac-11e9-9877-99739730fb95.png)

Complete되고 나면 다음과 같이 결과를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/68002854-409c3980-fcae-11e9-806a-323e9881f689.png)  

분명 00과 11만 나와야 하는데 01과 10도 일부 나온것을 확인할 수 있습니다. 이게 양자컴퓨터의 에러율인것 같습니다.  



## Qiskit Notebooks

다음은 코딩으로 짜는 방법입니다. IBM Q Expeerience에서 제공해주는 Qiskit Notebooks를 사용해도 되고, 그냥 아무데서나 하셔도 됩니다.  

![image](https://user-images.githubusercontent.com/15958325/68003113-5ceca600-fcaf-11e9-9c28-c4716302c0b0.png)  
Qiskit은 IBM의 양자 컴퓨터를 pulse, circuit레벨에서 다룰 수 있게 하는 오픈소스 프레임워크입니다.  

>[Qiskit Github](https://github.com/Qiskit)  
>
>Qiskit은 나중에 따로 포스팅으로 소개드리도록 하겠습니다.  

~~~python
#IBMQ의 account정보 저장
from qiskit import IBMQ

MY_API_TOKEN='e98185~~~abx'
IBMQ.save_account(MY_API_TOKEN,overwrite=True)
~~~

>토큰 정보는 이곳에서  
>![image](https://user-images.githubusercontent.com/15958325/68003537-26b02600-fcb1-11e9-828c-fc3f873a0c1b.png)  
>
>![image](https://user-images.githubusercontent.com/15958325/68003555-392a5f80-fcb1-11e9-986e-55d69f4c8824.png)   


~~~python
# 필요한 라이브러리 import
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
from qiskit.visualization import *
~~~


~~~python
## 2 Qubit, 2 Classical bit 정의
q = QuantumRegister(2, 'q')
c = ClassicalRegister(2, 'c')
circuit = QuantumCircuit(q, c)

## 0번 Qubit에 H게이트, 0번과 1번을 CNOT
circuit.h(q[0])
circuit.cx(q[0], q[1])

## Qubit을 Classical bit에 매핑
circuit.measure(q, c)

## 회로 그리기
%matplotlib inline
circuit.draw(output="mpl")
~~~
![image](https://user-images.githubusercontent.com/15958325/68003808-5d3a7080-fcb2-11e9-9d66-4810346f8a73.png)  


~~~python
## 1. 시뮬레이터로 테스트
simulator = Aer.get_backend('qasm_simulator')
job = execute(circuit, backend=simulator, shots=1024)
result = job.result()

## 결과를 text와 차트로 출력
counts = result.get_counts(circuit)
print("Result:",counts)
from qiskit.tools.visualization import plot_histogram
plot_histogram(counts)
~~~
![image](https://user-images.githubusercontent.com/15958325/68003895-bacebd00-fcb2-11e9-912f-c0d73f2a7630.png)  


~~~python
# 2. IBM Q 장비로 돌려보기
# 제일안쓰는 장비찾기
from qiskit.providers.ibmq import least_busy
IBMQ.load_accounts()
lb_device = least_busy(IBMQ.backends())

# 실행
job = execute(circuit, backend=lb_device, shots=1024)
from qiskit.tools.monitor import job_monitor
job_monitor(job)
result = job.result()

# 결과를 텍스트와 차트로 출력
counts = result.get_counts(circuit)
print("Result:",counts)
from qiskit.tools.visualization import plot_histogram
plot_histogram(counts)
~~~

![image](https://user-images.githubusercontent.com/15958325/68004013-2d3f9d00-fcb3-11e9-8306-a17640221ee1.png)  

----
 