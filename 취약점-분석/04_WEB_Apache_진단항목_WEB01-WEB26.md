# 04. WEB(웹 서비스) 진단 항목 상세 (WEB-01 ~ WEB-26)

> 2026년 주요정보통신기반시설 기술적 취약점 분석·평가 상세가이드(KISA) 기준.  
> 대상: Apache, IIS, Tomcat, JEUS 등. 4개 분류, 총 26개 항목.  
> 각 항목: 개요 / 판단 기준(양호·취약) / 조치 방법 / 조치 예시.

## 분류별 항목 수

| 분류 | 범위 | 개수 |
|------|------|:---:|
| 1. 계정 관리 | WEB-01 ~ WEB-03 | 3 |
| 2. 서비스 관리 | WEB-04 ~ WEB-18 | 15 |
| 3. 보안 설정 | WEB-19 ~ WEB-23 | 5 |
| 4. 패치 및 로그 관리 | WEB-24 ~ WEB-26 | 3 |

---

## 1. 계정 관리

### WEB-01 (상) Default 관리자 계정명 변경

웹 서비스 설치 시 기본적으로 설정된 관리자 계정의 변경 후 사용 여부 점검 기본 관리자 계정명과 같은 알려진 계정명을 유추하기 어려운 계정명으로 변경 후 사용하여 공격자에 의한 추측 공격 및 무단 접근 등을 방지하고 보안을 강화하기 위함 기본 관리자 계정명을 변경하지 않고 사용할 경우, 공격자에 의한 계정 및 비밀번호 추측 공격이 가능하고, 이를 통해 불법적인 접근, 데이터 유출, 시스템 장애 등의 보안 사고가 발생할 수 있는 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 관리자 페이지를 사용하지 않거나, 계정명이 기본 계정명으로 설정되어 있지 않은 경우 |
| 🔴 취약 | 계정명이 기본 계정명으로 설정되어 있거나, 추측하기 쉬운 문자 조합으로 이루어진 계정명을 사용하는 경우 |

**조치 방법**: 기본 관리자 계정명을 추측하기 어려운 계정명으로 설정

**조치 예시 (Tomcat)**
```apache
Step 1) 기본 계정명 변경 또는 관리자 페이지 비활성화(기본값: 비활성화)
# vi <Tomcat 설치 디렉터리>/conf/server.xml
예시) <user username="admin" password="XNDJxndn264!@" roles="manager-gui"/>
Step 2) Tomcat 재구동
# systemctl restart tomcat
※ “roles = manager-gui, manager-script, manager-jmx, manager-status” 설정 시 관리자 계정 및 페이지 활성화 상태
2026
```

<details><summary>참고</summary>

- 기본 계정: 웹 서비스 설치 시 기본적으로 생성되는 관리자 콘솔 계정
- 서비스별 기본 계정: IIS(Administrator), Tomcat(tomcat, admin), JEUS(administrator)
</details>

### WEB-02 (상) 취약한 비밀번호 사용 제한

관리자 계정의 취약한 비밀번호 설정 여부 점검 관리자 계정의 비밀번호가 복잡도 기준에 맞게 적용되어 있는지 점검하여, 비인가자에 의한 비밀번호 유추 공격 및 관리자 권한 탈취 등을 방지하기 위함 관리자 계정의 비밀번호를 취약하게 설정하여 사용하는 경우, 비인가자의 비밀번호 유추 공격으로 관리자 권한 탈취 및 시스템 침입 등의 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 관리자 비밀번호가 암호화되어 있거나, 유추하기 어려운 비밀번호로 설정된 경우 |
| 🔴 취약 | 관리자 비밀번호가 암호화되어 있지 않거나, 유추하기 쉬운 비밀번호로 설정된 경우 |

**조치 방법**: 복잡도 기준에 맞는 추측하기 어려운 비밀번호 설정

**조치 예시 (Tomcat)**
```apache
Step 1) 복잡도를 만족하는 비밀번호 설정
# vi <Tomcat 설치 디렉터리>/conf/server.xml
<user username="admin" password="XNDJxndn264!@" roles="manager-gui"/>
Step 2) Tomcat 재시작
# systemctl restart tomcat
```

### WEB-03 (상) 비밀번호 파일 권한 관리

비밀번호 파일에 대해 적절한 접근 권한 설정 여부 점검 비밀번호 파일의 접근 권한을 적절하게 설정하여 비인가자가 비밀번호 파일에 무단 접근 및 유출 등을 방지하기 위함 비밀번호 파일의 권한을 적절하게 설정하지 않은 경우, 비인가자에게 비밀번호 정보가 노출될 수 있고 웹 서버에 접속하는 등의 침해사고가 발생할 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 비밀번호 파일에 권한이 600 이하로 설정된 경우 |
| 🔴 취약 | 비밀번호 파일에 권한이 600 초과로 설정된 경우 |

**조치 방법**: 비밀번호 파일 권한 600 이하로 설정

**조치 예시 (Tomcat)**
```apache
Step 1) tomcat-users.xml 파일 권한 변경
# chmod 600 /<Tomcat 설치 디렉터리>/tomcat-users.xml
```


---

## 2. 서비스 관리

### WEB-04 (상) 웹 서비스 디렉터리 리스팅 방지 설정

디렉터리 리스팅 기능 차단 여부 점검 웹 서버에 대한 디렉터리 리스팅 기능을 차단하여 디렉터리 내의 모든 파일에 대한 접근 및 정보 노출을 차단하기 위함 디렉터리 리스팅 기능이 차단되지 않은 경우, 비인가자가 해당 디렉터리 내의 모든 파일의 리스트 확인 및 접근이 가능하고, 웹 서버의 구조 및 백업 파일이나 소스 파일 등 공개되면 안 되는 중요 파일들이 노출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 디렉터리 리스팅이 설정되지 않은 경우 |
| 🔴 취약 | 디렉터리 리스팅이 설정된 경우 |

