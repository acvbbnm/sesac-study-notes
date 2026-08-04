# 11. 취약점 진단 실전 결과 — WEB (Apache / Tomcat, CentOS 6.9)

> CentOS 6.9 서버의 웹 서비스(Apache 2.2 + Tomcat 9) 진단 **결과보고서 완성본**.  
> 실제 설정 파일 경로·값·판정 근거 포함. (표준 항목 → [04](./04_WEB_Apache_진단항목_WEB01-WEB26.md))

---

## 진단 결과 요약

- **총 26개 항목** 중 🟢 양호 **5** / 🔴 취약 **19** / N/A **2**

**🔴 취약 (19)**: WEB-01, WEB-02, WEB-03, WEB-04, WEB-05, WEB-06, WEB-08, WEB-09, WEB-11, WEB-12, WEB-13, WEB-14, WEB-16, WEB-20, WEB-21, WEB-22, WEB-24, WEB-25, WEB-26

**🟢 양호 (5)**: WEB-07, WEB-10, WEB-17, WEB-18, WEB-19

**N/A (2)**: WEB-15, WEB-23 (해당 기능 미사용)

> 대상 서버는 Apache가 대부분 기본 설정(Default)이라 **파일 소유자가 root, 권한이 과다(755/644)** 한 항목이 다수 취약. 조치 방향은 공통적으로 **전용 계정(apache/WAS 계정)으로 소유자 변경 + 권한 축소(750/640)**.

---

## 계정 관리

### WEB-01 Default 관리자 계정명 변경 `상` 🔴 취약

**[현황]**
- "/root/apache-tomcat-9.0.0.M19/conf/tomcat-users.xml" 파일 내 Default 계정(tomcat)을 그대로 사용하고 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 사용중인 Default 계정(tomcat)을 유추할 수 없는 계정명으로 변경하여 주시기 바랍니다.

### WEB-02 취약한 비밀번호 사용 제한 `상` 🔴 취약

**[현황]**
- "/root/apache-tomcat-9.0.0.M19/conf/tomcat-users.xml" 파일 내 Default 계정(tomcat)의 패스워드가 지정되지 않은 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 사용중인 Default 계정(tomcat) 패스워드를 복잡도 기준에 맞게 설정하여 주시기 바랍니다.

### WEB-03 비밀번호 파일 권한 관리 `상` 🔴 취약

**[현황]**
- "/root/apache-tomcat-9.0.0.M19/conf/tomcat-users.xml" 파일의 권한이 600(-rw-------)이지만 소유자 및 그룹 소유자가 "root"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 해당 파일의 소유자 및 그룹 소유자를 전용 WAS 계정으로 설정하여 주시기 바랍니다.

## 서비스 관리

### WEB-04 웹 서비스 디렉터리 리스팅 방지 설정 `상` 🔴 취약

**[현황]**
- 일부 웹 소스 디렉터리(/var/www/html, /var/www/icons) 옵션 값이 "Indexes"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 일부 웹 소스 디렉터리(/var/www/html, /var/www/icons) 옵션 값을 "-Indexes"로 설정하시거나 제거하여 주시기 바랍니다.

### WEB-05 지정하지 않은 CGI/ISAPI 실행 제한 `상` 🔴 취약

**[현황]**
- cgi 스크립트가 저장되는 경로에 스크립트가 저장되어 있지 않지만 "/etc/httpd/conf/httpd.conf" 설정 파일 내 "cgi_module"이 활성화되어 있고 "/var/www/cgi-bin" 디렉터리 권한이 755(drwxr-xr-x)로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 "cgi_module" 구문을 주석으로 처리한 후  "/var/www/cgi-bin" 디렉터리 권한을 750(drwxr-x---)으로 설정하여 주시기 바랍니다.

### WEB-06 웹 서비스 상위 디렉터리 접근 제한 설정 `상` 🔴 취약

**[현황]**
- "/"를 제외한 전체 웹 소스 디렉터리에 "AllowOverride" 값이 "None"으로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 전체 웹 소스 디렉터리에 "AllowOverride" 값을 "AuthConfig"로 변경하여 주시기 바랍니다.
(*) 현재 운영중인 웹 애플리케이션의 계정 인가 처리를 세션 통신을 하는 경우 별도의 인증처리 없이 상위 경로로 접근이 가능할 수 있음

