---
title: "호다닥 톺아보는 Callback 함수"
slug: callback
tags:
  - JavaScript
  - Programming
  - callback
date: 2022-09-23T13:00:00+09:00
---

## Callback?
![callback_1](https://user-images.githubusercontent.com/15958325/192140413-524ba28b-6fba-4705-be24-f2de9bdc3147.png)  

일반적인 함수의 형태는 아래와 같이 생겼습니다.  
~~~js
function hello(word){
  console.log(word);
}

var str = "hello!"
hello(str);  // hello!
~~~
파라미터로 문자든 숫자든 object든 들어가서 내부 로직에의해 처리되는 형태로 되어있습니다.  

object는 뭘까요? json이나 배열 등등의 객체를 말할 수 있겠죠.  
그렇다면, 자바스크립트에서 **"함수"**는 무엇일까요?  

자바스크립트에서 모든 함수는 **Function Ojbect**입니다.  

하나의 객체로 처리되기때문에 함수도 함수의 파라미터로 들어갈 수 있습니다!  

~~~js
function concat(one, two, callback){
  var res = one + two;
  callback(res);
}
  
function print(str){
  console.log(str);
}

concat("hello ", "world!", print); // hello world!
~~~
위의 예시에서는 `concat`이라는 함수를 선언하면서 세번째 파라미터인 `callback`의 동작도 정의해주었고,  

실제 `concat`이 사용되는 부분에서 `print`라는 이름의 함수를 정의함과 동시에 파라미터로 사용하는 모습을 보실 수 있습니다.  

이렇게 함수의 파라미터로 전달되는 함수를 **"callback"** 함수라고 합니다.   

그래서 특별한 문법이 있는게 아니라 호출되는 방식에 따라 불리는 이름 이라고 보시면 됩니다.  

## Callback의 여러 모양
여러 방법으로 Callback함수를 호출할 수 있습니다.  

### 1. 함수 선언 후 사용
이 경우는 위 스크립트방식과 동일합니다.  
함수를 각각 선언 후, 사용할때 함수의 이름만 파라미터에 넣습니다.  

호출부를 간결하게 만들 수 있으며 Callback함수를 재사용하기 편리합니다.  

### 2. 함수 선언과 동시에 사용  
~~~js
function concat(one, two, callback){
    var res = one + two;
    callback(res);
  }

concat("hello ", "world!", function print(str){
    console.log(str);
}); // hello world!
~~~
위의 스크립트와 동일한 작업을 합니다.  
다른점은 파라미터 부분에서 함수 선언을 동시에 하고 있습니다.  

~~~js
concat("hello ", "world!", function (str){
...
~~~
위와 같이 함수 이름은 생략할 수 있습니다.  

### 3. Arrow Function(화살표 함수)
Arrow Function은 기존 함수를 간단한 문법으로 표현하는 방식입니다.  

화살표(=>) 왼쪽에 있는 인자들을 받아서  
오른쪽의 로직을 수행한다고 보시면 됩니다.  
~~~js
function concat(one, two, callback){
    var res = one + two;
    callback(res);
  }

concat("hello ", "world!", (str) => {
    console.log(str);
}); //hello world!
~~~

괄호는 생략 가능합니다.  
~~~js
concat("hello ", "world!", str => {
...
~~~

>**리빙포인트)**   
>`(param1, param2...) => {}`  // 중괄호는 함수의 body라고 생각하면 된다!  
>`(param1, param2...) => exp` // 중괄호가 없는 경우는 `return exp;`이다!


## Callback함수 어디서 쓸까?
자바스크립트는 기본적으로 **동기식 언어**라 순차적으로 라인을 실행합니다.  
하지만 꽤 많은 경우에서 비동기식 처리를 해야할 때가 있죠, 예를 들어서 브라우저 이벤트, DB쿼리, 서버통신 등등이 있습니다.  

비동기는 single thread가 아닌 각각의 프로세스가 multi thread로 동작한다는 의미죠.  

때문에 기존의 동기식 로직으로는 비동기 이벤트를 핸들링하기 어렵습니다.  

아래 코드의 `getData`는 `ajax`를 통해 data를 불러와서 반환하는 함수입니다. 서버와 통신을 도와주는 `ajax`는 대표적인 비동기함수죠.    
아마 코드의 작성자는 불러온 data를 log로 찍고 싶었을 것입니다.  
~~~js
function getData() {
    var data;
    $.get('https://{URL}/sampleApi/v1/data', function (res) {
        data = res;
    });
    return data;
}

console.log(getData()); // undefined
~~~
그런데 결과는 `undefined`가 출력되었습니다.  
data를 받아오기전에 `console.log`가 실행되었기 때문입니다.  

이와같이 **비동기함수 실행 이후에 무언가 순차적으로 실행될 로직을 추가**하고 싶을 때 사용할 수 있는 방법이 **Callback**입니다.  

~~~js
function getData() {
    var data;
    $.get('https://{URL}/sampleApi/v1/data', function (res) {
        data = res;
    });
    return data;
}

//console.log(getData()); // undefined

getData((data)=>{
  console.log(data);
});
~~~
위의 코드처럼 Callback함수로 `console.log`를 실행하게 된다면, `getData`함수가 실행된 뒤에 순차적으로 출력하게되니 원하는 대로 로직을 구성할 수 있을겁니다!  

## Callback Hell (콜백 지옥)

조금 더 복잡한 로직을 생각해봅시다.  

1. GET으로 data를 긁어옴
2. A함수 실행
3. B함수 실행
4. C함수 실행  
...

이렇게 긁어온 데이터들을 각 함수를 통해 정제해야하고, 반드시 순차적으로 실행되어야 한다고 했을 때 Callback함수로 구현한다면 다음과 같은 형태가 될 것입니다.  

~~~js
getData((data)=>{
  A((data)=>{
    B((data)=>{
      C((data)=>{
        D((data)=>{
          E((data)=>{
            ...
          });
        });
      });
    });
  });
});
~~~

![callback_2](https://user-images.githubusercontent.com/15958325/192140764-b3905d6a-d3e1-414c-876f-2a5966f12d71.png)  

뭔가 가독성도 떨어지고 코드를 유지보수하기도 복잡해보입니다.  
그리고 함수의 깊이가 너무 깊어지니 에러 핸들링하기도 어려울 것입니다.  

이처럼 함수의 파라미터로 넘겨지는 콜백 함수가 반복되어 코드의 들여쓰기 수준이 감당하기 힘들 정도로 깊어지는 현상을 "**Callback Hell**", 콜백 지옥이라고 부릅니다.  

그러면 어떻게 이 콜백지옥을 벗어날 수 있을까?  

다음 포스팅에서는 `Promise`와 `async`, `await`에 대해서 알아보도록 하겠습니다.  

----