**조치 방법**: 디렉터리 리스팅 기능 차단 설정

**조치 예시 (Apache)**
```apache
Step 1) httpd.conf 파일 내 모든 디렉터리의 Options 지시자에서 Indexes 옵션 제거
# vi /<Apache 설치 디렉터리>/httpd.conf(또는 apache.conf)
<Directory />
Options Indexes 삭제 (또는 –Indexes 설정)
</Directory>
Step 2) Apache 재시작
# systemctl restart apache2
※ httpd.conf 뿐 아니라 sites-available 디렉터리 내 모든 사이트에 적용
※ 파일 위치 및 서비스명은 사용하는 운영체제에 따라 달라질 수 있음
2026
```

<details><summary>참고</summary>

- 디렉터리 리스팅(Directory Listing): 웹 서버의 취약한 설정으로 인해 웹 서버의 파일 시스템 참고 목록을 보여주는 것
</details>

### WEB-05 (상) 지정하지 않은 CGI/ISAPI 실행 제한

웹 서비스 CGI 실행 제한 설정 여부 점검 CGI 스크립트를 정해진 디렉터리에서만 실행되도록 하여 악의적인 파일의 업로드 및 실행을 방지하기 위함 게시판이나 자료실과 같이 업로드되는 파일이 저장되는 디렉터리에 CGI 스크립트가 실행 가능한 경우 악의적인 파일을 업로드하고 이를 실행하여 시스템의 중요 정보가 노출될 수 있으며 침해사고의 경로로 이용될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | CGI 스크립트를 사용하지 않거나 CGI 스크립트가 실행 가능한 디렉터리를 제한한 경우 |
| 🔴 취약 | CGI 스크립트를 사용하고 CGI 스크립트가 실행 가능한 디렉터리를 제한하지 않은 경우 |

**조치 방법**: CGI 스크립트를 정해진 디렉터리 내에서만 실행할 수 있도록 설정

**조치 예시 (Apache)**
```apache
Step 1) apache 설정 파일 내 CGI 모듈 비활성화 또는 주석 처리
# vi /<Apache 설치 디렉터리>/httpd.conf(또는 apache.conf)
#LoadModule cgi_module modules/mod_cgi.so
#LoadModule cgid_module modules/mod_cgid.so
Step 2) apache 설정 파일 내 설정된 모든 디렉터리의 Options 지시자에서 ExecCGI 옵션 제거
# vi /<Apache 설치 디렉터리>/apache.conf(또는 httpd.conf)
<Directory "/var/www/cgi-bin">
Options -ExecCGI
</Directory>
Step 3) Apache 재시작
```

<details><summary>참고</summary>

- CGI(Common Gateway Interface): 사용자가 서버로 보낸 데이터를 서버에서 작동 중인 데이터 참고 처리프로그램에 전달하고, 여기에서 처리된 데이터를 다시 서버로 되돌려 보내는 등의 일을 하는 표준 인터페이스 규격
</details>

### WEB-06 (상) 웹 서비스 상위 디렉터리 접근 제한 설정

“..” 와 같은 문자사용 등을 통한 상위 디렉터리 접근 제한 여부 점검 상위 디렉터리 접근 제한 설정을 통해 비인가자의 특정 디렉터리에 대한 접근 및 열람을 제한하여 중요 파일 및 데이터를 보호하고, Unicode 버그 및 서비스 거부 공격 등을 방지하기 위함 상위 디렉터리로 이동하는 것이 가능할 경우 접근하고자 하는 디렉터리의 하위 경로에서 상위로 이동하며 정보 탐색이 가능하여 중요 정보가 노출될 위험이 존재함 악의적인 목적을 가진 사용자가 중요 파일 및 디렉터리의 접근이 가능하여 데이터가 유출될 위험이 존재함 참고

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 상위 디렉터리 접근 기능을 제거한 경우 |
| 🔴 취약 | 상위 디렉터리 접근 기능을 제거하지 않은 경우 |

**조치 방법**: 상위 디렉터리 접근 기능 제거 설정

**조치 예시 (Apache)**
```apache
Step 1) AllowOverride 지시자 Authconfig 옵션 설정 확인
# vi /<Apache 설치 디렉터리>/httpd.conf(또는 apache.conf)
<Directory “/usr/local/apache2/htdocs”>
AllowOverride None
</Directory>
Step 2) AllowOverride 지시자 AuthConfig 옵션 설정
# vi /<Apache 설치 디렉터리>/httpd.conf(또는 apache.conf)
<Directory “/usr/local/apache2/htdocs”>
AllowOverride AuthConfig
</Directory>
2026
Step 3) 사용자 인증을 설정할 디렉터리에 .htaccess 파일 생성
AuthName “디렉터리 사용자 인증”
AuthType Basic
AuthUserFile /usr/local/apache/test/.auth
Require valid-user
지시자 설명
AuthName 인증 영역(웹 브라우저의 인증 창에 표시되는 문구)
AuthType 인증 형태(Basic 또는, Digest)
AuthUserFile 사용자 정보(아이디 및 비밀번호) 저장 파일 위치
AuthGroupFile 그룹 파일의 위치(옵션)
Require 접근을 허용할 사용자 또는, 그룹 정의
Step 4) 사용자 인증에 사용할 아이디 및 비밀번
```

<details><summary>참고</summary>