### WEB-07 웹 서비스 경로 내 불필요한 파일 제거 `중` 🟢 양호

**[현황]**
- apache 설치 디렉터리 및 웹 소스 디렉터리에 "htdocs", "manual"과 같은 임시 파일이 저장되어 있지 않은 상태입니다.

### WEB-08 웹 서비스 파일 업로드 및 다운로드 용량 제한 `하` 🔴 취약

**[현황]**
- 일부 웹 소스 디렉터리(/var/www/html)에 업로드 기능이 존재하지만 "/etc/httpd/conf/httpd.conf" 설정 파일 내 해당 웹 소스 디렉터리에 "LimitRequestBody" 값이 존재하지 않는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 "/etc/httpd/conf/httpd.conf" 설정 파일 내 해당 웹 소스 디렉터리에 "LimitRequestBody" 값을 "5000000" 이하로 설정하여 주시기 바랍니다.
※ 업/다운로드 관련 API Source에서 확장자 검증을 통해 업/다운로드를 사용할 경우 "LimitRequestBody"이 존재하지 않아도 양호로 처리될 수 있음

### WEB-09 웹 서비스 프로세스 권한 제한 `상` 🔴 취약

**[현황]**
- "httpd" 데몬이 전용 웹 서버 계정(apache)으로 구동하고 있고 로그인 할 수 없는 상태지만 apache 설치 디렉터리(/etc/httpd) 및 웹 소스 디렉터리(/var/www/html)의 소유자/그룹소유자가 "root"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 apache 설치 디렉터리(/etc/httpd) 및 웹 소스 디렉터리(/var/www/html)의 소유자/그룹소유자를 전용 웹 서버 계정(apache)으로 변경하여 주시기 바랍니다.

### WEB-10 불필요한 프록시 설정 제한 `상` 🟢 양호

**[현황]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 "Proxy" 설정이 존재하지 않는 상태입니다.
**[인터뷰]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 목적이 확인되지 않은 웹 URL Proxy가 존재하여 담당자 확인이 필요합니다.

### WEB-11 웹 서비스 경로 설정 `중` 🔴 취약

**[현황]**
- 웹 소스 디렉터리(/var/www/html)가 apache 설치 Default 경로로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 웹 소스 디렉터리를 유추할 수 없는 별도의 디렉터리 명으로 변경하여 주시기 바랍니다.
※ 웹 소스 디렉터리 변경 시 Frontend Source 경로도 동일하게 변경해야 서비스 영향도가 발생하지 않습니다. (SE 및 웹 개발 담당자 간 협의 후 조치 필요)

### WEB-12 웹 서비스 링크 사용 금지 `중` 🔴 취약

**[현황]**
- 일부 웹 소스 디렉터리(/, /var/www/html, /var/www/icons) 옵션에 "FollowSymLinks" 값이 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 일부 웹 소스 디렉터리(/, /var/www/html, /var/www/icons) 옵션에 "-FollowSymLinks"로 설정하시거나 제거하여 주시기 바랍니다.

### WEB-13 웹 서비스 설정 파일 노출 제한 `상` 🔴 취약

**[현황]**
- "/root/apache-tomcat-9.0.0.M19/conf/server.xml" 파일 권한이 600(-rw-------)으로 설정되어 있지만 소유자 및 그룹 소유자가 "root"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 해당 파일의 소유자 및 그룹 소유자를 전용 WAS 계정으로 설정하여 주시기 바랍니다.

### WEB-14 웹 서비스 경로 내 파일의 접근 통제 `상` 🔴 취약

**[현황]**
- apache 설정 파일(*.conf)의 권한이 644(-rw-r--r--), 설치 디렉터리 권한이 755(drwxr-xr-x)로 부여되어 있고 모든 파일 및 디렉터리 소유자/그룹 소유자가 "root"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 apache 설정 파일(*.conf)의 권한을 640(-rw-r-----), 설치 디렉터리 권한을 750(drwxr-x---)으로 설정 후 모든 파일 및 디렉터리 소유자/그룹 소유자를 웹 서버 전용 계정(apache)으로 변경하여 주시기 바랍니다.

