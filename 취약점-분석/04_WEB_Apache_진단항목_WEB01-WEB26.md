# 04. WEB(Apache) 진단 항목 (WEB-01 ~ WEB-26)

> 결과보고서 양식 기준 웹 서비스(Apache) 진단 항목. 4개 분류, 총 26개 항목.

---

## 분류별 항목

## 1. 계정 관리 (WEB-01 ~ WEB-03)

| 코드 | 점검항목 | 중요도 |
|------|---------|:---:|
| WEB-01 | Default 관리자 계정명 변경 | 상 |
| WEB-02 | 취약한 비밀번호 사용 제한 | 상 |
| WEB-03 | 비밀번호 파일 권한 관리 | 상 |

## 2. 서비스 관리 (WEB-04 ~ WEB-18)

| 코드 | 점검항목 | 중요도 |
|------|---------|:---:|
| WEB-04 | 웹 서비스 디렉터리 리스팅 방지 설정 | 상 |
| WEB-05 | 지정하지 않은 CGI/ISAPI 실행 제한 | 상 |
| WEB-06 | 웹 서비스 상위 디렉터리 접근 제한 설정 | 상 |
| WEB-07 | 웹 서비스 경로 내 불필요한 파일 제거 | 중 |
| WEB-08 | 웹 서비스 파일 업로드 및 다운로드 용량 제한 | 하 |
| WEB-09 | 웹 서비스 프로세스 권한 제한 | 상 |
| WEB-10 | 불필요한 프록시 설정 제한 | 상 |
| WEB-11 | 웹 서비스 경로 설정 | 중 |
| WEB-12 | 웹 서비스 링크 사용 금지 (Symbolic Link) | 중 |
| WEB-13 | 웹 서비스 설정 파일 노출 제한 | 상 |
| WEB-14 | 웹 서비스 경로 내 파일의 접근 통제 | 상 |
| WEB-15 | 웹 서비스의 불필요한 스크립트 매핑 제거 | 상 |
| WEB-16 | 웹 서비스 헤더 정보 노출 제한 (ServerTokens) | 중 |
| WEB-17 | 웹 서비스 가상 디렉토리 삭제 | 중 |
| WEB-18 | 웹 서비스 WebDAV 비활성화 | 상 |

## 3. 보안 설정 (WEB-19 ~ WEB-23)

| 코드 | 점검항목 | 중요도 |
|------|---------|:---:|
| WEB-19 | 웹 서비스 SSI(Server Side Includes) 사용 제한 | 중 |
| WEB-20 | SSL/TLS 활성화 | 상 |
| WEB-21 | HTTP 리디렉션 | 중 |
| WEB-22 | 에러 페이지 관리 | 하 |
| WEB-23 | LDAP 알고리즘 적절하게 구성 | 중 |

## 4. 패치 및 로그 관리 (WEB-24 ~ WEB-26)

| 코드 | 점검항목 | 중요도 |
|------|---------|:---:|
| WEB-24 | 별도의 업로드 경로 사용 및 권한 설정 | 상 |
| WEB-25 | 주기적 보안 패치 및 벤더 권고사항 적용 | 상 |
| WEB-26 | 로그 디렉터리 및 파일 권한 설정 | 중 |

---

## 주요 항목 조치 예시 (httpd.conf)

**WEB-04 디렉터리 리스팅 방지**
```apache
<Directory /path>
    Options -Indexes      # Indexes 제거
</Directory>
```

**WEB-06 상위 디렉터리 접근 제한**
```apache
<Directory />
    AllowOverride None
    Options None
</Directory>
# .htaccess 및 상위 경로(../) 접근 차단
```

**WEB-16 헤더 정보 노출 제한**
```apache
ServerTokens Prod      # Apache 버전·OS 정보 숨김
ServerSignature Off
```

**WEB-18 WebDAV 비활성화**
```apache
# 불필요한 DAV 모듈 주석 처리
# LoadModule dav_module modules/mod_dav.so
```