- “..” 는 Unicode 버그, 서비스 거부와 같은 공격에 쉽게 이용되므로 허용하지 않는 것을 권장함
</details>

### WEB-07 (중) 웹 서비스 경로 내 불필요한 파일 제거

웹 서비스 설치 시 기본으로 생성되는 불필요한 파일 및 디렉터리 제거 여부 점검 웹 서비스 설치 시 기본으로 생성되는 샘플, 매뉴얼 파일 등 서비스에 불필요한 파일을 제거하여 불필요한 공격 대상으로 이용되는 것을 방지하기 위함 웹 서비스 설치 시 기본으로 생성되는 파일 및 디렉터리나 백업, 테스트 파일 등을 제거하지 않은 경우, 비인가자에게 시스템 관련 정보 및 웹 서버 정보가 노출되거나 해킹에 악용될 수 있음 참고

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 기본으로 생성되는 불필요한 파일 및 디렉터리가 존재하지 않을 경우 |
| 🔴 취약 | 기본으로 생성되는 불필요한 파일 및 디렉터리가 존재하는 경우 |

**조치 방법**: 불필요한 파일 및 디렉터리를 제거하도록 설정

**조치 예시 (Apache)**
```apache
Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거
# rm –rf /<Apache 설치 디렉터리>/htdocs/manual
# rm –rf /<Apache 설치 디렉터리>/manual
※ 2.4 버전 이상은 htdocs 디렉터리가 기본 제공되지 않으므로 /var/www/html 사용
```

<details><summary>참고</summary>

- 불필요한 파일: 샘플 파일, 매뉴얼 파일, 임시 파일, 테스트 파일, 백업 파일 등
</details>

### WEB-08 (하) 웹 서비스 파일 업로드 및 다운로드 용량 제한

파일 업로드 및 다운로드의 용량 제한 설정 여부 점검 기반시설 시스템은 원칙적으로 파일 업로드 및 다운로드를 금지하지만 불가피하게 파일의 업로드 및 다운로드 기능이 필요한 경우, 파일의 용량 제한을 설정하여 불필요한 업로드 및 다운로드를 방지해 서버의 과부하를 예방하고, 웹 서버 자원을 효율적으로 관리하기 위함 웹 서비스의 파일 업로드 및 다운로드의 용량을 제한하지 않은 경우, 악의적인 목적을 가진 사용자가 반복 업로드 및 웹 쉘 공격 등으로 시스템 권한을 탈취하거나 대용량 파일의 업로드 및 다운로드로 서버 자원을 고갈시켜 서비스 장애를 발생시킬 위험이 존재함 참고

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 파일 업로드 및 다운로드 용량을 제한한 경우 |
| 🔴 취약 | 파일 업로드 및 다운로드 용량을 제한하지 않은 경우 |

**조치 방법**: 파일 업로드 및 다운로드 용량을 허용 가능한 최소 범위로 제한하여 설정

**조치 예시 (Apache)**
```apache
Step 1) 설정 파일 내 LimitRequestBody 지시자에서 파일 용량 제한 설정
<Directory />
LimitRequestBody 5000000
</Directory>
```

<details><summary>참고</summary>

- 불필요한 업로드 및 다운로드: 내부 정책에 맞지 않는 업로드와 다운로드
</details>

### WEB-09 (상) 웹 서비스 프로세스 권한 제한

웹 서비스 프로세스의 관리자 권한 구동 여부 점검 웹 프로세스가 웹 서비스 운영에 필요한 최소한의 권한만을 갖도록 제한함으로써 웹 사이트 방문자가 웹 서비스의 취약점을 이용해 시스템에 대한 어떤 권한도 획득할 수 없도록 하여 침해사고 발생 시 피해 범위 확산을 방지하기 위함 웹 프로세스 권한을 제한하지 않은 경우, 웹 사이트 방문자가 웹 서비스의 취약점을 이용하여 시스템 권한을 획득할 수 있으며, 웹 취약점을 통해 접속 권한을 획득한 경우에는 관리자 권한을 획득하여 서버에 접속 후 정보의 변경, 훼손 및 유출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 웹 프로세스(웹 서비스)가 관리자 권한이 부여된 계정이 아닌 운영에 필요한 최소한의 권한을 가진 |
| 🔴 취약 | 웹 프로세스(웹 서비스)가 관리자 권한이 부여된 계정으로 구동되고 있는 경우 |

**조치 방법**: 웹 서비스 프로세스 구동 시 관리자 권한이 아닌 운영에 필요한 최소한의 권한을 가진 계정으로 구동 설정

**조치 예시 (Apache)**
```apache
Step 1) envvars 파일 내 실행 계정을 관리자 계정이 아닌 별도의 계정으로 변경
# vi /[Apache 설치 디렉터리]/envvars
export APACHE_RUN_USER=www-data
export APACHE_RUN_GROUP=www-data
Step 2) Apache 서비스 파일 소유권 변경
# chown -R www-data:www-data /etc/apache2/
# chown -R www-data:www-data /var/www/
# chown -R www-data:www-data /var/log/apache2/
Step 3) 웹 서비스 실행 계정 로그인 제한 설정
# usermod -s /sbin/nologin [사용자명]
Step 4) Apache 재구동
# systemctl restart apache2 또는 httpd
```

### WEB-10 (상) 불필요한 프록시 설정 제한

