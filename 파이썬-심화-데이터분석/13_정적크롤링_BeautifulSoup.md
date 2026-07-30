**13. 정적 크롤링 (BeautifulSoup)**

정적 vs 동적 · HTML 구조 · find · select · 값 추출 · 테이블

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1\. 정적 vs 동적 (데이터 위치)

페이지의 **데이터가 어디서 채워지는가**에 따라 도구가 달라집니다. HTML 응답에 데이터가 이미 들어 있으면 **requests + BeautifulSoup**로 충분하고, 자바스크립트가 나중에 채워야 보이면 **Selenium**이 필요합니다.

| **기준** | **정적 (requests+BS4)** | **동적 (Selenium)** |
|----|----|----|
| 대상 | 서버 렌더링·정적 페이지 | SPA·무한스크롤·로그인 후 화면 |
| 판단 | **View Source에 데이터 보임** | View Source에 데이터 없음(JS가 채움) |
| 원칙 | **가능하면 API \> 정적** | 정적으로 안 되면 그때 동적(최후 수단) |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 판단 순서: 공개 API → 정적 → Selenium</strong></p>
<p>브라우저 <strong>View Source(페이지 원본)</strong>에서 데이터가 보이면 정적, 안 보이면 동적입니다. Selenium은 브라우저를 통째로 띄워 무겁고 느리므로(수만 건이면 며칠), <strong>① 공개 API → ② requests 정적 크롤링 → ③ 최후에 Selenium</strong> 순서로 판단합니다.</p></td>
</tr>
</tbody>
</table>

2\. HTML 구조 (태그·속성·텍스트 트리)

HTML 요소는 **태그명·속성·텍스트**로 구성되고, 중첩된 태그는 **부모-자식 트리** 관계를 만듭니다.

\<a href="/cve"\>상세\</a\>

\# ├ 태그명: a

\# ├ 속성: href="/cve"

\# └ 텍스트: 상세 (여는 태그와 닫는 태그 사이의 내용)

\<article\>

\<a href="..."\>...\</a\> \# article이 부모, a가 자식

\</article\>

