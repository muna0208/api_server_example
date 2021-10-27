# api_server_example
web.py(Python 3.8) 예제 프로그램

# web.py 기반 API 서버 만들기

## 개요

이 문서는 web.py를 기반으로 API 서버를 만드는 한 가지 방법을 소개한다.
web.py를 기반으로 API 서버를 만드는 방법은 여러 가지가 존재하지만
이 방법은 다음의 측면을 강조하여 설계되었다.

* web.py에 대한 별다른 지식이 없이도 API를 추가할 수 있다.
* 필수 파라메터 검사 및 디폴트 값 처리 등을 편리하게 정의할 수 있다.
* API가 구현이 되지 않은 상황에서도 예제 결과를 등록하여 API를 동작하도록 할 수 있다.
* API를 콘솔에서 테스트할 수 있다.

다만 python의 특성과 web.py 자체의 한계로 인해 이 예제에 의해 만들어진 API 서버는 다음과 같은 한계를 지닌다.

> web.py에 동시에 여러 요청이 보내지면 각 요청이 별도의 thread에 의해 처리되지만
> python의 GIL 정책에 의해 한 시점에 하나의 thread만 실행되어
> multi-core multi-processor를 장착한 서버에서 CPU 자원을 충분히 활용하지 못한다.

이 문제를 해결하는 비교적 간단한 방법은 다음과 같다.

> multiprocessing.Process를 이용하여 동일한 web.application 프로세스를 구동하되
> 각 프로세스의 listen port는 TCP가 아닌 linux domain socket을 사용하도록 만들고,
> 그 앞단에 lighthttpd와 같은 web server를 띄운 후 proxy.server 규칙에
> 다중으로 구동한 web.py 서버들을 등록하는 것이다.

이에 대한 자세한 방법은 별도로 leeho@daumsoft.com에 문의 요망.

----

## 구동에 필요한 환경

* python 3.x
* web.py
* cheroot

----

## 파일 구성

* api_server.py: API 서버 메인 프로그램
* request_handler.py: HTTP 요청에 대한 파싱 및 파라메터 처리하는 모듈
* action_table.py: API 서버에서 제공할 API 목록과 각 API에 대한 필수 파라메터 및 디폴트 값을 정의하는 모듈
* api_handler.py: 개별 API에 대한 기능 구현 모듈
* api_handler_test.py: 개별 API에 대한 콘솔 테스트용 프로그램
* sample_response.py: 개별 API의 예제 응답
* json_patch.py: JSON 관련 유틸리티 모듈

----

## API 서버 구동하기

* 예) 7878 포트에 구동할 경우

```
python api_server.py 7878
```

----

## API 서버에 요청 보내기

* 알림
    * 모든 요청은 GET 방식, POST 방식을 모두 지원하지만, 요청 파라메터가 복잡할 경우 POST를 권장
    * 요청의 경로는 API이름.json 형태임
    * POST 방식으로 요청을 보낼 경우 HTTP request header의 Content-Type을 application/json으로 지정하고 payload 영역에 JSON을 보내는 것을 권장
    * GET 방식으로 요청을 보낼 경우 list 형태의 값은 name=value1&name=value2&... 형태로 보낼 수 있음
    * GET 방식으로 요청을 보낼 경우 ascii가 아닌 문자(예: 한글)는 모두 encoding되어야 함
    * 요청에 pretty=Y 라고 파라메터를 정의하면 응답이 인덴팅된 JSON으로 전달됨
    * 요청에 callback 파라메터가 주어지면 JSONP 형태의 응답이 제공됨

* 예) 10.1.1.1 서버의 7878 포트에 서버가 구동되어 있는 상황에서 area라는 API를 GET 방식으로 호출하는 경우

```
curl 'http://10.1.1.1:7878/area.json?width=15&height=8'
```

* 예) 10.1.1.1 서버의 7878 포트에 서버가 구동되어 있는 상황에서 area라는 API를 POST 방식으로 호출하는 경우
    * 아래에서 -d @- 는 payload를 stdin으로 받겠다는 의미이며, {"width": 15, "height": 8}를 입력하고 Enter를 친 후 Ctrl+D를 누르면 요청이 전송됨

```
curl -X POST -H "Content-Type: application/json" -d @- 'http://10.1.1.1:7878/area.json'
{"width": 15, "height": 8}
```

----

## API를 추가하기 위해 처리해야할 작업

* action_table.py에서 action_table에 API 이름에 대응하는 항목을 추가함
* api_handler.py에 API이름에 대응되는 method를 추가함(실제 API 처리 함수)
    * 만약 API 가 구현되지 않아 예제 응답을 이용하고 싶을 경우에는 method 몸체를 return self.get_sample_response() 로 구성함
* sample_response.py에 API이름에 대응되는 예제 데이터를 추가함
* (필요할 경우) 추가된 API를 테스트하는 코드를 api_handler_test.py 에 추가함

----
