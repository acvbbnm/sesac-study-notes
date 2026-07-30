**Oracle SQL 명령어 실습 보고서**

SELECT · INSERT · UPDATE · DELETE · CREATE · ALTER · DROP

명령어별 기본 설명 · 주요 옵션 · 마당서점 예제

AI를 활용한 보안전문가 양성과정 (새싹 SW 5기)

목차

1. 실습 개요

Oracle 데이터베이스 환경에서 SQL 명령어로 테이블 데이터를 조회·삽입·수정·삭제(DML)하고, DDL 명령어로 스키마·테이블을 생성·수정·삭제하며 데이터베이스 객체 관리와 데이터 처리 절차를 이해한다. 본 보고서는 7개 핵심 명령어를 **기본 설명 → 주요 옵션 → 예제** 순으로 정리한다.

모든 예제는 실습용 **마당서점 데이터베이스** 3개 테이블을 기준으로 한다.

Book(bookid, bookname, publisher, price)

Customer(custid, name, address, phone)

Orders(orderid, custid, bookid, saleprice, orderdate)

-- 기본키: bookid, custid, orderid

-- 외래키: Orders.custid -> Customer, Orders.bookid -> Book

| **분류** | **명령어** | **용도** |
|----|----|----|
| DML (데이터 조작어) | SELECT · INSERT · UPDATE · DELETE | 테이블 안의 **데이터**를 다룸 |
| DDL (데이터 정의어) | CREATE · ALTER · DROP | 테이블·스키마 등 **구조(객체)**를 다룸 |

> **💡 DML은 데이터, DDL은 구조**
> **DML**은 이미 만들어진 테이블 '안의 값'을 조작하고(커밋 필요), **DDL**은 테이블 자체의 '틀'을 만들고 바꿉니다. DDL은 실행 즉시 자동 커밋(auto-commit)되어 롤백이 어렵다는 점이 DML과 큰 차이입니다.

2. SELECT — 데이터 조회

**기본 설명** : 테이블에서 원하는 열과 행을 검색합니다. SQL에서 가장 많이 쓰는 명령으로, 관계대수의 프로젝션(열 선택)과 셀렉션(행 조건)에 대응합니다.

SELECT [DISTINCT] 열목록 -- 프로젝션(열 선택)

FROM 테이블

WHERE 조건 -- 셀렉션(행 조건)

GROUP BY 열 HAVING 그룹조건

ORDER BY 열 [ASC\|DESC];

주요 옵션 · 절

| **옵션 / 절**         | **설명**                                   |
|-----------------------|--------------------------------------------|
| DISTINCT              | 중복 행 제거                               |
| WHERE                 | 행 필터 조건 (=, <, >, <>, AND/OR/NOT) |
| BETWEEN a AND b       | 범위 조건(양 끝 포함)                      |
| IN (…)                | 목록 중 하나와 일치                        |
| LIKE '%_'            | 패턴 검색(% : 0글자 이상, _ : 한 글자)    |
| IS NULL / IS NOT NULL | NULL 여부 (= NULL 은 동작 안 함)           |
| ORDER BY              | 정렬 (ASC 오름차순 기본, DESC 내림차순)    |
| GROUP BY / HAVING     | 그룹 집계 / 집계 결과 조건                 |
| 별칭(AS)              | 열·테이블에 별명 부여                      |

-- 가격이 10000~30000원인 도서명·가격 조회, 가격 내림차순

SELECT bookname, price

FROM Book

WHERE price BETWEEN 10000 AND 30000

ORDER BY price DESC;

-- 출판사별 도서 수와 평균가 (그룹 집계)

SELECT publisher, COUNT(*) AS 도서수, AVG(price) AS 평균가

FROM Book

GROUP BY publisher

HAVING COUNT(*) >= 2;

> **💡 날짜 조건은 문자열이 아니라 DATE로**
> DATE 열을 조건에 쓸 때는 **DATE '2025-07-04'** 또는 **TO_DATE('2025-07-04','YYYY-MM-DD')** 처럼 날짜 값으로 줘야 합니다. 그냥 '2025-07-04' 문자열로 주면 타입 불일치(ORA-00932)가 납니다. 또 NULL 비교는 =/&lt;&gt;가 아니라 IS NULL / IS NOT NULL을 씁니다.

