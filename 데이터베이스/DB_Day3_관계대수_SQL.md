**데이터베이스 Day 3**

관계대수(Relational Algebra) · SQL 개요

데이터베이스 교안 정리 (요약 · 보충 · 퀴즈)

목차

6\. 관계대수 (Relational Algebra)

**관계대수** : 릴레이션에서 원하는 결과를 얻기 위한 연산을 기술하는 **절차적 언어**(어떻게 찾는지 절차를 명시). DBMS 내부의 처리 언어이며, 결과도 릴레이션으로 반환됩니다.

순수 관계 연산자

| **연산자** | **기호** | **설명** |
|----|----|----|
| 셀렉션(Selection) | σ (시그마) | 릴레이션에서 **조건에 맞는 튜플(행)** 선택 |
| 프로젝션(Projection) | π (파이) | 릴레이션에서 **원하는 속성(열)** 선택 |
| 조인(Join) | ⋈ | 두 릴레이션의 카티전 프로덕트 중 조건에 맞는 튜플 결합 |
| 디비전(Division) | ÷ | 분자 릴레이션의 모든 값을 포함하는 튜플의 나머지 반환 |

일반 집합 연산자

| **연산자**           | **기호** | **설명**                             |
|----------------------|----------|--------------------------------------|
| 합집합(Union)        | ∪        | 두 릴레이션의 합집합 (중복 제거)     |
| 차집합(Difference)   | \-       | R1에만 있고 R2에 없는 튜플           |
| 교집합(Intersection) | ∩        | 두 릴레이션 모두에 있는 튜플         |
| 카티전 프로덕트      | ×        | 두 릴레이션 튜플의 모든 조합(곱집합) |

**조인의 종류** : 세타 조인(비교 조건), 동등 조인(=), **자연 조인(동등 조인에서 중복 속성 제거)**, 세미 조인(한쪽 속성만 남김), **외부 조인(left/right/full — 실패한 쪽을 NULL로 채움)**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 셀렉션은 가로(행), 프로젝션은 세로(열)</strong></p>
<p><strong>셀렉션(σ)은 조건에 맞는 행을 잘라내고, 프로젝션(π)은 원하는 열만 뽑습니다.</strong> 관계대수는 SQL의 이론적 토대로, 결과가 항상 릴레이션이라 연산을 계속 이어붙일 수 있습니다(닫힘 성질). 자연 조인은 공통 속성으로 두 표를 합치되 중복 열을 하나로 정리한 것이라 실무에서 가장 많이 쓰입니다.</p></td>
</tr>
</tbody>
</table>

7\. SQL 개요

실습용 **마당서점 데이터베이스**는 세 릴레이션으로 구성됩니다(밑줄=기본키).

Book(bookid, bookname, publisher, price)

Orders(orderid, custid, bookid, saleprice, orderdate)

Customer(custid, name, address, phone)

\# 기본키: bookid, orderid, custid

\# 외래키: Orders.custid → Customer.custid, Orders.bookid → Book.bookid

**SQL** : 데이터베이스에서 데이터를 추출·조작하는 언어. **입력도 테이블, 출력도 테이블**이며 번역은 DBMS가 담당합니다(일반 언어는 컴파일러).

SQL 기능별 분류

| **분류** | **용도** | **주요 명령어** |
|----|----|----|
| 데이터 정의어(DDL) | 테이블·구조 생성·변경·삭제 | **CREATE · ALTER · DROP** |
| 데이터 조작어(DML) | 데이터 검색·삽입·수정·삭제 | **SELECT · INSERT · UPDATE · DELETE** |
| 데이터 제어어(DCL) | 사용 권한 관리 | **GRANT · REVOKE** |

SELECT publisher, price -- 프로젝션(열 선택)

FROM Book -- 대상 릴레이션

WHERE bookname = '축구의 역사'; -- 셀렉션(행 조건)

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 SQL = 관계대수의 실무 구현</strong></p>
<p>SQL의 <strong>SELECT 절은 프로젝션(π), WHERE 절은 셀렉션(σ)</strong>에 대응합니다. 즉 관계대수가 이론, SQL이 그 실무 구현입니다. 명령어는 <strong>DDL(구조)·DML(데이터)·DCL(권한)</strong> 세 갈래로 나뉘며, 이 중 DML의 SELECT가 조회의 핵심입니다.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<td><p><strong>💡 전체 마무리</strong></p>
<p>Day1 <strong>DBMS·독립성</strong> → Day2 <strong>관계모델·키·무결성</strong> → Day3 <strong>관계대수→SQL</strong>. 관계대수의 셀렉션·프로젝션이 SQL의 WHERE·SELECT로 이어지며 이론이 실무로 완성된다.</p></td>
</tr>
</tbody>
</table>
