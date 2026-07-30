**10. 그룹 집계 (groupby · pivot)**

apply·map · split-apply-combine · agg · pivot_table · cut

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1. apply · map 으로 파생 열

정제된 표에 원본에 없는 **파생 열**을 만듭니다. **apply(axis=1)**은 한 행의 여러 열을 조합해 새 값을 만들고, **Series.map(dict)**은 한 열의 값을 1:1로 치환합니다.

import pandas as pd

\# apply(axis=1): 각 행(row)을 받아 여러 열을 조합

LOGS["risk"] = LOGS.apply(lambda r: r["bytes"] * (r["result"]=="fail"), axis=1)

\# map(dict): 한 열의 값을 딕셔너리로 1:1 치환

LOGS["grade"] = LOGS["result"].map({"fail": "F", "ok": "S"})

\# ['F','F','S','F','F','S','F','S','F']

\# dict에 없는 키는 NaN → isna()로 룩업 누락 탐지

> **💡 apply=행 조합, map=값 룩업**
> **apply(axis=1)**은 행 단위로 여러 열을 조합, **apply(axis=0)**은 열별 통계입니다. **map(dict)**은 한 열 값을 딕셔너리로 1:1 치환하며, **dict에 없는 키는 NaN**이 되므로 isna()로 룩업 누락을 잡습니다. for 루프 없이 열 전체에 벡터화 적용됩니다.

2. 집계의 원리 (split-apply-combine)

**groupby**는 **split → apply → combine** 세 단계로 표를 요약합니다. 키가 같은 행끼리 그룹으로 나누고(split), 각 그룹에 집계 함수를 적용하고(apply), 그 결과를 하나의 Series·DataFrame으로 합칩니다(combine).

LOGS.groupby("src_ip").size()

\# src_ip 값이 같은 행끼리 그룹으로 나눈 뒤 각 그룹의 행 수를 셈

\# 172.16.0.10 → 4, 172.16.0.33 → 3, 172.16.0.55 → 2

LOGS.groupby("src_ip")["bytes"].sum() \# 그룹별 합계

LOGS.groupby("src_ip")["bytes"].agg(["sum","mean"]) \# 여러 통계 한 번에

> **💡 Pandas 그룹 연산은 C 레벨로 빠르다**
> 그룹별 연산을 파이썬 for 루프로 짜지 않고 **groupby(...).집계함수()** 한 줄로 표현합니다. Pandas가 내부에서 C 레벨로 일괄 처리해 훨씬 빠릅니다. size()·sum()·mean()·agg([...])를 붙여 그룹별 통계를 구하고, 결과는 그룹 키가 인덱스가 된 하나의 표로 모입니다.

3. 단일 키 집계 (size vs count · named agg)

**size()**는 전체 행 수(NaN 포함)를, **count()**는 **값이 있는 행만** 셉니다. 결측이 없으면 둘이 같지만, NaN이 섞이면 달라집니다 — 발생 '건수'는 size()로 구해야 합니다.

g = LOGS.groupby("src_ip")["bytes"]

g.size() \# 전체 행 수 (NaN 포함)

g.count() \# NaN 아닌 값만 카운트

\# named agg: 결과 열 이름 = ("원본열", "집계함수")

report = LOGS.groupby("src_ip").agg(

total=("bytes", "sum"),

avg=("bytes", "mean"),

fails=("result", lambda s: (s=="fail").sum()),

)

\# total avg fails

\# 172.16.0.10 3840 960.0 3

> **💡 건수는 size, named agg로 의미 있는 열 이름**
> **size()=전체 행 수(NaN 포함), count()=유효값 수**. 발생 건수는 size()로 셉니다. **named agg**는 **이름=("열", "함수")** 문법으로 결과 열 이름을 직접 지정해(total·avg·fails 등) 후속 분석에 바로 쓸 수 있는 보고서를 만듭니다.

4. 다중 키 집계 (MultiIndex)

리스트로 두 열을 주면 **두 키의 조합마다** 그룹이 만들어집니다. 같은 IP라도 result 값에 따라 다른 그룹으로 나뉘고, 결과는 두 키가 합쳐진 **MultiIndex(계층 인덱스)**로 반환됩니다.

LOGS.groupby(["src_ip", "result"]).size()

\# src_ip result

\# 172.16.0.10 fail 3

\# ok 1 ← 같은 IP도 fail/ok로 나뉨

\# 172.16.0.33 fail 2

\# ...

> **💡 두 키 → MultiIndex, 긴 형태는 pivot으로 펼침**
> **groupby(["a","b"])**는 두 키의 조합마다 그룹을 만들고 결과 인덱스가 **MultiIndex**가 됩니다. size()로 각 조합의 건수를 셉니다. 이런 '긴(long) 형태'는 뒤에서 **pivot_table**로 가로로 펼쳐 읽기 쉬운 교차표(보고서)로 만듭니다.

5. 사용자 함수 (agg 커스텀 · apply 요약)

**agg()**는 'mean' 같은 문자열 대신 **람다·사용자 정의 함수**도 집계 함수로 받습니다. 각 함수는 그룹의 Series 하나를 받아 스칼라 값을 반환합니다.

def byte_range(s): \# Series를 받아 max - min 반환

return s.max() - s.min()

LOGS.groupby("src_ip").agg(

byte_range=("bytes", byte_range),

fail_rate=("result", lambda s: (s=="fail").mean()),

)

