---
title: "호다닥 톺아보는 async&await"
categories: 
  - JavaScript
tags:
  - JavaScript
  - Programming
  - callback
last_modified_at: 2022-10-03T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## Promise 중첩..?
~~~js
let p = new Promise(function(resolve, reject) {
  // Doing something!
  resolve(1);
});

console.log(p);
~~~
지난 [포스팅](https://gruuuuu.github.io/javascript/promise/)에서는 Promise의 개념과 사용 예시들을 다뤘었습니다.  
위의 예시처럼 간단한 비동기 프로세스라면 상관없겠지만, 비동기와 동기가 섞이거나 복잡한 로직이라면 `Promise`가 점점 중첩되고 `then`과 `catch`가 체인처럼 늘어지다보니  
**"Callback 지옥"** 처럼 가독성이 떨어지진 않지만 그래도 복잡해지면 읽는데 불편함이 생기게 됩니다.   

## async 와 await
그래서 나오게 된 `async`와 `await`!  
Promise를 좀 더 쉽게 사용할 수 있게 해주는 함수들입니다.  

### async

간단한 Promise예제를 한번 봅시다.  
~~~js
function test(){
  return new Promise(function(resolve, reject) {
    // Doing something!
    resolve(1);
  });
}

test().then(
  res => {console.log(res);}
)
~~~
test라는 함수에서 Promise객체를 반환하고 있고,  
그걸 `then`으로 받아 값을 출력하는 코드입니다.  

`async`는 `function`키워드 앞에 붙게되고, 사용하면 암시적으로 Promise객체를 반환하게 됩니다.  
~~~js
async function test(){
  // Doing something!
  return 1;
}

test().then(
  res => {console.log(res);}
)
~~~
이 코드는 위의 코드와 동일한 코드입니다.  

### await
의미그대로 기다려주는 함수입니다.  

Promise에서는 `then`을 통한 연결로 비동기함수를 동기처럼 후속 로직을 실행시킬 수 있었습니다.  

`await`를 사용하면 기존에 익숙한 동기식 코드작성으로 비동기함수들을 다룰 수 있게 됩니다.  

**단! `async`안에서만 가능합니다!**  

예를 들어 
1. 1초동안 기다렸다가 문자열을 반환하는 함수가 있고,  
2. 그 문자열들을 받아 이어붙인 다음  
3. 마지막에 결과값을 출력해야한다고 했을 때,  

Promise로는 이렇게 짤 수 있을겁니다.  
~~~js
//Promise 객체를 반환하는 비동기 함수
//인자로 받은 수만큼 지연시킴
function delay(time){
  return new Promise(resolve => setTimeout(resolve,time));
}

//1초 지연시켰다 "hello"반환
function one(){
  return delay(1000).then(
    res => "hello"
    );
}

//1초 지연시켰다 "world"반환
function two(){
  return delay(1000).then(
    res => "world!"
    );
}

function concat(){
  return one().then(
    a => { 
      return two().then(
        b=>{ 
        return a+b; 
      });
    }
  );
}
concat().then(console.log); //helloworld!
~~~
확실히 Callback지옥보다는 가독성이 좋아지긴 했지만 여전히 `then`을 타고 코드의 depth가 깊어지고 있습니다.  

이걸 async&await식으로 변경해본다면!  
~~~js
function delay(time){
  return new Promise(resolve => setTimeout(resolve,time));
}

async function one(){
  await delay(1000);
  return "hello";
}

async function two(){
  await delay(1000);
  return "world!";
}

async function concat(){
  const a = await one();
  const b = await two();
  return a+b;
}
concat().then(console.log); //helloworld!
~~~
코드가 좀 더 직관적이고 기존의 동기식으로 코드를 짜던것 같이 구성할 수 있습니다.  

단 위에서 언급했듯이, `await`는 `async`안에서밖에 사용할 수 없습니다.  
최상위 레벨에서 사용하려면 익명 `async`함수를 사용하는 것도 방법입니다.  
~~~js
(async () =>{
  const a = await one();
  const b = await two();
  console.log(a+b);
})();
~~~

### catch
에러핸들링은 `await`를 사용하는 쪽에서 `try-catch`로 묶어주면 됩니다.    
~~~js
async function concat(){
  try{
    const a = await one();
    const b = await two();
    return a+b;
  } catch(err){
    alert(err);
  }
}
~~~

## 비동기함수들 병렬처리하기! (Promise.all)
위의 예제를 다시 가져와서 보면  
~~~js
async function concat(){
  const a = await one();
  const b = await two();
  return a+b;
}
~~~
함수 `one`이 실행될때까지 기다리고, 함수`two`가 실행됩니다.  
둘 다 delay를 1초씩 주었으니 총 합 2초를 기다려야 하는데요, 굳이 순차적으로 실행시키지 않고 한번에 전부 돌려버릴수도 있습니다.  

바로 `Promise.all`입니다. 
~~~js
function concat(){
  return Promise.all([one(),two()]).then(res=>
    res[0]+res[1]);
}

concat().then(console.log); //helloworld!
~~~
사용은 `Promise.all`의 인자로 병렬로 실행시킬 함수들을 배열로 넣어주면 됩니다.  
그리고 반환값도 배열로 나오게 됩니다.  

----