# prediction_web_service

## 개발환경
``` sh
* Python 3.7 ver
* RDS(My sql)
* HTML
* AJAX
* UBUNTU (AWS)
* putty
```

## 세팅

``` sh
$ sudo pip3 install python3
$ sudo pip3 install flask
$ sudo pip3 install pymysql
$ sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 5000
$ sudo python3 main.py
```

## 프로젝트 설명
* 리얼타임 스포츠 베팅 시뮬레이션 웹사이트 개발
- 해외 배당 API bets365 활용
