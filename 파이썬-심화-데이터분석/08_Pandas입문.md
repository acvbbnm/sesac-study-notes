**08. Pandas 입문**

Series · DataFrame · read_csv · loc/iloc · 불리언 필터

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1. Series 기초

**Series** 는 1차원 배열에 인덱스 라벨을 더한 구조, **DataFrame** 은 여러 Series를 열로 결합한 2차원 표입니다. 둘 다 NumPy 배열 위에 라벨을 얹은 것.

import pandas as pd

s = pd.Series([100, 200, 300]) \# 인덱스 0,1,2 자동

s = pd.Series([100, 200, 300], index=["월","화","수"]) \# 라벨 지정

s["화"] \# 200 라벨로 조회

s[["월","수"]] \# 여러 라벨 → 새 Series

s.iloc[1] \# 200 정수 위치로 조회

s.index.tolist() \# ['월','화','수'] 라벨 목록

s.values \# [100 200 300] 값 (NumPy 배열)

> **💡 라벨 인덱스 / .index·.values는 속성**
> **s["화"]와 s.iloc[1]은 같은 값**을 줍니다(라벨 vs 위치). 라벨을 리스트로 묶으면 여러 원소를 골라 새 Series로 받습니다. **.index·.values는 속성**이라 괄호를 쓰지 않습니다. 스칼라 곱(s*2)은 모든 원소에 적용됩니다.

2. DataFrame 생성 · 입출력

\# dict로 생성: 키=열 이름, 값=열 데이터

df = pd.DataFrame({

"src_ip": ["10.0.0.5", "10.0.0.9"],

"status": [200, 403],

}, index=["r1", "r2"]) \# index=로 행 라벨 지정

\# CSV 읽기

df = pd.read_csv("logs.csv") \# 첫 줄=열 이름, 왼쪽=자동 index

df = pd.read_csv("logs.csv", index_col="src_ip") \# 특정 열을 index로

df = pd.read_csv("logs.csv", usecols=["src_ip","status"]) \# 필요한 열만

df = pd.read_csv("logs.csv", parse_dates=["timestamp"]) \# 날짜→datetime64

> **💡 read_csv 옵션 4가지**
> **index_col:** 특정 열을 행 인덱스로. **usecols:** 지정한 열만 읽어 메모리 절약. **parse_dates:** 문자열 날짜를 datetime64로 변환(안 하면 str이라 날짜 연산·정렬이 안 됨).

3. 탐색 · 파생 열 · 저장

df.dtypes \# 열별 데이터 타입 (숫자여야 할 열이 str이면 정제 필요 신호)

df["status"] \# 단일 열 → Series (1차원)

df[["src_ip","status"]] \# 열 리스트 → DataFrame (2차원, 대괄호 2개)

\# 파생 열: 산술 연산은 모든 행에 적용

df["kb"] = (df["bytes"] / 1024).round(2)

df.to_csv("report.csv", index=False) \# 저장 (index=False로 행번호 제외)

> **💡 단일 열=Series, 복수 열=DataFrame**
> **df["status"]** 는 Series를, **df[["src_ip","status"]]** 는 DataFrame을 반환합니다(대괄호 개수 차이). 열에 산술 연산을 하면 모든 행에 한 번에 계산된 파생 열이 생깁니다. dtypes로 숫자열이 문자열로 읽혔는지 미리 확인하세요.

4. loc vs iloc (행·열 선택)

|             | **iloc**                       | **loc**                        |
|-------------|--------------------------------|--------------------------------|
| 기준        | **정수 위치**(번호)            | **이름(라벨)**                 |
| 문법        | df.iloc[행번호, 열번호]      | df.loc[행라벨, 열이름]       |
| 슬라이스 끝 | 끝 번호 **미포함** (0:2 → 0·1) | 끝 라벨 **포함** (1:3 → 1·2·3) |
| 다중 선택   | df.iloc[[0,3],[1,2]]     | df.loc[["a","b"],["c"]]  |

df.iloc[0:2] \# 위치 0·1 행 (끝 2 미포함)

df.iloc[[0, 3], [1, 2]] \# 떨어진 0·3행 x 1·2열 콕 집어 선택

df = df.set_index("src_ip") \# 특정 열을 행 라벨로

df.loc[["10.0.0.9", "10.0.0.2"], ["status"]] \# 라벨로 선택

df.loc[1:3] \# 끝 라벨 3 포함 → 1·2·3

> **💡 끝 인덱스 처리가 결정적 차이**
> **iloc = integer(위치)**, **loc = label(이름)**. 슬라이스에서 **iloc는 끝 미포함, loc는 끝 포함**입니다(loc[1:3]은 3까지 3개). 리스트로 주면 떨어진 행·열도 콕 집어 다중 선택할 수 있습니다. set_index로 특정 열을 행 라벨로 올려 loc로 조회합니다.

5. 불리언 필터링

열 값과 기준을 비교하면 각 행의 조건 충족 여부를 담은 **불리언 마스크**가 생깁니다. 마스크를 넣으면 True인 행만 남습니다.

df[df["점수"] >= 60] \# 60 이상인 행만

df[df["이름"].isin(["나","라"])] \# 목록에 포함된 행만

\# 여러 조건: and/or 대신 & \| , 각 조건은 소괄호로!

df[(df["점수"] >= 60) & (df["반"] == "A")]

> **💡 and/or 금지 → &amp;/| + 소괄호**
> 파이썬의 **and·or는 Series 전체의 참/거짓을 한 번에 판단하려다 ValueError**를 냅니다. 여러 조건은 **&amp; (그리고), | (또는)** 비트 연산자를 쓰고, 우선순위 때문에 **각 조건을 소괄호로 감싸야** 합니다. **isin([...])** 은 여러 값 중 하나에 해당하는 행을 한 번에 고릅니다.

6. 값 수정 · 삭제

\# 한 셀 수정: at (행 라벨, 열 이름)

df.at["e2", "status"] = 503 \# 그 셀만 변경, 나머지 유지

\# 파생 열 추가 (조건 → 불리언 열)

df["is_error"] = df["status"] >= 400

\# 열 삭제: drop

df = df.drop(columns=["bytes"]) \# bytes 열 제거 후 재할당

> **💡 한 칸은 at, 범위는 loc/iloc**
> **df.at[행, 열]** 은 한 셀만 빠르게 수정합니다(범위는 loc/iloc). **df.drop(columns=[...])** 은 열을 삭제한 새 DataFrame을 반환하므로 다시 대입해야 반영됩니다. 조건식으로 만든 불리언 열(is_error)을 마스크로 다시 써서 에러 행만 뽑는 흐름이 종합 실습의 핵심입니다.

> **💡 Ch08 핵심 3**
> ① Series(1D)·DataFrame(2D)를 dict나 read_csv로 만들고 dtypes로 점검, ② **loc(이름)·iloc(위치)**로 행·열 선택(끝 포함 규칙 주의), ③ 불리언 마스크(&amp;/|+소괄호)로 조건 필터 + at·drop으로 수정·삭제. 이 세 가지가 핵심입니다.