3. INSERT — 데이터 삽입

**기본 설명** : 테이블에 새로운 행(튜플)을 추가합니다. 열 목록을 지정하는 방식과 생략하는 방식이 있습니다.

-- 방식 1: 열 목록 지정(권장) — 순서/일부 열만 안전하게

INSERT INTO Book (bookid, bookname, publisher, price)

VALUES (11, '농구 교본', '굿스포츠', 9000);

-- 방식 2: 열 생략 — 테이블의 모든 열을 정의 순서대로 채워야 함

INSERT INTO Book VALUES (12, '배구 이야기', '삼성당', 8000);

주요 옵션

- **열 목록 지정** : 일부 열만 넣거나 순서를 바꿔 넣을 수 있음(나머지는 NULL/DEFAULT)

- **서브쿼리 삽입** : VALUES 대신 SELECT 결과를 통째로 삽입

- **날짜 값** : DATE 리터럴 또는 TO_DATE 사용

-- 다른 테이블 조회 결과를 삽입

INSERT INTO Book (bookid, bookname, publisher, price)

SELECT bookid+100, bookname, publisher, price FROM Book WHERE price >= 30000;

-- 날짜가 있는 주문 삽입

INSERT INTO Orders VALUES (11, 1, 11, 9000, DATE '2025-07-11');

COMMIT; -- DML은 커밋해야 확정

> **💡 제약조건 위반과 커밋에 주의**
> 기본키 중복이면 **ORA-00001(무결성 위반)**, 참조하는 외래키 값이 부모에 없으면 **ORA-02291** 이 납니다(예: 없는 custid로 주문 삽입). INSERT 후에는 반드시 **COMMIT**해야 저장이 확정되고, 잘못 넣었으면 커밋 전에 **ROLLBACK**으로 취소할 수 있습니다.

4. UPDATE — 데이터 수정

**기본 설명** : 기존 행의 열 값을 변경합니다. **WHERE 절로 대상 행을 반드시 한정**해야 하며, 생략하면 전체 행이 수정됩니다.

UPDATE 테이블

SET 열1 = 값1, 열2 = 값2, ...

WHERE 조건; -- 생략하면 전체 행 수정(주의!)

주요 옵션

- **여러 열 동시 수정** : SET 열1=…, 열2=… 처럼 콤마로 나열

- **계산식 사용** : SET price = price * 1.1 처럼 기존 값 기반 갱신

- **서브쿼리** : SET 값이나 WHERE 조건에 SELECT 결과를 사용

-- 굿스포츠 도서 가격을 10% 인상

UPDATE Book

SET price = price * 1.1

WHERE publisher = '굿스포츠';

-- 특정 고객의 주소·전화 동시 수정

UPDATE Customer

SET address = '대한민국 부산', phone = '000-9000-0001'

WHERE custid = 5;

COMMIT;

> **💡 WHERE 없는 UPDATE는 전체를 바꾼다**
> **WHERE를 빼면 테이블의 모든 행이 수정**됩니다. 실무 사고의 대표 원인이므로, UPDATE 전에 같은 조건으로 **SELECT를 먼저 실행해 대상 행을 확인**하는 습관이 안전합니다. 커밋 전이라면 ROLLBACK으로 되돌릴 수 있습니다.

5. DELETE — 데이터 삭제

**기본 설명** : 테이블에서 행을 삭제합니다. UPDATE와 마찬가지로 **WHERE로 대상을 한정**하며, 생략하면 전체 행이 삭제됩니다(구조는 남음).

DELETE FROM 테이블

WHERE 조건; -- 생략하면 전체 행 삭제

주요 옵션 · 비교

| **구분**    | **DELETE**          | **TRUNCATE**        |
|-------------|---------------------|---------------------|
| 종류        | DML                 | DDL                 |
| 조건(WHERE) | 가능 (일부 행 삭제) | 불가 (전체만)       |
| 롤백        | 가능(커밋 전)       | **불가(자동 커밋)** |
| 속도        | 상대적으로 느림     | 매우 빠름           |

