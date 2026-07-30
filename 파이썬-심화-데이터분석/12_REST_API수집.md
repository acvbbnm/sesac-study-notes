**12. REST API 수집**

robots.txt · HTTP 메서드 · requests · 예외 · JSON · POST · 인증

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1\. 수집 윤리 (robots.txt · rate limit)

데이터를 수집하기 전에 **사이트가 허용하는 범위**를 먼저 확인하고, 서버에 부담을 주지 않도록 요청 속도를 조절해야 합니다.

from urllib.robotparser import RobotFileParser

rp = RobotFileParser()

rp.set_url("http://localhost:8800/robots.txt")

rp.read()

rp.can_fetch("\*", "http://localhost:8800/") \# True → 수집 허용

rp.can_fetch("\*", "http://localhost:8800/admin") \# False → 차단 경로

import time

\# 요청 사이에 간격을 둬 IP 차단(DDoS 오인) 방지

time.sleep(1.0) \# 한 요청 후 1초 대기

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 robots.txt로 허용 확인 · sleep으로 속도 제한</strong></p>
<p><strong>robots.txt</strong>는 사이트 운영자가 크롤러에게 공개하는 수집 규칙입니다. <strong>RobotFileParser.can_fetch('*', url)</strong>로 경로별 허용 여부를 검사합니다. 짧은 시간에 수백 건을 보내면 <strong>load balancer가 DDoS로 오인해 IP를 차단</strong>할 수 있으니 <strong>time.sleep()</strong>으로 요청 간격을 두고, 이미 받은 데이터는 재요청하지 않습니다.</p></td>
</tr>
</tbody>
</table>

2\. HTTP 기초 (메서드 · GET vs POST)

HTTP 메서드는 **서버에 보낼 의도**를 나타냅니다. 같은 요청을 반복해도 결과가 같은지를 뜻하는 **멱등성(idempotency)**을 알면 재시도 설계가 단순해집니다.

| **메서드** | **의미**           | **멱등성** | **재시도**      |
|------------|--------------------|------------|-----------------|
| GET        | 조회 — 데이터 읽기 | **멱등**   | 안전            |
| POST       | 생성 — 결과 제출   | **비멱등** | 위험(중복 생성) |
| PUT        | 교체 — 레코드 갱신 | **멱등**   | 안전            |
| DELETE     | 삭제 — 항목 제거   | **멱등**   | 안전            |

**GET은 조건을 URL 쿼리 문자열**에 붙여 보내 URL이 바뀌고, **POST는 조건을 body(payload)**에 담아 보내 URL은 그대로입니다. 브라우저 F12 → Network 탭의 Payload에서 확인할 수 있습니다.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 멱등성 = 반복해도 안전한가</strong></p>
<p>GET은 수십 번 반복해도 결과가 항상 같아(조회) 재시도가 안전하지만, <strong>POST는 호출할 때마다 새 레코드가 생성</strong>될 수 있어 네트워크 오류 시 재요청을 신중히 해야 합니다. URL에 파라미터가 보이면 GET, 숨겨져 있으면 POST입니다.</p></td>
</tr>
</tbody>
</table>

3\. requests.get (timeout · 응답 읽기)

네트워크는 로컬 파일과 달리 통제 불가 변수가 많으므로 **실패를 기본으로 깔고** 요청합니다.

import requests

URL = "http://localhost:8800/api/echo"

resp = requests.get(URL, timeout=(3.05, 10)) \# (연결, 읽기) 타임아웃

resp.raise_for_status() \# 4xx·5xx면 HTTPError 발생

resp.status_code \# 200

resp.headers\["Content-Type"\] \# application/json; charset=utf-8

resp.headers.get("Server", "?") \# 누락 헤더는 기본값

data = resp.json() \# JSON 본문 → 파이썬 dict

**params**에 dict를 넘기면 키-값 쌍이 자동으로 URL 쿼리스트링으로 인코딩됩니다(특수문자·한글도 안전하게 처리).

params = {"topic": "crawl", "week": "2"}

resp = requests.get(URL, params=params, timeout=10)

resp.url \# http://localhost:8800/api/echo?topic=crawl&week=2

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 timeout·raise_for_status·params 3종 세트</strong></p>
<p><strong>timeout</strong>은 무한 대기를 차단하고(안 주면 서버가 응답을 안 줄 때 영원히 멈춤), <strong>raise_for_status()</strong>는 4xx·5xx를 예외로 바꿔 if 검사 없이 처리하게 합니다. 쿼리 조건은 문자열을 직접 잇지 말고 <strong>params=dict</strong>로 넘겨 인코딩을 맡깁니다.</p></td>
</tr>
</tbody>
</table>

4\. 네트워크 예외 처리

네트워크는 다양한 외부 변수가 있어 예외를 정확히 분리해야 합니다. 세 가지 대표 예외:

- **ConnectionError** — 회선 단절·서버 Off로 접속 자체가 실패

- **Timeout** — 서버 과부하로 응답이 제한 시간을 초과

- **HTTPError** — 연결 성공 후 4xx/5xx 에러 코드 수신

from requests.exceptions import Timeout, ConnectionError, HTTPError

def fetch(url):

try:

r = requests.get(url, timeout=5)

r.raise_for_status()

return r.json()

except Timeout as e: \# 자식 예외 먼저

