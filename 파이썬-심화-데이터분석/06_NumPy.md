**06. NumPy 기초**

배열 생성·dtype · 인덱싱 · 불리언 마스크 · 변형·집계

슬라이드 정리본 (요약 · 보충 · 퀴즈)

목차

1\. 왜 NumPy — 원소별 연산

리스트에 정수를 곱하면 리스트가 **반복(복제)**되지만, 배열에 곱하면 **각 원소에 곱셈이 적용**됩니다. NumPy는 반복문 없이 배열 전체를 통째로 계산합니다.

import numpy as np

\[1, 2, 3\] \* 3 \# \[1,2,3,1,2,3,1,2,3\] ← 반복(복제)

np.array(\[1, 2, 3\]) \* 3 \# \[3 6 9\] ← 원소별 계산

scores = np.array(\[80, 90, 70\])

scores + 5 \# \[85 95 75\] 전체 +5

scores \* 10 \# \[800 900 700\] 전체 \*10

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 NumPy의 핵심 = 반복문 없는 벡터 연산</strong></p>
<p>배열은 원소를 <strong>하나의 dtype</strong>으로 저장해, +5·*10 같은 연산을 모든 원소에 한 번에 적용합니다. 이 '벡터화'가 파이썬 리스트보다 빠르고 간결한 이유입니다.</p></td>
</tr>
</tbody>
</table>

2\. 배열 생성과 dtype

a = np.array(\[1, 2, 3\]) \# 리스트 → 배열, a.dtype = int64

np.zeros(3) \# \[0. 0. 0.\] 1차원 0 배열

np.zeros((2, 3)) \# 2x3 0 배열 (모양은 (행,열) 튜플)

np.arange(0, 10, 2) \# \[0 2 4 6 8\] 끝값 미포함 (range와 동일)

np.linspace(0, 1, 5) \# \[0. 0.25 0.5 0.75 1.\] 끝 포함, 5개 균등

한 배열 한 dtype (자동 승격)

| **입력**        | **dtype** | **해석**                  |
|-----------------|-----------|---------------------------|
| \[1, 2, 3\]     | int64     | 정수 배열                 |
| \[1, 2.5, 3\]   | float64   | 소수 섞이면 전체 float    |
| \[True, False\] | bool      | 마스크의 재료             |
| \[1, "2", 3\]   | \<U21     | 타입 섞이면 문자열로 통일 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 dtype 자동 추론 / arange vs linspace</strong></p>
<p>배열은 하나의 dtype으로 모든 원소를 저장하므로, 자료형이 섞이면 <strong>모두 표현 가능한 공통 타입으로 승격</strong>합니다(정수+소수→float64, 숫자+문자→문자열).</p>
<p><strong>arange는 '간격' 지정·끝값 미포함</strong>, <strong>linspace는 '개수' 지정·끝값 포함</strong>. 소수 간격이 필요하면 arange보다 linspace가 오차 없이 안전합니다.</p></td>
</tr>
</tbody>
</table>

배열 정보 — 속성 3종

| **속성**  | **의미**                 | **예 (2x3 배열)** |
|-----------|--------------------------|-------------------|
| **shape** | 각 축 크기 (행, 열) 튜플 | (2, 3)            |
| **ndim**  | 차원(축) 개수            | 2                 |
| **size**  | 전체 원소 수 (행x열)     | 6                 |
| **dtype** | 원소 자료형              | float64           |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 shape에는 괄호가 없다</strong></p>
<p><strong>shape·ndim·size·dtype은 모두 '속성'</strong>이라 arr.shape처럼 <strong>괄호 없이</strong> 씁니다(메서드 아님). 1차원 배열의 shape는 (n,) 형태입니다.</p></td>
</tr>
</tbody>
</table>

3\. 인덱싱·슬라이싱 (2차원)

2차원 배열은 행과 열로 된 표입니다. 값 선택은 **X\[행, 열\]** — 항상 행이 먼저.

X = np.array(\[\[85, 90, 80\],

\[70, 95, 60\],

\[88, 75, 92\]\])

X\[0\] \# \[85 90 80\] 첫 번째 행 전체 (1차원)

X\[:, 1\] \# \[90 95 75\] 모든 행의 2번째 열 (콜론=그 축 전부)

X\[1:3, :2\] \# \[\[70 95\],\[88 75\]\] 1~2번 행 x 0~1번 열 (끝 미포함)

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 콜론(:)은 '그 축 전부' / 끝은 미포함</strong></p>
<p><strong>X[1]은 행을, X[:, 1]은 열을</strong> 선택합니다. 콜론 <strong>:</strong> 은 해당 축 전체를 뜻해요. 슬라이싱의 끝 인덱스는 미포함이라 <strong>1:3은 1·2번</strong>만 고릅니다(파이썬 규칙과 동일).</p></td>
</tr>
</tbody>
</table>

4\. 불리언 인덱싱 (마스크)

배열을 값과 비교하면 각 원소의 조건 충족 여부를 담은 **bool 배열(마스크)**이 생깁니다. 반복문·append 필터링을 배열 연산 한 번으로 대체합니다.