-- 8000원 미만 도서 삭제

DELETE FROM Book WHERE price < 8000;

-- 특정 고객의 모든 주문 삭제

DELETE FROM Orders WHERE custid = 3;

COMMIT;

> **💡 참조되는 행은 먼저 자식부터**
> 자식(Orders)이 참조 중인 부모(Book·Customer) 행을 먼저 지우려 하면 **ORA-02292(자식 레코드 존재)** 오류가 납니다. **자식 행(주문)을 먼저 삭제**하거나, 외래키를 ON DELETE CASCADE로 정의해야 합니다. 전체 데이터만 빠르게 비울 때는 TRUNCATE가 유리하지만 되돌릴 수 없습니다.

6. CREATE — 객체(테이블) 생성

**기본 설명** : 테이블·뷰 등 데이터베이스 객체를 생성합니다. 열 이름·데이터 타입과 함께 무결성을 지키는 **제약조건**을 정의합니다.

CREATE TABLE Customer (

custid NUMBER(2) PRIMARY KEY, -- 기본키(NULL·중복 불가)

name VARCHAR2(40) NOT NULL, -- 필수 입력

address VARCHAR2(50),

phone VARCHAR2(20) UNIQUE, -- 중복 불가

grade CHAR(1) DEFAULT 'C' -- 기본값

CHECK (grade IN ('A','B','C')) -- 허용 값 제한

);

주요 데이터 타입 · 제약조건

| **구분** | **항목**                 | **의미**                    |
|----------|--------------------------|-----------------------------|
| 타입     | NUMBER(p,s)              | 숫자(전체 자릿수 p, 소수 s) |
| 타입     | VARCHAR2(n)              | 가변 길이 문자열(최대 n)    |
| 타입     | CHAR(n) / DATE           | 고정 길이 문자 / 날짜·시간  |
| 제약     | PRIMARY KEY              | 기본키(NULL·중복 불가)      |
| 제약     | FOREIGN KEY … REFERENCES | 외래키(부모 기본키 참조)    |
| 제약     | NOT NULL / UNIQUE        | 필수 입력 / 중복 금지       |
| 제약     | DEFAULT / CHECK          | 기본값 / 값 범위 제한       |

-- 외래키가 있는 테이블 (부모 Customer·Book 이 먼저 존재해야 함)

CREATE TABLE Orders (

orderid NUMBER(2) PRIMARY KEY,

custid NUMBER(2) REFERENCES Customer(custid), -- 외래키

bookid NUMBER(2) REFERENCES Book(bookid),

saleprice NUMBER(8),

orderdate DATE DEFAULT SYSDATE

);

-- 조회 결과로 테이블 생성 (CTAS)

CREATE TABLE Book_expensive AS SELECT * FROM Book WHERE price >= 20000;

> **💡 생성 순서와 이름 중복**
> 외래키는 참조 대상이 먼저 있어야 하므로 **부모(Customer·Book) → 자식(Orders)** 순으로 만듭니다. 같은 이름 테이블이 이미 있으면 **ORA-00955** 가 나므로, 재실행 스크립트라면 앞에 **DROP TABLE IF EXISTS … CASCADE CONSTRAINTS** 를 두면 편합니다(23ai 지원).

7. ALTER — 구조 변경

**기본 설명** : 이미 만들어진 테이블의 구조(열·제약조건·이름)를 변경합니다.

주요 옵션

| **작업**         | **문법**                             |
|------------------|--------------------------------------|
| 열 추가          | ALTER TABLE t ADD (열 타입)          |
| 열 타입 변경     | ALTER TABLE t MODIFY (열 타입)       |
| 열 삭제          | ALTER TABLE t DROP COLUMN 열         |
| 열 이름 변경     | ALTER TABLE t RENAME COLUMN 옛 TO 새 |
| 제약조건 추가    | ALTER TABLE t ADD CONSTRAINT 이름 …  |
| 제약조건 삭제    | ALTER TABLE t DROP CONSTRAINT 이름   |
| 테이블 이름 변경 | ALTER TABLE t RENAME TO 새이름       |