print("\[time\] 초과:", e)

except ConnectionError as e:

print("\[conn\] 연결 실패:", e)

except HTTPError as e:

print("\[http\]", e.response.status_code)

except requests.RequestException as e: \# 부모 — 맨 아래

print("\[req\] 알 수 없는 오류:", e)

return None

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 구체 예외 먼저, 부모(RequestException)는 마지막</strong></p>
<p>파이썬은 except를 <strong>위에서부터 차례로 매칭</strong>합니다. 따라서 좁은 예외(Timeout·ConnectionError·HTTPError)를 먼저 처리하고, 이들의 부모인 <strong>RequestException은 맨 마지막</strong>에 둬야 합니다. 부모를 위에 두면 자식 예외가 영원히 잡히지 않습니다.</p></td>
</tr>
</tbody>
</table>

5\. JSON 파싱 (중첩 탐색 · 컴프리헨션)

API 응답은 **dict 안에 list, list 안에 dict**가 중첩된 경우가 많습니다. **resp.json()**이 이 구조를 파이썬 객체로 바꾸면 키와 인덱스로 단계별로 탐색합니다. 리스트 컴프리헨션으로 원하는 항목만 뽑습니다.

items = requests.get(url).json()\["items"\] \# dict → list of dict

\# severity가 Critical인 것만 cve_id 추출

criticals = \[i\["cve_id"\] for i in items

if i.get("severity", "Unknown") == "Critical"\]

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 .get(키, 기본값)으로 KeyError 방지</strong></p>
<p>중첩 구조에서 <strong>i["severity"]</strong>로 직접 조회하면 그 키가 없는 레코드에서 <strong>KeyError로 프로그램이 중단</strong>됩니다. <strong>i.get("severity", "Unknown")</strong>처럼 기본값을 주면 키가 누락돼도 수집을 이어갈 수 있습니다.</p></td>
</tr>
</tbody>
</table>

6\. POST · 페이지네이션

**requests.post()**의 **json=** 매개변수에 dict를 넘기면 dict를 JSON으로 직렬화하고 **Content-Type: application/json** 헤더를 자동 추가합니다.

resp = requests.post(

"http://localhost:8800/api/reports",

json=payload, \# dict → JSON + Content-Type 자동

headers={"Authorization": f"Bearer {TOKEN}"},

timeout=10,

)

대량 데이터는 한 번에 안 오고 **페이지별로 잘라 응답**됩니다. 응답의 **next 커서**를 따라가며 while 루프로 모든 페이지를 누적하되, **max_pages 상한**으로 무한 루프를 막습니다.

def collect_all(max_pages=50):

collected, page = \[\], 1

while page \<= max_pages: \# ① 페이지 상한

r = requests.get(BASE, params={"page": page}, timeout=10)

r.raise_for_status()

body = r.json()

collected.extend(body\["items"\]) \# 원소 단위 평탄 누적

if not body.get("next"): \# ② next 없으면 종료

break

page += 1

time.sleep(0.2)

return collected

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 종료 조건은 next와 max_pages 둘 다</strong></p>
<p><strong>json=payload</strong>는 JSON 직렬화와 헤더를 자동 처리합니다(data=는 폼 전송용이라 JSON API엔 부적합). 페이지네이션은 <strong>next 유무(if not body.get('next'): break)</strong>로 끝을 감지하되, 서버 버그로 next가 계속 오는 무한 루프를 막으려 <strong>max_pages 상한</strong>을 함께 둡니다.</p></td>
</tr>
</tbody>
</table>

7\. 인증 (Session · Bearer 토큰)

**Authorization 헤더**에 Bearer 토큰을 실어 보냅니다. 인증 없이 요청하면 401이 오고, **Session**에 토큰을 한 번 설정하면 이후 모든 요청에 같은 헤더가 자동으로 붙습니다.

import requests, os

TOKEN = os.getenv("API_TOKEN") \# 하드코딩 금지 → 환경변수

requests.get(f"{BASE}/api/protected", timeout=10)

\# 401 {'error': 'unauthorized'} 인증 없음

session = requests.Session()

session.headers.update({"Authorization": f"Bearer {TOKEN}"})

session.get(f"{BASE}/api/protected", timeout=10)

\# 200 {'user': 'student'} 같은 Session으로 재요청

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 토큰은 환경변수로 · Session에 한 번만 설정</strong></p>
<p><strong>토큰을 코드에 하드코딩하면 저장소 노출 사고</strong>로 이어지므로 <strong>os.getenv("API_TOKEN")</strong>으로 실행 시점에 읽습니다. <strong>requests.Session()</strong>에 Authorization 헤더를 한 번 등록하면 그 세션의 모든 요청에 자동 적용돼 매번 headers를 넘길 필요가 없습니다.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 Ch12 핵심 3</strong></p>
<p>① 요청은 <strong>timeout + raise_for_status + 예외 분리</strong>가 기본. ② JSON은 <strong>dict처럼 .get()으로 안전 탐색</strong>, 인증 토큰은 환경변수로 읽어 <strong>Authorization 헤더/Session</strong>에 실음. ③ 대량 데이터는 <strong>next 커서를 while로 따라가며 누적</strong>하고 max_pages·sleep으로 안전장치를 둔다.</p></td>
</tr>
</tbody>
</table>