크롤링에서 자주 만나는 태그: **h1~h6**(제목), **p**(문단), **ul\>li**(목록), **table\>tr\>th/td**(표), **a href**(링크), **img src**(이미지), **div**(레이아웃 묶음).

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 선택자 표기: 태그명 그대로 · class는 점 · id는 샵</strong></p>
<p>요소를 가리키는 CSS 선택자는 <strong>태그명은 그대로(p), class는 점(.quote), id는 샵(#header)</strong>으로 표기합니다. <strong>class는 여러 요소에 중복 사용 가능</strong>하지만 <strong>id는 페이지에 한 번만</strong> 써야 합니다. 트리 경로로 요소를 찾으면 디자인이 바뀌어도 같은 요소를 안정적으로 찾습니다.</p></td>
</tr>
</tbody>
</table>

3\. BeautifulSoup 생성 · 파서 고르기

**BeautifulSoup**은 HTML 문자열을 트리로 변환하는데, 이 파싱을 **두 번째 인자로 지정한 파서**에게 맡깁니다.

import requests

from bs4 import BeautifulSoup

res = requests.get(URL, timeout=5)

res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser") \# 두 번째 인자 = 파서

| **파서**    | **설치**                     | **특징**                |
|-------------|------------------------------|-------------------------|
| html.parser | **표준 라이브러리 — 불필요** | 설치 없이 바로 사용     |
| lxml        | pip 설치 필요                | 빠르고 깨진 HTML에 관대 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 이 강의는 html.parser (설치 불필요)</strong></p>
<p>두 번째 인자를 생략하면 경고가 나므로 명시합니다. <strong>html.parser</strong>는 파이썬 표준 라이브러리라 설치가 필요 없고, <strong>lxml</strong>은 더 빠르고 깨진 HTML에 관대하지만 pip 설치가 필요합니다. 이 강의는 html.parser를 씁니다.</p></td>
</tr>
</tbody>
</table>

4\. find · select 로 요소 찾기

**find**는 태그명·속성으로 첫 번째 일치 태그를 반환합니다. **class는 파이썬 예약어이므로 class\_**로 씁니다.

title = soup.find("h1", class\_="board-title") \# 첫 h1 태그

print(title.text) \# 태그 안 텍스트

**select**는 **CSS 선택자 한 문자열**로 모든 조건을 지정하고 **일치하는 태그 리스트(ResultSet)**를 반환합니다. 개발자 도구의 Copy selector로 얻은 선택자를 그대로 붙여 넣을 수 있습니다.

\# 점(.)으로 class를 이어 붙이면 둘 다 가진 요소만 선택 (AND)

critical = soup.select("span.severity.critical")

print(\[s.get_text(strip=True) for s in critical\]) \# 리스트 → 컴프리헨션

\# 자손 결합: 공백으로 트리 경로 지정

soup.select("article.advisory h3.title")

**select_one**은 select와 같은 선택자를 쓰되 **첫 일치 요소 하나만** 반환합니다. 일치가 없으면 **None**을 반환하므로 .get_text() 호출 전에 확인해야 합니다.

one = soup.select_one("article.advisory h3.title")

if one: \# None일 수 있으니 확인

print(one.get_text(strip=True))

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 select=리스트, select_one=하나(None 주의)</strong></p>
<p><strong>find/find_all</strong>은 태그명·속성 인자로, <strong>select/select_one</strong>은 CSS 선택자 문자열로 찾습니다. <strong>select와 find_all은 리스트</strong>를, <strong>select_one과 find는 하나(없으면 None)</strong>를 반환합니다. None에 .get_text()를 쓰면 AttributeError가 나므로 if로 먼저 확인합니다. 점으로 class를 이어 붙이면 두 class를 모두 가진 요소만(AND) 선택됩니다.</p></td>
</tr>
</tbody>
</table>

5\. 값 추출 (.get · .get_text)

노드를 찾은 뒤에는 값을 추출합니다. 방향은 **태그의 속성값이냐 안쪽 텍스트냐** 두 가지입니다.

cve = art.get("data-cve") \# 속성값 읽기 (href, src, data-\* 등)

text = tag.get_text(strip=True) \# 안쪽 텍스트 (strip으로 공백 제거)

태그가 없으면 select_one이 None을, 속성이 없으면 \[\] 접근이 KeyError를 냅니다. **.get(이름, 기본값)**과 None 확인으로 방어합니다.

for art in soup.select("article.advisory"):

cve = art.get("data-cve", "N/A") \# 속성 없으면 기본값

title = art.select_one("h3.title")

title = title.get_text(strip=True) if title else "" \# None 방어

ref = art.select_one("a.ref")

href = ref.get("href", "") if ref else ""

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 속성은 .get(), 텍스트는 .get_text(strip=True)</strong></p>
<p><strong>.get(이름, 기본값)</strong>은 속성값을(href·src·data-cve 등), <strong>.get_text(strip=True)</strong>는 화면에 보이는 안쪽 텍스트를 준다(strip으로 들여쓰기·줄바꿈 제거). 두 함정 — <strong>None 객체에 .get_text() 호출(AttributeError)</strong>과 <strong>없는 속성 [] 접근(KeyError)</strong> — 을 if 확인과 .get() 기본값으로 막습니다.</p></td>
</tr>
</tbody>
</table>

6\. find · find_all · select 선택 기준

세 메서드 모두 태그를 검색하지만 문법·반환값·필터 능력이 다릅니다.

| **기준** | **find / find_all** | **select / select_one** |
|----|----|----|
| 문법 | 태그명 · 속성 인자 | **CSS 선택자 문자열** |
| 반환 | find=Tag/None, find_all=리스트 | select_one=Tag/None, select=리스트 |
| 중첩 구조 | find("article").find("a") | **"article.advisory a.ref"** (한 줄) |
| 필터 능력 | **조건 함수·정규식·속성 dict** | class 결합·속성·자손 결합 |
| 실무 판단 | 복잡한 조건은 find_all | **Copy selector면 select (더 짧음)** |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 깊을수록 select, 복잡한 조건은 find_all</strong></p>
<p>중첩이 깊으면 <strong>select가 CSS 경로 한 줄</strong>로 끝나 더 짧습니다(find는 .find().find() 체인). 반대로 <strong>정규식·조건 함수 같은 복잡한 필터</strong>는 find_all이 유리합니다. 개발자 도구에서 Copy selector로 얻은 선택자는 select에 그대로 붙입니다.</p></td>
</tr>
</tbody>
</table>

7\. 테이블 스크래핑 (thead · tbody)

HTML 표는 **thead(헤더)·tbody(데이터)** 두 부분으로 나뉩니다. thead의 th에서 컬럼명을, tbody의 각 tr에서 td 텍스트를 리스트로 뽑아 2차원 리스트로 누적합니다.

table = soup.select_one("table#assets")

\# 헤더: thead의 th 텍스트를 리스트로

headers = \[th.get_text(strip=True) for th in table.select("thead th")\]

\# \['hostname', 'ip', 'status', 'owner'\]

\# 데이터: tbody의 각 tr을 돌며 td 텍스트를 리스트로

rows = \[\]

for tr in table.select("tbody tr"):

cells = \[td.get_text(strip=True) for td in tr.select("td")\]

rows.append(cells)

\# \[\['gw-seoul-01','10.0.0.1',...\], \['api-busan-02','10.0.0.2',...\]\]

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 헤더는 thead th, 행은 tbody tr → td</strong></p>
<p>표 스크래핑은 이중 for 패턴입니다: <strong>thead th</strong>로 컬럼명을 한 번 뽑고, <strong>tbody tr</strong>을 돌며 각 행의 <strong>td 셀 텍스트</strong>를 리스트로 만들어 rows에 누적합니다. 이렇게 얻은 headers·rows는 곧바로 <strong>pd.DataFrame(rows, columns=headers)</strong>로 표로 바꿀 수 있습니다.</p></td>
</tr>
</tbody>
</table>

8\. 통합 실습 (파싱 함수 → DataFrame)

카드 목록을 **딕셔너리 리스트**로 파싱하는 함수를 만들면, 그대로 DataFrame으로 바꿔 필터·집계까지 이어집니다.

def parse_advisories(soup):

out = \[\]

for art in soup.select("article.advisory"):

sev = art.select_one("span.severity")

out.append({

"cve": art.get("data-cve", ""),

"title": art.select_one("h3.title").get_text(strip=True),

"severity": sev.get_text(strip=True) if sev else "Unknown",

})

return out

soup = BeautifulSoup(requests.get(url, timeout=5).text, "html.parser")

df = pd.DataFrame(parse_advisories(soup)) \# 딕셔너리 리스트 → DataFrame

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 정적 수집 파이프라인: 요청→파싱→선택→추출→DataFrame</strong></p>
<p>전체 흐름은 <strong>① requests.get → ② BeautifulSoup(html) → ③ select/select_one → ④ get/get_text → ⑤ DataFrame</strong>입니다. select_one이 None을 반환해도 파싱이 멈추지 않도록 <strong>if sev else "Unknown"</strong>처럼 기본값으로 방어하고, 딕셔너리 리스트로 모은 뒤 DataFrame으로 만들어 12·09·10장에서 배운 필터·groupby로 이어갑니다.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 Ch13 핵심 3</strong></p>
<p>① <strong>View Source로 정적/동적 판단</strong> — 가능하면 API&gt;정적&gt;Selenium. ② <strong>find(태그·속성)·select(CSS 선택자)</strong>로 요소를 찾고, select_one의 None을 항상 확인. ③ 값은 <strong>.get()(속성)·.get_text(strip=True)(텍스트)</strong>로 뽑아 딕셔너리 리스트 → DataFrame으로 잇는다.</p></td>
</tr>
</tbody>
</table>