scores = np.array(\[85, 92, 58, 77, 95\])

mask = scores \> 90 \# \[False True False False True\] ← 마스크

scores\[mask\] \# \[92 95\] True 위치의 값만 추출

\# 조건부 일괄 수정 (원본 직접 변경)

scores\[scores \< 60\] = 0 \# 60 미만만 0으로 → \[85 92 0 77 95\]

슬라이싱은 원본과 공유 (view) — copy()

col = X\[:, 0\] \# 뷰(view): 원본과 메모리 공유

col\[0\] = 99 \# → 원본 X\[0,0\]도 99로 바뀜!

col = X\[:, 0\].copy() \# 독립 복사본 → 원본 보존

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 마스크 결과 vs 뷰 / 팬시 인덱싱</strong></p>
<p><strong>마스크(불리언 인덱싱)와 팬시 인덱싱(X[[0,2,3]])의 결과는 원본과 독립된 새 배열</strong>이지만, <strong>기본 슬라이싱(X[:,0])은 원본을 공유하는 뷰</strong>입니다. 뷰를 수정하면 원본도 바뀌니, 보존하려면 <strong>.copy()</strong>를 먼저 부르세요.</p>
<p><strong>불리언 마스크는 '조건'으로, 팬시 인덱싱은 '번호'로</strong> 선택합니다. X[[0,2,3]]은 0·2·3번 행을 그 순서대로 뽑습니다.</p></td>
</tr>
</tbody>
</table>

5\. 배열 변형·결합

| **도구** | **동작** | **비고** |
|----|----|----|
| **reshape(행,열)** | 원소 수 유지한 채 모양 변경 | 전후 원소 수 다르면 ValueError |
| **reshape(2,-1)** | 한 축을 -1로 → 자동 계산 | -1은 한 축에만 |
| **flatten()** | 다차원 → 1차원 (행 우선) | 원본과 독립 새 배열 |
| **.T** | 행과 열 교환 (전치) | (행,열) → (열,행) |
| **np.vstack(\[a,b\])** | 세로로 쌓기 (행 증가) | 열 수가 같아야 |
| **np.hstack(\[a,b\])** | 가로로 붙이기 (열 증가) | 행 수가 같아야 |

flat = np.arange(12) \# 0~11

flat.reshape(3, 4) \# 3행 4열 (행 우선 배치)

flat.reshape(2, -1).shape \# (2, 6) → -1이 6을 자동 계산

A = np.array(\[\[1,2\],\[3,4\]\])

A.flatten() \# \[1 2 3 4\]

A.T \# 전치 \[\[1 3\],\[2 4\]\]

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 reshape는 원소 수 유지 / -1은 한 번만</strong></p>
<p><strong>reshape는 전체 원소 수가 같을 때만</strong> 됩니다(12개 = 3x4 성공, 3x5는 ValueError). 한 축을 <strong>-1</strong>로 두면 나머지로 그 축 크기를 자동 계산하는데, -1은 한 축에만 쓸 수 있습니다. vstack은 열 수, hstack은 행 수가 맞아야 결합됩니다.</p></td>
</tr>
</tbody>
</table>

6\. 축(axis) 집계

sum·mean 등은 **axis** 로 집계 방향을 정합니다. 인자가 없으면 전체를 하나의 값으로 합칩니다.

| **호출** | **의미** | **2x3 예 \[\[80,90,70\],\[60,100,50\]\]** |
|----|----|----|
| **M.sum()** | axis 없음 → 전체 합 | 450 (스칼라) |
| **M.sum(axis=0)** | 행 축을 접음 → **열별** 합 | \[140 190 120\] |
| **M.sum(axis=1)** | 열 축을 접음 → **행별** 합 | \[240 210\] |

M = np.array(\[\[80, 90, 70\],

\[60, 100, 50\]\])

M.sum() \# 450 전체 합

M.sum(axis=0) \# \[140 190 120\] 열별(과목별) 합 — 행이 접힘

M.sum(axis=1) \# \[240 210\] 행별(학생별) 합 — 열이 접힘

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 axis=0은 열별, axis=1은 행별 (헷갈림 주의)</strong></p>
<p><strong>axis=0 = 행 축을 접어 위아래로 집계 → 열별 결과</strong>(길이 = 열 수), <strong>axis=1 = 열 축을 접어 좌우로 집계 → 행별 결과</strong>(길이 = 행 수). '접히는 축 번호'를 준다고 기억하면 헷갈리지 않습니다.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 Ch06 핵심 3</strong></p>
<p>① np.array로 한 dtype 배열 생성·shape로 모양 확인, ② 인덱싱(X[행,열])과 불리언 마스크(scores&gt;90)로 값 선택·수정, ③ reshape/.T/vstack/hstack로 모양 바꾸고 sum(axis=0/1)로 축 방향 집계. 이 세 가지가 핵심입니다.</p></td>
</tr>
</tbody>
</table>