웹 서비스 불필요한 Proxy 설정제한 여부 점검 불필요한 Proxy 설정을 제한하여 자원 낭비 예방 및 관리의 복잡성을 감소시키며, 중간자 공격 등의 해킹 공격으로부터 시스템 관련 정보가 노출되거나 악용되는 것을 방지하기 위함 불필요한 Proxy 설정을 제한하지 않는 경우 공격자가 Proxy 서버를 이용하여 원래 의도되지 않은 방식으로 시스템에 접근하거나 시스템 관련 정보가 유출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 불필요한 Proxy 설정을 제한한 경우 |
| 🔴 취약 | 불필요한 Proxy 설정을 제한하지 않은 경우 |

**조치 방법**: 불필요한 Proxy 설정 존재 여부 점검 및 제한 설정

**조치 예시 (Apache)**
```apache
Step 1) apache2.conf (또는 /conf/httpd.conf) 파일 내 불필요한 Proxy 제거
<VirtualHost *:80>
ServerName www.example.com
ProxyPreserveHost On
ProxyRequests Off
ProxyPass / http://backend-server.example.com/
ProxyPassReverse / http://backend-server.example.com/
</VirtualHost>
```

### WEB-11 (중) 웹 서비스 경로 설정

웹 서버에 설정한 DocumentRoot 경로가 기본 경로와 분리되었는지 여부 점검 웹 서비스 영역 내 불필요한 경로를 분리해 웹 서비스의 침해가 시스템 영역으로 확장될 가능성을 최소화하기 위함 웹 서비스 경로를 기타 업무와 영역이 분리되지 않은 경로로 설정하거나, 불필요한 경로가 존재할 경우 외부에서 시스템 중요 파일이나 기능에 비인가 접근이 발생할 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 웹 서버 경로를 기타 업무와 영역이 분리된 경로로 설정 및 불필요한 경로가 존재하지 않는 경우 |
| 🔴 취약 | 웹 서버 경로를 기타 업무와 영역이 분리되지 않은 경로로 설정하거나 불필요한 경로가 있는 경우 |

**조치 방법**: 웹 서버의 경로를 별도의 경로로 변경 및 불필요한 경로 제거 설정

**조치 예시 (Apache)**
```apache
Step 1) apache2.conf (또는 /conf/httpd.conf) 파일 내 DocumentRoot를 별도의 경로로 변경
DocumentRoot [별도의 경로]
```

### WEB-12 (중) 웹 서비스 링크 사용 금지

웹 서비스 링크(심볼릭 링크, aliases 등) 사용 제한 여부 점검 무분별한 심볼릭 링크, 별칭(aliases) 등을 제거하여 허용하지 않은 경로에서의 접근을 차단해 경로 검증을 우회한 시스템 파일 접근을 방지하기 위함 보안상 민감한 내용이 포함되어 있는 파일이 악의적인 사용자에게 노출될 경우 침해사고로 이어질 위험이 존재함 접근을 허용한 웹 디렉터리 내에 서버의 다른 디렉터리나 파일들에 접근할 수 있는 심볼릭 링크, aliases, 바로가기 등이 존재하는 경우 해당 링크를 통해 허용하지 않은 다른 디렉터리에 액세스할 수 있는 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하지 않는 경우 |
| 🔴 취약 | 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하는 경우 |

**조치 방법**: 웹 서비스 링크 사용 제한 설정

**조치 예시 (Apache)**
```apache
Step 1) apache.conf(또는 /conf/httpd.conf) 파일 내 Options 지시자 FollowSymLinks 옵션 제거
<Directory />
Options –FollowSymLinks
#Options Indexes FollowSymLinks
</Directory>
```

<details><summary>참고</summary>

- 심볼릭 링크(Symbolic link, 소프트 링크): 사용자가 심볼릭 링크 파일을 요청하면, 시스템이 해당 참고 링크에 저장된 대상 경로를 따라가서 실제 원본 데이터를 가져와 전달
</details>

### WEB-13 (상) 웹 서비스 설정 파일 노출 제한

DB 연결 파일에 대한 접근 권한, 스크립트 매핑 등 웹 서비스에서의 DB 연결 취약점 존재 여부 점검 웹 서비스에서 DB 연결 파일에 대한 접근 권한 제한 및 불필요한 스크립트 매핑을 제거하여, DB 연결 정보(사용자 이름, 비밀번호 등)가 외부에 노출되거나 공격자의 DB 접근 및 관리자 권한 획득 등의 다양한 공격을 방지하기 위함 웹 서비스에서 DB 연결 파일에 대한 접근 권한 제한 및 불필요한 스크립트 매핑을 제거하지 않을 경우, DB 연결 파일에 존재하는 데이터베이스 관련 정보(IP주소, DB명, 비밀번호), 서버 내부 IP주소, 웹 서비스 환경설정 정보 등 보안상 민감한 내용이 악의적인 사용자에게 노출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 일반 사용자의 DB 연결 파일에 대한 접근을 제한하고, 불필요한 스크립트 매핑이 제거된 경우 |
| 🔴 취약 | 일반 사용자의 DB 연결 파일에 대한 접근을 제한하지 않거나, 불필요한 스크립트 매핑이 제거되지 않은 경우 |

**조치 방법**: 연결 취약점 제거 설정

**조치 예시 (Tomcat)**
```apache
Step 1) server.xml 파일 내 불필요한 DB 연결 리소스 설정 제거
<GlobalNamingResources>
<Resource name=“jdbc/MyDB”
auth=“Container”
type=“javax.sql.DataSource”
maxTotal=“100”
maxIdle=“30”
maxWaitMillis=“10000”
username=“dbuser”
2026
password=“dbpassword”
driverClassName=“com.mysql.jdbc.Driver”
url=“jdbc:mysql://localhost:3306/mydb”/>
</GlobalNamingResources>
Step 2) DB 연결 리소스가 존재하는 설정 파일 접근권한을 600으로 설정
# chmod 600 /[Tomcat 설치 디렉터리]/conf/server.xml
```

