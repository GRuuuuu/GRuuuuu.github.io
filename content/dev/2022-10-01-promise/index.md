---
title: "호다닥 톺아보는 Promise"
slug: promise
tags:
  - JavaScript
  - Programming
  - callback
date: 2022-10-01T13:00:00+09:00
---

## 콜백지옥에서 벗어나기
지난 [포스팅](https://gruuuuu.github.io/javascript/callback/)에서 Callback함수란 무엇인가에 대해서 다뤘고, 복잡한 로직에서 Callback함수를 사용할때의 문제점, 콜백지옥에 대해서도 다뤘습니다.  

콜백지옥을 짧게 요약하자면 다음과 같습니다.    
1. 코드의 가독성이 떨어진다.
2. 매 코드블럭들마다 에러처리를 해주어야 한다.  

## Promise?

어떤 특정한 문법이 아니라 일종의 패턴을 나타내는 용어였던 `Callback`과 달리 `Promise`는 Javascript의 객체입니다.  

![img](https://github.com/GRuuuuu/hololy-img-repo/blob/main/2022/2022-09-30-promise/2.png?raw=true)  

간단히 말하자면 **비동기로 실행된 작업의 결과**를 나타내는 객체의 이름이라고 보시면 됩니다.  

## Promise 만들기!

간단히 아래와 같이 `Promise` 생성자로 만들 수 있습니다.  
~~~js
let promise = new Promise(function(resolve, reject) {
  // Doing Something!
});
~~~

`Promise`객체는 파라미터로 `executor`라는 함수를 받아서 **비동기로 실행하고, 성공이든 실패든 값을 반환**하게 됩니다.   
![image](https://github.com/GRuuuuu/hololy-img-repo/blob/main/2022/2022-09-30-promise/1.png?raw=true)  

`executor`는 두개의 Callback 파라미터를 갖고 있습니다.  
- `resolve(value)` : 성공시, **value**를 반환하는 함수 호출  
- `reject(error)` : 실패시, **error**를 반환하는 함수 호출  

## Promise의 4가지 상태
성공과 실패가 있으니 당연히 Promise라는 객체가 갖고있는 상태가 있겠죠?  

![img](https://github.com/GRuuuuu/hololy-img-repo/blob/main/2022/2022-09-30-promise/3.png?raw=true)  

크게는 성공(`fulfilled`)과 실패(`rejected`)가 있고, 실행중인 상태(`pending`)과 실행이 끝났을 때(`settled`)가 있습니다.  

조금 더 자세히 설명하자면,  
- `pending` : `resolve(value)`또는 `reject(error)`가 호출되기 전, 실행중인 상태  
- `fulfilled` : `resolve(value)`가 호출된 상태. 성공적으로 실행.  
- `rejected` : `reject(error)`가 호출된 상태. 실행중 실패.  
- `settled` : 성공/실패 상태유무와 별개로 모든 프로세스가 종료된 상태.  

아래 예시코드에서는 `Promise`생성자로 새로운 `Promise`를 만들어 성공적으로 일을 마쳤다는 것을 가정해 `resolve`함수를 호출하고 있습니다.  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  resolve(1);
});

console.log(p);
~~~

그렇게 반환된 Promise객체는 변수 "p"에 저장되고, 그것을 출력해보면 
~~~
Promise {[[PromiseState]]: 'fulfilled', [[PromiseResult]]: 1}
~~~
상태는 `fulfilled`, 반환된 값은 `resolve`함수에 넣었던 "1"이 담겨있습니다.  

이번엔 작업이 실패했음을 가정해서 `reject`함수를 호출해보겠습니다.  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  reject("ERROR!!!!!!!");
});

console.log(p);
~~~

~~~
Promise {[[PromiseState]]: 'rejected', [[PromiseResult]]: 'ERROR!!!!!!!'}
~~~
이번엔 상태가 `rejected`로 뜨고 `reject`함수에 넣었던 에러메세지가 담겨있습니다!  

## then, catch, finally
그런데 사실 Promise로 실행된 값을 정상적으로 받아보려면 `console.log`가 아니라 다른 방법을 사용해야 합니다.  

왜냐면 **Promise는 비동기작업이기 때문이죠!** 

이전 Callback함수에서 체인을 만들어 비동기작업의 후속작업을 확정적으로 실행할 수 있게 했듯이,  
`Promise`도 작업들을 연결해주는 메서드가 있습니다.  

### then
`then`은 이전 `Promise`객체를 받아서 처리해주는 구문입니다.  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
});

p.then(
  res => {/* promise resolved */},
  err => {/* promise rejected */}
);
~~~
`then`은 두개의 Callback함수를 인자로 받습니다.  
- 첫번째 인자는 promise가 정상적으로 실행되어 값을 반환한 경우 (resolved)  
- 두번째 인자는 promise가 비정상적으로 실행되어 에러값을 반환한 경우(rejected)  

예제로 보면:  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  resolve(1);
});

p.then(
  res => {
    /* promise resolved */
    console.log(res);  //1
  },
  err => {/* promise rejected */}
);
~~~
첫번째 인자를 받아서 출력했더니, `Promise`에서 정상적으로 실행되었다고 가정하여 호출된 `resolve`함수에 담긴 값이 출력되었습니다.  

이번엔 실패하였다고 가정하여 error를 출력해보겠습니다.  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  reject("ERROR!!!");
});

p.then(
  res => {
    /* promise resolved */
    console.log(res);
  },
  err => {
    /* promise rejected */
    console.log(err);  // ERROR!!!
  }
);
~~~
`reject`함수에 담겼던 값이 `then`의 두번째 콜백함수에서 출력되는 것을 확인할 수 있습니다.  

만약 성공적으로 처리한 경우만 다루고 싶다면, `then`에 첫번째 인자만 정의해주면 됩니다.  
~~~js
p.then(
  res => {
    /* promise resolved */
    console.log(res);
  }
);
~~~
생략도 가능합니다.
~~~js
p.then(
    /* promise resolved */
    console.log
);
~~~
### catch
`catch`는 에러를 처리해주는 부분입니다.  
try-catch문을 생각하면 이해가 쉬울 것 같습니다.  

~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  reject("Error!!!");
});

p.then(
  res => {console.log(1,res)}
).then(
  res => {console.log(2,res)}
).catch(
  err => {console.log(err)}  //Error!!!
);
~~~

### finally
`finally`는 `Promise`가 성공했든 실패했든 마무리가 지어지면 실행되는 부분입니다.  
try-catch-finally문을 생각할 수도 있는데 약간 다릅니다.

~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  resolve(1);
});

p.then(
  res => {console.log(res);}  //1
).catch(
  err => {console.log(err);}
).finally(
  () => {console.log("finally!!")}  //finally!!
);
~~~

이렇게 보면 `then`과 `catch`가 전부 끝난 후 `finally`가 실행되는 것처럼 보이지만,  
`finally`는 `Promise`의 프로세스가 마무리된 후 실행되는 부분이기 때문에 어느 위치든 `Promise`이후면 실행됩니다.  
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  resolve(1);
});

p.finally(
  () => {console.log("finally!!")}  //finally!!
).then(
  res => {console.log(res);}  //1
)
~~~
위 예시처럼 `then`이 끝나야 `finally`가 실행되는게 아니라 `Promise`가 종료되고나서 `finally`가 실행되고, 결과값은 `finally`를 통과해서 `then`으로 넘어가게 됩니다.  

---