-- 열 추가

ALTER TABLE Book ADD (stock NUMBER(4) DEFAULT 0);

-- 열 타입 변경 (문자열 길이 확장)

ALTER TABLE Book MODIFY (bookname VARCHAR2(60));

-- 제약조건 추가 (가격은 0 이상)

ALTER TABLE Book ADD CONSTRAINT chk_price CHECK (price >= 0);

-- 열 삭제

ALTER TABLE Book DROP COLUMN stock;

> **💡 ALTER는 자동 커밋 (DDL)**
> ALTER는 DDL이라 실행 즉시 **자동 커밋**되어 롤백되지 않습니다. 또 이미 데이터가 있는 열의 타입을 축소하거나(예: VARCHAR2(60)→(10)) NOT NULL을 추가할 때 기존 값과 충돌하면 오류가 나므로, 변경 전 데이터 상태를 확인해야 합니다.

8. DROP — 객체 삭제

**기본 설명** : 테이블 등 객체 자체를 삭제합니다. DELETE가 '행'을 지우는 것과 달리 DROP은 **구조와 데이터를 통째로 제거**합니다.

DROP TABLE 테이블 [CASCADE CONSTRAINTS] [PURGE];

주요 옵션

| **옵션** | **의미** |
|----|----|
| CASCADE CONSTRAINTS | 이 테이블을 **참조하는 외래키 제약조건도 함께 제거** |
| PURGE | 휴지통(Recycle Bin)을 거치지 않고 **완전 삭제**(복구 불가) |
| IF EXISTS | 테이블이 없어도 오류 없이 넘어감 (Oracle 23ai) |

-- 참조 관계가 있으면 자식부터, 또는 CASCADE

DROP TABLE Orders CASCADE CONSTRAINTS;

DROP TABLE Book CASCADE CONSTRAINTS;

DROP TABLE Customer CASCADE CONSTRAINTS;

-- 재실행 스크립트에 안전 (23ai)

DROP TABLE IF EXISTS Book CASCADE CONSTRAINTS;

> **💡 DELETE·TRUNCATE·DROP 구분**
> **DELETE** = 행 삭제(구조 유지, 롤백 가능), **TRUNCATE** = 전체 행 삭제(구조 유지, 자동 커밋), **DROP** = 테이블 자체 삭제(구조+데이터 모두). 부모 테이블을 DROP할 때 자식이 참조 중이면 **CASCADE CONSTRAINTS** 가 필요합니다.

9. 명령어 요약

| **명령어** | **분류** | **핵심 기능** | **필수/주의 옵션**          |
|------------|----------|---------------|-----------------------------|
| SELECT     | DML      | 데이터 조회   | WHERE·ORDER BY·GROUP BY     |
| INSERT     | DML      | 행 삽입       | 열 목록 지정 · COMMIT       |
| UPDATE     | DML      | 행 수정       | **WHERE 필수** · COMMIT     |
| DELETE     | DML      | 행 삭제       | **WHERE 필수** · 참조 주의  |
| CREATE     | DDL      | 객체 생성     | 제약조건 · 생성 순서        |
| ALTER      | DDL      | 구조 변경     | ADD/MODIFY/DROP · 자동 커밋 |
| DROP       | DDL      | 객체 삭제     | CASCADE CONSTRAINTS         |

> **💡 실습 마무리 체크**
> ① DML(SELECT·INSERT·UPDATE·DELETE)은 **데이터**를 다루고 **COMMIT**으로 확정, ② DDL(CREATE·ALTER·DROP)은 **구조**를 다루고 **자동 커밋**, ③ UPDATE·DELETE는 **WHERE로 대상을 한정**, ④ 날짜는 **DATE 리터럴**, ⑤ 참조 관계가 있으면 **생성은 부모→자식, 삭제는 자식→부모(또는 CASCADE)**. 산출물은 각 명령 실행 후 결과 테이블을 확인하는 것.