### WEB-14 (상) 웹 서비스 경로 내 파일의 접근 통제

웹 서비스 경로의 파일들에 대해 관리자를 제외한 일반 사용자의 파일 접근 권한 제거 여부 점검 웹 서비스 경로의 파일들에 관리자를 제외한 일반 사용자의 파일 접근 권한을 제거함으로써 인가되지 않은 사용자가 허용되지 않는 파일에 접근하는 것을 차단하기 위함 웹 서비스 경로 파일에 비인가자가 접근 가능한 경우, 해당 파일의 수정 및 삭제로 인해 웹 서비스 운영 장애 및 계정 비밀번호 정보 등의 중요한 정보가 노출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여되지 않은 경우 |
| 🔴 취약 | 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여된 경우 |

**조치 방법**: 주요 설정 파일 및 디렉터리에 불필요한 접근 권한 제거 설정

**조치 예시 (Apache)**
```apache
Step 1) 루트 디렉터리 내 불필요한 권한 삭제 또는 적절한 권한 부여
# chown –R <Apache 계정>]:<Apache 그룹> apache2.conf (또는 httpd.conf)
# chmod -R 750 apache2.conf (또는 httpd.conf)
```

<details><summary>참고</summary>

- 웹 서비스 경로 내 파일/디렉터리에 접근 권한을 허용할 때는 필요한 때에만 설정하고, 필요한 특정 참고 위치의 특정 사용자에게만 허용하도록 조치
</details>

### WEB-15 (상) 웹 서비스의 불필요한 스크립트 매핑 제거

웹 서비스 내 불필요 스크립트 매핑 제거 여부 점검 웹 서비스에서 사용하지 않는 불필요 스크립트 매핑이 존재하는지 점검하여 잠재적 을 방지하기 위함 웹 서비스에서 불필요한 스크립트 매핑을 제거하지 않은 경우, 버퍼 오버플로우(Buffer Overflow), 서비스 거부 공격(Denial of Service), 크로스 사이트 스크립팅(Cross Site Scripting) 등의 공격 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 불필요한 스크립트 매핑이 존재하지 않는 경우 |
| 🔴 취약 | 불필요한 스크립트 매핑이 존재하는 경우 |

**조치 방법**: 불필요한 스크립트 매핑 존재 여부 점검 및 제거 설정

**조치 예시 (Tomcat)**
```apache
Step 1) 설정 파일의 불필요 스크립트 매핑 제거
<servlet-mapping>
<servlet-name>UnuseServlet</servlet-name>
<url-pattern>/example/*</url-pattern>
</servlet-mapping>
※ context.xml 파일 내 명시된 설정 파일에서도 DB 연결 확인 필요
```

<details><summary>참고</summary>

- .asp나 .shtm과 같은 확장자들은 특정 DLL 파일과 매핑되어 있어, 이러한 파일들에 대한 요청이 들어오면 해당 DLL에 의해 처리됨 참고
- 스크립트 매핑: 웹 서버에서 특정 파일 확장자나 URL 경로를 특정 스크립트 처리프로그램에 연결하는 설정
</details>

### WEB-16 (중) 웹 서비스 헤더 정보 노출 제한

웹페이지 응답 헤더에서 버전 정보, 사용 중인 OS 등의 서버 정보 노출 여부 점검 HTTP 응답 헤더에서 웹 서버 버전 및 종류, OS 정보 등 웹 서버와 관련된 정보가 불필요하게 노출되는 것을 최소화하기 위함 웹 서버 및 OS 정보가 노출될 경우 공격자에 의해 해당 버전의 알려진 취약점을 이용하여 시스템 구조와 특성 노출 및 해당 취약점을 통한 공격의 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | HTTP 응답 헤더에서 웹 서버 정보가 노출되지 않는 경우 |
| 🔴 취약 | HTTP 응답 헤더에서 웹 서버 정보가 노출되는 경우 |

**조치 방법**: 응답 헤더에 표시되는 정보를 최소한으로 제한하여 설정

**조치 예시 (Apache)**
```apache
Step 1) httpd.conf (또는 apache2.conf) 파일 내 모든 디렉터리에 ServerTokens, ServerSignature 옵션 설정
<Directory/>
ServerTokens Prod
ServerSignature Off
</Directory>
※ ServerTokens 지시자 옵션
ServerTokens 지시자 옵션
키워드 제공하는 정보 예문
Prod 웹 서버 종류 Apache
Min 웹 서버 버전 Apache/2.2.3
OS 웹 서버의 버전 + 운영체제 Apache/2.2.3 (CentOS) 기본값
Apache/2.2.3 (CentOS) DAV/2
Full 웹 서버의 모든 정보
PHP/5.16
2026
```

### WEB-17 (중) 웹 서비스 가상 디렉로리 삭제

불필요한 가상 디렉터리 삭제 여부 점검 불필요한 가상 디렉터리를 삭제하여 공격이 가능한 영역을 최소화하고 정보 노출 방지 및 권한 상승 공격 등의 위험을 제거하기 위함 불필요한 가상 디렉터리를 삭제하지 않은 경우, 취약한 가상 디렉터리를 통해 시스템 권한 탈취 및 시스템 구조 등의 중요 정보가 노출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 불필요한 가상 디렉터리가 존재하지 않는 경우 |
| 🔴 취약 | 불필요한 가상 디렉터리가 존재하는 경우 |

**조치 방법**: 불필요한 가상 디렉터리 존재 여부 점검 및 삭제하도록 설정

