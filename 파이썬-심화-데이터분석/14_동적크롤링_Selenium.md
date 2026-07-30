**14. 동적 크롤링 (Selenium)**

webdriver · 요소 찾기 · 대기 · 상호작용 · 무한 스크롤 · page_source

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1. WebDriver 설정 (Options)

동적 페이지는 **자바스크립트가 화면을 채우므로** requests로는 빈 화면만 옵니다. Selenium은 **브라우저를 띄워 JS 실행을 기다렸다가** 수집합니다. headless와 window-size 두 옵션이 핵심입니다.

from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options

opts = Options()

opts.add_argument("--headless=new") \# 창 없이 백그라운드(서버 필수)

opts.add_argument("--window-size=1920,1080") \# 가상 화면 크기 지정

opts.add_argument("--no-sandbox") \# 컨테이너 환경

opts.add_argument("--user-agent=Mozilla/5.0 (course-bot)") \# 정직한 식별

driver = webdriver.Chrome(options=opts)

> **💡 headless엔 window-size 필수 (반응형 함정)**
> **--headless=new**는 창 없이 백그라운드로 실행합니다(서버에 필수). 다만 headless는 해상도가 미지정이면 **기본 화면이 작게 잡혀** 반응형 사이트가 모바일 레이아웃으로 바뀌고 로그인 버튼이 햄버거 메뉴 안에 숨을 수 있으니 **--window-size=1920,1080**을 명시합니다. user-agent로 우리가 누구인지 정직하게 식별합니다.

2. 요소 찾기 (find_element · By)

**find_element(By.CSS_SELECTOR, ...)**는 조건에 맞는 첫 요소 하나를, **find_elements**는 리스트를 반환합니다. By.CSS_SELECTOR는 13장의 BS4 select와 같은 선택자 문법을 씁니다.

from selenium.webdriver.common.by import By

title = driver.find_element(By.CSS_SELECTOR, "h1") \# 단일 요소

print(title.text) \# 안쪽 텍스트

items = driver.find_elements(By.CSS_SELECTOR, "#items li") \# 리스트

print(len(items))

> **💡 단수 find_element는 None이 아니라 예외**
> **find_element(단수)**는 못 찾으면 None이 아니라 **NoSuchElementException으로 중단**됩니다. 반드시 있을 요소(로그인 입력칸 등)에만 쓰고, 있을 수도 없을 수도 있으면 **find_elements(복수)**를 써서 **빈 리스트**로 안전하게 받거나 try/except로 감쌉니다.

3. 대기 전략 (WebDriverWait)

렌더링은 비동기라 get() 직후엔 원하는 요소가 아직 DOM에 없을 수 있습니다. **고정 sleep은 도박**입니다 — 빠르면 시간 낭비, 느리면 요소를 못 찾아 실패합니다.

time.sleep(3) \# ✗ 빠르면 2초 낭비, 느리면 3초 뒤에도 실패

**WebDriverWait**는 조건이 충족될 때까지만 기다렸다가 즉시 통과하는 **폴링 대기** 객체입니다. **expected_conditions(EC)**가 무엇을 기다릴지 지정하고, 시간 초과 시 **TimeoutException**을 던집니다.

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

wait = WebDriverWait(driver, 10) \# 최대 10초, 0.5초 간격 폴링

\# 존재(presence) / 클릭 가능(clickable) 구분

el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#items")))

btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit")))

> **💡 고정 sleep 대신 조건 충족 즉시 통과**
> **WebDriverWait(driver, 10).until(EC...)**는 조건이 참이 될 때까지만 폴링하다 **충족되는 즉시 진행**하므로 빠르면 빨리, 느리면 최대 10초까지 기다립니다. **presence(DOM에 존재)**와 **clickable(클릭 가능)**을 구분해서 쓰고, 시간 초과 시 TimeoutException으로 실패를 명확히 합니다.

4. 상호작용 (입력 · 클릭 · 전환 검증)