### WEB-15 웹 서비스의 불필요한 스크립트 매핑 제거 `상` ⚪ N/A


### WEB-16 웹 서비스 헤더 정보 노출 제한 `중` 🔴 취약

**[현황]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 "ServerTokens" 값이 "OS", "ServerSignature" 값이 "On"으로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 "ServerTokens" 값을 "Prod", "ServerSignature" 값을 "Off"로 변경하여 주시기 바랍니다.

### WEB-17 웹 서비스 가상 디렉토리 삭제 `중` 🟢 양호

**[현황]**
- 가상의 웹 소스 디렉터리(Alias)에 등록되어 있는 경로가 현재 사용중인 상태입니다.

### WEB-18 웹 서비스 WebDAV 비활성화 `상` 🟢 양호

**[현황]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 "Dav" 값이 존재하지 않고 "/var/www/cgi-bin" 디렉터리에 어떠한 파일도 존재하지 않는 상태입니다.

## 보안 설정

### WEB-19 웹 서비스 SSI(Server Side Includes) 사용 제한 `중` 🟢 양호

**[현황]**
- 일부 웹 소스 디렉터리(/var/www/error)에 "IncludesNoExec" 값이 설정되어 있는 상태입니다.

### WEB-20 SSL/TLS 활성화 `상` 🔴 취약

**[현황]**
- 대상 웹 애플리케이션의 웹 기능에 입력값이 존재하는데 "/etc/httpd/conf/httpd.conf" 설정 파일 내 HTTP(80)만 허용되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 HTTPS(443) 포트를 Listen 값으로 추가 및 포트를 허용한 후 SSL/TLS 사설 인증서를 서버 내 등록하여 주시기 바랍니다.

### WEB-21 HTTP 리디렉션 `중` 🔴 취약

**[현황]**
- 대상 웹 애플리케이션의 웹 기능에 입력값이 존재하는데 "/etc/httpd/conf/httpd.conf" 설정 파일 내 HTTP(80)만 허용되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 HTTP(80) URL 호출 시 HTTPS(443) URL로 Redirection 될 수 있도록 설정하여 주시기 바랍니다.
※ HTTPS(443) 포트를 Listen 값으로 추가 및 포트를 허용한 후 SSL/TLS 사설 인증서를 서버 내 등록하여 주시기 바랍니다.

### WEB-22 에러 페이지 관리 `하` 🔴 취약

**[현황]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 "ErrorDocument" 에러 핸들링 값이 주석으로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 "ErrorDocument" 에러 핸들링 값의 주석 제거 후 에러 코드가 노출되지 않도록 공통의 에러페이지 생성 및 각각의 에러 핸들링 파일에 생성한 공통의 에러페이지를 설정하여 주시기 바랍니다.

### WEB-23 LDAP 알고리즘 적절하게 구성 `중` ⚪ N/A


## 패치 및 로그 관리

### WEB-24 별도의 업로드 경로 사용 및 권한 설정 `중` 🔴 취약

**[현황]**
- 일부 웹 소스 디렉터리(/var/www/html) 하위에 업로드 기능이 추가되어 있지만 "/var/www/html" 권한이 755(drwxr-xr-x), 소유자/그룹 소유자가 "root"로 설정되어 있는 상태입니다. 
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 해당 경로에 업로드 파일을 저장하고 있어 "/var/www/html" 권한을 750(drwxr-x---), 소유자/그룹 소유자를 웹 서버 전용 계정(apache)으로 변경하여 주시기 바랍니다.

### WEB-25 주기적 보안 패치 및 벤더 권고사항 적용 `상` 🔴 취약

**[현황]**
- "apache(2.2.15-69)"가 Repository 설치 방식으로 구성되어 있어 현재 CentOS 6.9 버전은 2020년 11월 30일 기준으로 EOS(End Of Service)되어 최신 패치 적용이 불가능한 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 최신 패치 적용이 가능한 OS로 신규 구축 후 Apache 구성 및 데이터 Migration을 진행하여 주시기 바랍니다.

### WEB-26 로그 디렉터리 및 파일 권한 설정 `중` 🔴 취약