**조치 예시 (Apache)**
```apache
Step 1) Alias 지시자 확인
# vi /[Apache 설치 디렉터리]/conf/httpd.conf(또는 apache2.conf)
Alias /virtual /var/www/virtual
<Directory /var/www/virtual>
Options Indexes FollowSymLinks
AllowOverride None
Require all granted
</Directory>
Step 2) 불필요한 가상 디렉터리 삭제
2026
```

<details><summary>참고</summary>

- 가상 디렉터리: 물리적으로 홈 디렉터리와 다른 위치에 있거나 홈 디렉터리에 종속된 디렉터리가 참고 아니어도 웹 브라우저를 통해 사용자가 접속할 때 웹사이트의 하위 디렉터리로 인식되도록 하는 기법
</details>

### WEB-18 (상) 웹 서비스 WebDAV 비활성화

웹 서비스 WebDAV 비활성화 여부 점검 WebDAV 서비스를 비활성화하여, WebDAV에서 발견되는 다수의 인증 우회 취약점을 제거하고자 함 WebDAV가 활성화되어 있는 경우 웹 서비스에 악의적으로 작성된 요청을 이용하여 인증을 우회함으로써 비밀번호로 보호된 WebDAV의 자원에 접근 (디렉터리 열람, 파일 다운로드 등)이 가능하며, WebDAV에 의해 호출된 일부 구성요소에 매개 변수를 정확하게 점검하지 않는 결함이 존재하여, 이로 인해 버퍼 오버런이 발생할 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | WebDAV 서비스를 비활성화하고 있는 경우 |
| 🔴 취약 | WebDAV 서비스를 활성화하고 있는 경우 |

**조치 방법**: WebDAV 서비스 비활성화 설정

**조치 예시 (Apache)**
```apache
Step 1) httpd.conf 파일 내 모든 디렉터리에서 WebDAV 설정 확인
# cat /[Apache_Dir]/conf/httpd.conf(또는 apache2.conf)
Dav On
Step 2) 모든 디렉터리에서 WebDAV 설정 비활성화 또는 주석 처리
# vi /[Apache_Dir]/conf/httpd.conf(또는 apache2.conf)
<Directory "/path/to/directory">
Dav Off
</Directory>
Step 3) Apache 재구동
# systemctl restart apache2
2026
l Nginx
Step 1) nginx.conf 파일 내 모든 디렉터리에서 WebDAV 설정 확인
# cat /[Nginx 설치 디렉터리]/conf/nginx.conf
location /webdav {
root /path/to/webdav;
dav_methods PUT DELETE MKCOL COPY MOVE;
dav_access user:rw group:rw all:r;
create_full_put_path on;
}
Step 2) nginx.conf 파일 내 모든 디렉터리에서 WebDAV 설정 주석 처리 또는 제거
Step 3) Nginx 재구동
# systemctl restart nginx
```

<details><summary>참고</summary>

- WebDAV(Web Distributed Authoring and Versioning): 사용자가 원격 World Wide Web 서버를 이용하여 파일을 수정하거나 처리할 수 있도록 하는 HTTP의 확장 서비스. 웹상의 참고 공동개발을 지원하기 위한 IETF 표준안(RFC 2518)으로써, 원격지 사용자 간에 인터넷상에서 파일을 공동 편집하고 관리할 수 있도록 함
</details>


---

## 3. 보안 설정

### WEB-19 (중) 웹 서비스 SSI(Server Side Includes) 사용 제한

웹 서비스 SSI 사용 제한 설정 여부 점검 웹 서비스 내 SSI 사용을 제한하여 불법적인 데이터 접근을 차단하여 웹 서버의 보안을 강화하기 위함 웹 서비스 내 SSI 사용을 제한하지 않을 경우, 공격자가 SSI 기능을 이용하여 시스템 명령 실행 및 중요 파일 탈취 등 공격이 가능하며, 이를 통해 서버 시스템 침해, 데이터 유출 등이 발생할 위험이 존재함 SSI 공격 시 HTML 페이지에 스크립트를 삽입하거나 원격으로 코드를 실행하여 웹 서비스를 악용할 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 웹 서비스 SSI 사용 설정이 비활성화되어 있는 경우 |
| 🔴 취약 | 웹 서비스 SSI 사용 설정이 활성화되어 있는 경우 |

**조치 방법**: 웹 서비스 내 불필요한 SSI 사용 제한 설정

**조치 예시 (Apache)**
```apache
Step 1) Options 지시자 Includes 옵션 확인
# vi /[Apache 설치 디렉터리]/conf/httpd.conf(또는 /conf/apache.conf)
<Directory />
Options Includes
</Directory>
Step 2) Options 지시자 Includes 옵션 제거
# vi /[Apache 설치 디렉터리]/conf/httpd.conf(또는 /conf/apache.conf)
<Directory />
Options
</Directory>
```

<details><summary>참고</summary>

- SSI(Server-Side Includes): CGI 프로그램을 작성하거나 혹은 서버 사이드 스크립트를 사용하는 언어로, 웹 서버가 사용자에게 페이지를 제공하기 전에 구문을 해석하도록 지시하는 역할을 함 참고
- SSI(Server-Side Includes) Injection: HTML 문서 내 입력받은 변수값을 서버 측에서 처리할 때 부적절한 명령문이 포함 및 실행되어 서버의 데이터가 유출되는 취약점
</details>

### WEB-20 (상) SSL/TLS 활성화

