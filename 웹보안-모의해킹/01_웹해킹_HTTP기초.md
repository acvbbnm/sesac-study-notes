# 01. 웹 해킹 기초 & HTTP 프로토콜

> 교재: 웹 보안 및 모의해킹 (장대현 수석, SeSAC SW 5기)

---

## 1. 웹 해킹이란

웹 서비스의 취약점을 공격하는 기술적 위협으로, 웹 기능(로그인·게시판·파일 업로드 등)을 통해 **권한 없는 시스템에 접근**하거나 **데이터 유출·파괴**를 일으키는 공격 행위.

### 웹 해킹의 기본 원리 — 서버 & 클라이언트

| 구분 | 역할 |
|------|------|
| **웹 클라이언트** | 웹 서버에 페이지를 요청하고, 응답 결과를 출력(브라우저) |
| **웹 서버** | 요청받은 페이지를 찾아 HTML/JavaScript/CSS 등으로 전달 |

### 실행 위치별 언어

| 구분 | 언어 | 실행 위치 |
|------|------|----------|
| **클라이언트 측 (Client Side)** | HTML, CSS, JavaScript, VBScript | 브라우저(사용자 PC)에서 실행 |
| **서버 측 (Server Side)** | Java(JSP/Servlet), ASP.NET, PHP, Python | 웹 서버에서 실행 |

> **보안 핵심**: 인증·권한·검증 로직은 반드시 **Server Side**에서 처리해야 한다. Client Side Script는 사용자가 조작 가능하므로 신뢰할 수 없다.

---

## 2. HTTP 프로토콜

**HTTP (Hyper Text Transfer Protocol)**: WWW 상에서 HTML 문서 등을 주고받는 애플리케이션 계층의 텍스트 기반 프로토콜.

- **요청(Request) / 응답(Response)** 방식
- **TCP 기반**, 기본 포트 **80번** (HTTPS는 443)
- **Stateless(상태 없음)**: 요청 간 상태를 서버가 기억하지 않음 → 세션/쿠키로 상태 유지

### HTTP 주요 Method

| Method | 설명 | 특징 / 보안 |
|--------|------|------------|
| **GET** | 데이터 조회 | URL에 정보 노출, 데이터 변경 없음 |
| **POST** | 데이터 생성/처리 | body에 데이터 포함, 상태 변경 |
| HEAD | 헤더 정보만 요청 | 본문 없이 응답, 존재 확인용 |
| **TRACE** | 요청을 그대로 반환 | 경로 테스트용, ⚠️ 보안상 비활성화 권장 |
| **PUT** | 리소스 전체 수정/생성 | ⚠️ 기존 내용 전체 덮어씀 |
| **DELETE** | 리소스 삭제 | ⚠️ 서버에서 제거 |
| PATCH | 리소스 일부 수정 | 부분 업데이트 |
| OPTIONS | 지원 메서드 조회 | - |

> ⚠️ **PUT / DELETE / TRACE**는 악용 위험이 커서 불필요 시 비활성화 (→ 취약한 보안설정)

### GET vs POST

```
# GET — 데이터를 URL에 포함 (노출됨, 길이 제한 ~2000자)
GET login.jsp?user_id=admin&user_pass=abcd
Host: www.security_test.com

# POST — 데이터를 Request Body에 포함 (상대적으로 안전, 길이 제한 거의 없음)
POST login.jsp HTTP/1.1
Host: www.security_test.com
Content-Length: 45

user_id=admin; user_pass=abcd
```

### HTTP 응답 코드 (Status Code)

| 코드 | 분류 | 대표 |
|:----:|------|------|
| **1XX** | 정보 | 100 Continue, 101 Switching Protocols |
| **2XX** | 성공 | **200 OK**, 201 Created, 204 No Content |
| **3XX** | 리다이렉션 | 301 영구이동, **302 임시이동**, 304 Not Modified |
| **4XX** | 클라이언트 오류 | 400 Bad Request, **401 인증 필요**, **403 접근 거부**, **404 Not Found**, 405 Method Not Allowed |
| **5XX** | 서버 오류 | **500 Internal Server Error**, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout |

---

## 3. Session & Cookie

HTTP의 Stateless 특성을 보완해 클라이언트를 구분·인증 상태를 유지하는 방법.

| 구분 | 세션(Session) | 쿠키(Cookie) |
|------|--------------|-------------|
| **저장 위치** | 서버 | 클라이언트(브라우저) |
| **보안** | 🟢 상대적으로 안전 | ⚠️ 정보 유출 위험(변조 가능) |
| **부담** | 서버 메모리·저장소 사용 | 서버 부담 적음 |
| **식별** | 서버가 **세션 ID** 발급 → 클라이언트가 이를 통해 연결 | 로그인 정보 등 인증 상태 유지 |

> **보안 원칙**: 인증에는 쿠키보다 **Server Side Session** 사용. 세션 ID는 예측 불가능하게 생성하고, 고정(Session Fixation)·평문 전송을 피한다.