**send_keys**로 입력칸에 타이핑하고 **click**으로 버튼을 누릅니다. 로그인 폼은 각 요소를 id 선택자로 집습니다(예: \#username, \#password, \#submit).

driver.get("http://localhost:8800/login")

driver.find_element(By.CSS_SELECTOR, "#username").send_keys("student")

driver.find_element(By.CSS_SELECTOR, "#password").send_keys("pass1234")

driver.find_element(By.CSS_SELECTOR, "#submit").click()

**click은 전환을 시작할 뿐 완료 신호가 아닙니다.** 클릭 직후 바로 다음 화면을 읽으면 아직 이전 페이지라 깨집니다. **EC.url_contains**로 주소 전환 완료를 기다린 뒤 읽습니다.

\# 전환 완료까지 대기 후 검증

wait.until(EC.url_contains("/dashboard"))

welcome = driver.find_element(By.CSS_SELECTOR, ".welcome").text

> **💡 click 후 반드시 전환 완료를 대기**
> 클릭 직후엔 JS가 화면을 다시 그리는 중이라 아직 이전 페이지입니다. 대기 없이 바로 읽으면 이전 페이지를 긁어 깨집니다. **URL 변경(url_contains)·환영 메시지 등 전환 완료 증거를 명시적으로 대기**한 뒤 다음 요소를 읽어야 합니다.

5. 무한 스크롤 (execute_script)

무한 스크롤은 한 번에 다 주지 않고 **아래로 내릴 때마다 JS가 다음 묶음을 붙입니다.** 그래서 화면을 끝까지 내려야 전부 모입니다. 파이썬으로 못 하는 스크롤은 **execute_script**로 브라우저 안에서 JS를 직접 실행합니다.

last = driver.execute_script("return document.body.scrollHeight")

while True:

driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

time.sleep(1) \# 새 묶음 로드 대기

new = driver.execute_script("return document.body.scrollHeight")

if new == last: \# 높이 안 늘면 끝까지 로드됨

break

last = new

\# 루프 종료 = 전부 로드 완료 → 한 번에 수집

items = driver.find_elements(By.CSS_SELECTOR, "#items li")

print("수집:", len(items), "건") \# 200건

> **💡 scrollHeight가 안 늘 때까지 · append vs extend**
> 맨 아래로 스크롤 → 로드 대기 → **scrollHeight 비교**를 높이가 변하지 않을 때까지 반복하면 끝까지 로드됩니다. 여러 회차를 누적할 때 **append는 리스트를 통째로 넣어 중첩([[...],[...]])**되고, **extend는 원소를 풀어 한 줄로 평탄화**합니다. 전체 항목은 마지막에 find_elements로 한 번에 셉니다.

6. Selenium → BeautifulSoup 추출

**selenium은 화면 완성까지만 맡고, 추출은 BeautifulSoup에 넘깁니다.** 스크롤·클릭으로 동적 페이지를 끝까지 렌더한 뒤 **page_source**로 현재 화면의 HTML 전체를 꺼내 13장 그대로 파싱합니다.

from bs4 import BeautifulSoup

html = driver.page_source \# 지금 렌더된 화면의 HTML 전체

soup = BeautifulSoup(html, "html.parser") \# 13장의 그 BeautifulSoup

items = [li.text.strip() for li in soup.select("#items li")]

driver.quit() \# 추출 끝났으면 브라우저 종료

> **💡 find_element 반복보다 page_source 한 번이 빠르다**
> **find_element를 요소마다 반복**하면 매번 browser↔︎python 왕복이라 느립니다. 대신 **page_source로 HTML 전체를 한 번에 꺼내 BeautifulSoup으로 파싱**하면 find·select·.text를 13장처럼 빠르게 쓸 수 있습니다. 추출이 끝나면 **driver.quit()**으로 브라우저를 반드시 종료합니다.

7. 통합 실습 (드라이버 수명주기)

로그인·전환·무한 스크롤을 한 흐름으로 잇되, **try/finally로 driver.quit()을 보장**해 예외가 나도 브라우저가 남지 않게 합니다.

driver = webdriver.Chrome(options=opts)

try:

driver.get("http://localhost:8800/login")

\# ① 입력 → ② 제출

driver.find_element(By.CSS_SELECTOR, "#username").send_keys("student")

driver.find_element(By.CSS_SELECTOR, "#password").send_keys("pass1234")

driver.find_element(By.CSS_SELECTOR, "#submit").click()

\# ③ 전환 확인

wait.until(EC.url_contains("/dashboard"))

\# ④ 스크롤 → page_source → BS4 추출

soup = BeautifulSoup(driver.page_source, "html.parser")

finally:

driver.quit() \# 예외가 나도 반드시 종료

> **💡 동적 수집 파이프라인: 옵션→열기→대기→상호작용→추출→종료**
> 전체 흐름은 **① Options → ② driver.get → ③ WebDriverWait로 대기 → ④ send_keys·click·scroll 상호작용 → ⑤ page_source→BeautifulSoup 추출 → ⑥ finally: quit()**입니다. 드라이버는 자원을 잡으므로 **try/finally로 종료를 보장**하는 것이 수명주기 관리의 핵심입니다.

> **💡 Ch14 핵심 3**
> ① 동적은 최후의 수단 — **API &gt; 정적(requests+BS4) &gt; 동적(Selenium)**, headless+window-size로 서버 구동. ② 대기는 **WebDriverWait+EC로 조건 충족 즉시** — 고정 sleep 금지, click 후 전환도 대기 검증. ③ **selenium은 화면 완성, page_source→BS4로 추출 분업**, try/finally로 quit 보장.