서버와 클라이언트 간 통신 시 데이터 암호화 전송 여부 점검 서버와 클라이언트 간 통신 시 데이터의 평문 전송을 사용하지 않고 데이터가 암호화되는 SSL/TLS 인증 암호화 접속을 통해 스니핑을 통한 정보 유출의 위험을 방지하기 위함 웹상의 데이터 통신 시 서버와 클라이언트 간에 데이터를 평문 전송하는 경우, 간단한 도청(스니핑)을 통해 정보가 탈취 및 도용될 위험이 존재함 SSL/TLS가 활성화되어 있지 않을 경우, 데이터는 암호화되지 않아 공격자가 중간에서 데이터를 가로채거나 도청할 수 있으며, 더 나아가 평문으로 전송되어 중간에서 변경될 우려가 있어 데이터의 정확성이 훼손될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | SSL/TLS 설정이 활성화되어 있는 경우 |
| 🔴 취약 | SSL/TLS 설정이 비활성화되어 있는 경우 |

**조치 방법**: 웹 서비스 내 SSL/TLS 활성화 설정

**조치 예시 (Apache)**
```apache
Step 1) SSL 모듈 활성화 확인
# apache2ctl –M | grep ssl
ssl_module (shared)
Step 2) SSL 가상 호스트 설정에 SSL 인증서 설정 추가
# vi /[Apache 설치 디렉터리]/sites-available/default-ssl.conf
<VirtualHost *:443>
ServerAdmin webmaster@yourdomain.com
ServerName yourdomain.com
DocumentRoot /var/www/html
SSLEngine on
SSLCertificateFile /path/to/your_domain_name.crt
SSLCertificateKeyFile /path/to/your_domain_name.key
ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
Step 3) SSL 가상 호스트 활성화
# a2ensite default-ssl
Step 4) Apache 재구동
# systemctl restart apache2
l Nginx
Step 1) SSL 인증서 파일 및 개인키 파일 준비
Step 2) nginx.conf 파일 내 SSL/TLS 설정
# vi /[Nginx 설치 디렉터리]/conf/nginx.conf
```

<details><summary>참고</summary>

- 스니핑(임의 지정): 스니퍼(Sniffer)는 "컴퓨터 네트워크상에 흘러 다니는 트래픽을 엿듣는 도청장치"라고 말할 수 있으며 "스니핑"이란 이러한 스니퍼를 이용하여 네트워크상의 데이터를 도청하는 행위를 말함 참고
- SSL(Secure Socket Layer): 인터넷상에서 정보를 암호화하여 송/수신하는 프로토콜. 현재 인터넷에서 널리 쓰이고 있는 www, FTP 등의 데이터를 암호화하여, 프라이버시에 관한 정보나 신용카드 번호, 기업 비밀 등을 안전하게 송/수신할 수 있음
</details>

### WEB-21 (중) HTTP 리디렉션

웹 서비스 접근 시 HTTP Redirection 활성화 여부 점검 HTTP 차단 및 HTTPS로 Redirection 활성화를 통해 평문으로 전송되는 데이터를 암호화하여 공격자의 데이터 스니핑에 대비하기 위함 HTTP 통신은 암호화 전송이 아닌 평문 전송을 하므로 공격자가 스니핑을 시도할 경우 관리자의 ID, 비밀번호가 노출되어 악의적 사용자가 관리자 계정을 탈취할 수 있는 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | HTTP 접근 시 HTTPS Redirection이 활성화된 경우 |
| 🔴 취약 | HTTP 접근 시 HTTPS Redirection이 비활성화된 경우 |

**조치 방법**: HTTP Redirection 활성화 설정

**조치 예시 (Apache)**
```apache
Step 1) SSL 모듈 활성화 확인
# apache2ctl -M | grep ssl
Step 1) SSL 인증서 활성화 설정
Step 2) (미설치 시) mod_rewrite 설치
# apt install mod_ssl
Step 3) HTTP Redirection 설정 확인
# vi /[Apache 설치 디렉터리]/sites-available/default-ssl.conf
<VirtualHost *:80>
ServerName example.com
Redirect permanent / https://example.com/
</VirtualHost>
2026
Step 4) SSL 가상 호스트 설정
# vi /[Apache 설치 디렉터리]/sites-available/default-ssl.conf
<VirtualHost *:80>
ServerAdmin webmaster@yourdomain.com
ServerName yourdomain.com
DocumentRoot /var/www/html
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined
</
```

### WEB-22 (하) 에러 페이지 관리

에러 페이지 내 불필요 정보 노출 여부 및 필수 에러 코드에 대해 일원화된 에러 페이지 관리 여부 점검 에러 페이지에서 웹 서버 버전 및 종류, OS 정보 등 웹 서버와 관련된 불필요한 정보 및 에러 코드를 통한 기술적 취약점이 노출되는 것을 최소화하기 위함 에러 페이지에서 불필요한 정보가 노출될 경우 공격자에 의해 해당 버전의 알려진 취약점 등을 이용하여 시스템 구조와 특성 노출 및 해당 취약점을 통한 공격의 위험이 존재함 필수 에러 코드에 대해 일원화된 에러 페이지로 관리하지 않는 경우 에러 코드를 통해 각종 정보 유추의 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 웹 서비스 에러 페이지가 별도로 지정된 경우 |
| 🔴 취약 | 웹 서비스 에러 페이지가 별도로 지정되지 않거나 에러 발생 시 중요 정보가 노출되는 경우 |

**조치 방법**: 필수 에러 코드에 대해 일원화된 에러 페이지 사용 및 에러 페이지 내 불필요 정보 노출 제한 설정