**groupby(...).apply(summary)**는 그룹 DataFrame 전체를 함수에 넘겨 여러 열을 동시에 요약합니다. 함수가 **pd.Series({...})**를 반환하면 각 그룹이 요약표의 한 행이 됩니다.

def summary(g): \# g = 그룹 전체(서브 DataFrame)

return pd.Series({

"n": len(g),

"fail_rate": (g["result"]=="fail").mean(),

"top_bytes": g["bytes"].max(),

})

LOGS.groupby("src_ip").apply(summary, include_groups=False)

> **💡 agg=열 하나씩, apply=그룹 전체**
> **agg**는 그룹의 한 열(Series)을 받아 스칼라를 돌려주는 함수를(min·max·람다) 씁니다. **apply**는 그룹 DataFrame 전체를 받아 여러 열을 조합한 요약 행(pd.Series)을 만들 때 씁니다. **include_groups=False**로 그룹 키 열을 입력에서 제외합니다.

6. pivot_table (교차표 · long→wide)

**pivot_table**은 긴(long) 형태의 표를 가로로 펼친 교차표(wide)로 만듭니다. 한 열을 행 인덱스로, 다른 열을 열 헤더로 배치하고, 값을 집계 함수로 모읍니다.

LOGS.pivot_table(

index="src_ip", \# 행 = src_ip

columns="result", \# 열 = result (fail / ok)

values="bytes", \# 셀 값 = bytes

aggfunc="sum", \# 같은 (src_ip, result) 조합은 합계로 집계

fill_value=0, \# 나타나지 않는 조합은 0으로 채움

)

\# result fail ok

\# src_ip

\# 172.16.0.10 1792 2048

\# 172.16.0.33 320 64

> **💡 index=행, columns=열, fill_value로 빈칸 0**
> 교차표는 **index=행, columns=열, values=셀 값, aggfunc=집계 방법**으로 구성합니다. 같은 조합의 값은 aggfunc로 모으고, 데이터에 없는 조합은 **fill_value=0**으로 채워 깔끔한 정수형 리포트를 완성합니다. groupby+size의 긴 결과를 읽기 쉽게 펼치는 도구입니다.

7. 빈도 · 구간화 (value_counts · cut)

**value_counts()**는 각 값의 출현 빈도를 셉니다. **normalize=True**면 전체 대비 비율을, **head(N)**을 이으면 상위 N개만 뽑습니다.

LOGS["src_ip"].value_counts(normalize=True).round(2)

\# 172.16.0.10 0.44 ← 전체 대비 비율

\# 172.16.0.33 0.33

LOGS["src_ip"].value_counts().head(2) \# 상위 2개 출처 IP

**pd.cut()**은 연속형 숫자를 **지정한 절대 경계(bins)**로 구간에 할당합니다. labels로 구간 이름을 붙이고, if-elif를 일일이 쓰는 대신 경계 리스트 하나로 구간화합니다.

sizes = pd.cut(LOGS["bytes"], bins=[0, 100, 500, 2500],

labels=["small", "medium", "large"])

sizes.value_counts().reindex(["small","medium","large"])

\# small 1, medium 4, large 4

\# 주의: bins 범위 밖 값(0 이하·2500 초과)은 NaN

\# → include_lowest=True 또는 범위 확인 필요

> **💡 비율은 normalize, 구간화는 cut(bins)**
> **value_counts(normalize=True)**는 비율을, head(N)은 상위 N개를 줍니다. **pd.cut(bins=[...], labels=[...])**은 연속값을 고정 경계로 구간화하되, **경계 밖 값은 NaN**이 되므로 include_lowest나 범위 점검이 필요합니다. (참고: qcut은 동일 개수로 나누는 분위 구간화)

8. 통합 실습 (IP별 실패율)

groupby와 agg로 IP별 전체 시도와 실패 횟수를 한 표에 만들고, 실패율이 임계값(threshold) 이상인 IP를 정렬해 리스트로 반환하는 흐름입니다.

def suspects(df, threshold=0.7):

by_ip = df.groupby("src_ip").agg(

total=("result", "size"), \# 전체 시도

fail=("result", lambda s: (s=="fail").sum()), \# 실패 건수

)

rate = by_ip["fail"] / by_ip["total"] \# 실패율

hot = rate[rate >= threshold].sort_values(ascending=False)

return hot.index.tolist()

\# 실패 집중 IP(실패율 ≥ 0.7): ['10.0.0.5', '198.51.100.9', '203.0.113.7']

> **💡 집계 → 파생 비율 → 필터 → 정렬의 표준 흐름**
> ① groupby+agg로 **전체(size)와 실패(조건 sum)**를 한 표에 집계, ② **실패 = fail / total**로 비율 파생, ③ 불리언 마스크로 threshold 이상만 필터, ④ sort_values로 정렬해 리스트 반환. 이 챕터의 groupby·agg·불리언 필터를 한 번에 쓰는 종합 패턴입니다.

> **💡 Ch10 핵심 3**
> ① **groupby = split-apply-combine** — 키로 나눠 size·sum·mean·agg로 집계. ② **named agg·사용자 함수·apply**로 의미 있는 열 이름의 요약 보고서 생성. ③ **pivot_table(교차표)·value_counts(빈도/비율)·cut(구간화)**로 결과를 읽기 쉬운 리포트로 재구성. 최종 패턴은 집계→비율 파생→필터→정렬입니다.