**[현황]**
- "/etc/httpd/conf/httpd.conf" 설정 파일 내 로그 디렉터리(/etc/httpd/logs)의 권한이 700(drwx------)이지만, 로그 파일의 권한이 644(-rw-r--r--), 소유자/그룹 소유자가 "root"로 설정되어 있는 상태입니다.
**[대응방안]**
주요정보통신기반시설 가이드를 참고하시어 로그 디렉터리 및 파일의 소유자/그룹 소유자를 웹 서버 전용 계정(apache)으로 변경하여 주시고 로그 파일의 권한을 640(-rw-r-----)으로 설정하여 주시기 바랍니다.
※ 현재 대상 웹 서버의 로그 기록에 대한 기준은 "Combined"로 설정되어 있음
---

## Apache 진단 실무 명령어 (강의)

진단 시 실제로 사용한 httpd.conf 확인 명령어 모음.

```bash
# ServerRoot / DocumentRoot 확인 (설치 경로·웹 루트)
cat /etc/httpd/conf/httpd.conf | grep "DocumentRoot\|ServerRoot" | grep -v "#"

# Directory 지시자 블록 확인 (Options, AllowOverride 등 — WEB-04/06/12)
cat /etc/httpd/conf/httpd.conf | grep -C10 Directory | grep -v "#"

# 모든 .conf 설정 파일 목록·권한 확인 (WEB-14)
find /etc/httpd/ -name "*.conf" -exec ls -al {} \;

# Listen 포트 확인 (HTTP 80 / HTTPS 443 — WEB-20/21)
cat /etc/httpd/conf/httpd.conf | grep Listen | grep -v "#"

# 로그 설정 확인 (CustomLog / ErrorLog — WEB-26)
cat /etc/httpd/conf/httpd.conf | grep "CustomLog\|ErrorLog" | grep -v "#"

# 로그 포맷 확인 (LogFormat)
cat /etc/httpd/conf/httpd.conf | grep LogFormat

# Tomcat servlet-mapping 확인 (WAS)
cat /root/apache-tomcat-9.0.0.M19/conf/web.xml | grep -C5 "servlet-mapping"
```

### SSL/TLS 프로토콜 설정 (WEB-20)

취약한 구버전 프로토콜(SSLv2/3, TLS 1.0/1.1)을 끄고 TLS 1.2/1.3만 허용한다.

```apache
Listen 443
# 중략
SSLProtocol      -All +TLSv1.2 +TLSv1.3      # TLS 1.2+1.3 허용
SSLProxyProtocol -All +TLSv1.2 +TLSv1.3

# TLS 1.3만 허용하는 더 강한 설정
SSLProtocol      -All +TLSv1.3
SSLProxyProtocol -All +TLSv1.3
```
> `-All`로 전부 끈 뒤 `+TLSvX.X`로 허용할 버전만 켜는 방식.

### Apache 로그 포맷(LogFormat) 이해 (WEB-26)

```apache
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t \"%r\" %>s %b" common
LogFormat "%{Referer}i -> %U" referer
LogFormat "%{User-agent}i" agent
```

**가. common** — 기본 접근 로그

| 포맷 | 의미 |
|------|------|
| `%h` | 원격 호스트(클라이언트 IP) |
| `%l` | 원격 로그인 ID (identd 지원 시) |
| `%u` | 인증된 원격 유저 이름 |
| `%t` | 접속 시간 (CLF 포맷) |
| `%r` | 첫 번째 요청 라인 (메서드·URL·프로토콜) |
| `%>s` | 응답 상태 코드 |
| `%b` | 헤더 포함 전송량(bytes) |

**나. referer** (`%{Referer}i -> %U`) — 접속 전 머물렀던 URL(유입 경로) 기록  
**다. agent** (`%{User-agent}i`) — 접속자의 웹 브라우저·OS 종류 기록  
**combined** = common + referer + agent를 합친 형태 (대상 서버 기본값)

> 진단 시 `CustomLog`가 **combined** 포맷인지 확인. combined여야 IP·요청·유입경로·UA가 모두 남아 침해분석에 활용 가능. (→ [07. 계층별 로그](./07_계층별_로그_정리.md))