**조치 예시 (Apache)**
```apache
Step 1) httpd.conf 파일 내 에러 코드별 에러 페이지 설정 정보 확인 후 별도의 일원화된 에러 페이지 설정
# vi /[Apache 설치 디렉터리]/sites-available/000-default.conf
ErrorDocument 400 /error.html
ErrorDocument 401 /error.html
(이하 생략)
Step 2) Apache 재구동
# systemctl restart apache2
2026
```

### WEB-23 (중) LDAP 알고리즘 적절하게 구성

LDAP 연결 시 취약한 알고리즘 사용 제한 설정 여부 점검 LDAP 연결 시 안전한 비밀번호 다이제스트 알고리즘을 사용하여 비밀번호 평문 전송 시 발생할 수 있는 스니핑 등의 공격에 대비하기 위함 취약한 다이제스트 알고리즘을 사용하는 경우 공격자의 스니핑, 무차별 공격 등을 통해 인증 정보가 노출될 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하는 경우 |
| 🔴 취약 | LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하지 않는 경우 |

**조치 방법**: LDAP 연결 인증 시 SHA-256 이상의 알고리즘을 사용하도록 설정

**조치 예시 (Tomcat)**
```apache
Step 1) 비밀번호 다이제스트 알고리즘 확인 (LDAP 종류별 암호화 알고리즘 지원 여부 확인)
# grep 'digest=' /[Tomcat 설치 디렉터리]/conf/server.xml
digest="SSHA"
Step 2) 비밀번호 다이제스트 알고리즘 설정
# vi /[Tomcat 설치 디렉터리]/conf/server.xml
digest="SHA-256"
Step 3) Tomcat 재구동
# systemctl restart tomcat
※ SHA-256 이상 암호화 알고리즘 권고
2026
```

<details><summary>참고</summary>

- LDAP(Lightweight Directory Access Protocol): 네트워크상에서 조직이나 개인정보 혹은 참고 파일이나 디바이스 정보 등을 조회·관리하는 표준 프로토콜
</details>

### WEB-24 (중) 별도의 업로드 경로 사용 및 권한 설정

웹 서비스 제공 시 이용되는 파일 전송의 업로드 경로를 별도의 디렉터리 사용 및 적절한 권한 설정 여부 점검 웹 서버 루트 디렉터리 내 업로드 경로가 아닌 별도의 디렉터리에서 파일을 업로드할 수 있도록 하여 루트 디렉터리 내 악의적인 파일 업로드 및 실행을 방지하기 위함 웹 서버 내 별도의 파일 업로드 경로 사용 및 적절한 권한 설정을 하지 않을 경우, 악의적인 목적을 가진 파일을 업로드하여 시스템 침투, 중요 정보 유출 및 변조 등의 침해사고의 가능성이 있음

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 별도의 업로드 경로를 사용하고 일반 사용자의 접근 권한이 부여되지 않은 경우 |
| 🔴 취약 | 별도의 업로드 경로를 사용하지 않거나, 일반 사용자의 접근 권한이 부여된 경우 |

**조치 방법**: 제한하도록 설정

**조치 예시 (Apache)**
```apache
Step 1) apache2.conf 파일 내 업로드 경로 및 웹서비스 디렉터리 경로 확인
# vi /[Apache 설치 디렉터리]/apache2/apache2.conf(또는 apache2.conf)
<Directory /var/www/html/uploads>
Options None
AllowOverride None
Require all denied
</Directory>
Step 2) 별도 업로드 경로 생성
# mkdir [웹서비스 디렉터리 외 경로]
# mkdir /var/www/html/uploads
Step 3) 파일 실행 권한 확인
# ls -al /[Apache 업로드 디렉터리]
Step 4) 업로드 디렉터리 권한 설정
# chmod 750 /var/www/html/uploads/
# chown www-data:www-data /var/www/html/uploads/
Step 5) apache2.conf 파일 내 업로드 디렉터리 접근제한 설정
# vi /[Apache 설치 디렉터리]/apache2/apache2.conf
<Directory "/var/www/html/uploads/">
Require all denied
</Directory>
```


---

## 4. 패치 및 로그 관리

### WEB-25 (상) 주기적 보안 패치 및 벤더 권고사항 적용

최신 보안 패치 적용 여부 점검 주기적인 최신 보안 패치를 통해 보안성 및 시스템 안정성을 확보하기 위함 주기적으로 최신 보안 패치를 적용하지 않을 경우, 알려진 취약점을 이용한 공격 또는 새로운 공격에 대한 침해사고 발생 위험이 존재함

| 판단 | 기준 |
|------|------|
| 🟢 양호 | 최신 보안 패치가 적용되어 있으며, 패치 적용 정책을 수립하여 주기적인 패치 관리를 하는 경우 |
| 🔴 취약 | 최신 보안 패치가 적용되어 있지 않거나 패치 적용 정책을 수립 및 주기적인 패치 관리를 하지 않는 경우 |

**조치 방법**: 패치 적용에 따른 서비스 영향 정도를 정확히 파악하여 주기적인 패치 적용 정책 수립 및 적용하도록 설정

**조치 예시 (Apache)**
```apache
Step 1) 웹 서버 버전과 최신 패치 버전을 비교하여 확인
# /[Apache 설치 디렉터리]/httpd –v
[ Apache 웹 서버 버전 확인 ]
Step 2) Apache 사이트를 통해 주기적으로 버전 점검을 하며, 최신 버전 적용 시 충분한 테스트 후 적용 권고
※ 참고 사이트: http://httpd.apache.org/download.cgi
```

<details><summary>참고</summary>

- 최신 버전을 사용하도록 권고하고 있으나 시스템 운영상 적용이 어려운 경우 최신이 아닌 취약점이 참고 존재하지 않는 버전도 허용하고 있음
</details>
