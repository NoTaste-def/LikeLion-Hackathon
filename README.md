# LikeLion-Hackathon

### [会議録](https://docs.google.com/document/d/1q98L3-qdRojePyOh-5ZUIalv5jVCzIac39IjWbg9Er0/edit)

### [Figma](https://www.figma.com/proto/Am6ehAp9Y3ZuqV7m3hA7zD/24_%EC%A0%80%EC%86%8D%EB%85%B8%ED%99%94_%EB%8A%90%EB%A6%BC%EC%9D%98%EB%AF%B8%ED%95%99?t=jEe87ggp40lpQifW-1&node-id=1-2&starting-point-node-id=1%3A2)

> #### History

###### 2024-07-15 : Todo List Database & API completion.

###### 2024-07-18 : User Provided Todo List Database & API completion.

###### 2024-07-19 : Successfully Merged Database & API.

###### 2024-07-23 : Server Completion.

###### 2024-08-05 : Changed login logic. From session method to self-implemented login logic.



### 問題
CORSエラーによる特定URLへの接近が不可能になった。
<br/>
settings.pyとviews.pyの権限に関する設定およびコードを追加しても問題が解決出来なかった。

### 解決
データベースの構造を変え、ログインを行う仕組みを変えることにした。
<br/>

### 考察
推論に過ぎないが、おそらくDRFが提供するセッション、CSRF検証に関する問題だったと思う。
<br/>
この問題を解決するためにはDRF自体の内部ロジックに詳しく調べる必要をかんじた。
<br/>
これから時間をかけて調べる予定だ。
