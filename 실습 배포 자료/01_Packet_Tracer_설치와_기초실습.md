# 01. Packet Tracer 설치와 기초 실습

출처: 로컬 `1일차 실습 자료/Packet_tracer 설치/패킷트레이서 설치 가이드.pdf`, 14쪽.

## 목적과 설치 (p.2-9)

Cisco 라우터·스위치·PC를 배치해 IP 통신과 장비 설정을 연습하는 시뮬레이션 환경이다. 교안은 배포 설치 파일 실행 후 로그인하고 작업 화면을 여는 흐름을 안내한다. 계정 화면은 교안 당시 기준이다.

설치 후 메뉴·장치 선택·케이블·작업 공간·실시간/시뮬레이션 전환을 확인한다. Options → Preferences에서 포트 이름 표시와 CLI 글자 크기를 조절한다.

## 장비 배치와 통신 (p.10-11)

1. PC·스위치·라우터를 작업 공간에 배치한다.
2. 케이블과 양쪽 포트를 선택해 연결한다.
3. PC의 IP·마스크·게이트웨이를 구성도에 맞게 설정한다.
4. 라우터·스위치 CLI에서 필요한 설정을 적용한다.
5. 링크 상태, 같은 대역 통신, 라우터 경유 통신을 차례로 확인한다.

## VLAN·Trunk·OSPF 예시 (p.12)

교안은 스위치의 Fa0/13~23을 VLAN 20에 배정하고 Fa0/24를 VLAN 10·20 트렁크로 사용하는 예를 보여준다. 재현 시 해당 VLAN과 포트가 존재하는지 먼저 확인한다.

```text
conf t
interface range fa0/13 - 23
 switchport access vlan 20
interface fa0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end
```

라우터 예시는 OSPF process 1, router-id 3.3.3.1, area 0에 다음 대역을 포함한다.

```text
conf t
router ospf 1
 router-id 3.3.3.1
 network 3.3.3.0 0.0.0.255 area 0
 network 192.168.3.0 0.0.0.255 area 0
 network 172.16.2.0 0.0.0.255 area 0
 network 172.16.3.0 0.0.0.255 area 0
end
```

이는 교안 예시를 표기 정리한 것이며 실제 로컬 장비의 설정 덤프가 아니다. 전체 IP·인터페이스 구성은 실습 토폴로지에 맞춰야 한다.

## 확장과 검증 (p.13)

교안은 WiFi 구성과 무선 사용자 인증 서버 실습도 소개한다. 구체적인 인증 값은 추정하지 않는다. 결과 기록에는 구성도, 주소표, VLAN·트렁크 상태, 라우팅 상태와 ping 성공·실패를 남긴다. 현재 사용자 실습 완료를 입증하는 Packet Tracer 실행 결과는 확인하지 않았다.

[목차](README.md)
