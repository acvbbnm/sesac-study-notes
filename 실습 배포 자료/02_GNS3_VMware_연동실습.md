# 02. GNS3 설치와 VMware 연동

출처: 로컬 `3일차 실습 자료/gns3_v2/GNS3 설치 및 Vmware 연동 가이드.pdf`, 23쪽.

## 1. 환경 준비 (p.2-6)

GNS3는 네트워크 장비와 VM을 연결해 토폴로지를 구성하는 실습 도구다. 교안 기준 설치 파일은 `GNS3-2.2.31-all-in-one-regular.exe`다. 설치 후 새 프로젝트 이름을 정하고 장비 도구·작업 공간·메시지 창을 확인한다.

## 2. IOS 등록 (p.7-13)

1. Edit → Preferences → Dynamips → IOS routers를 연다.
2. 배포된 라우터 IOS 이미지를 등록한다.
3. 장비 이름과 플랫폼 등 설정을 확인하고 등록을 완료한다.
4. 교안의 스위치용 등록 과정에서는 `This is an EtherSwitch router` 설정을 사용한다.
5. 라우터와 스위치 템플릿이 목록에 생성됐는지 확인한다.

파일 확장자만 바꾸거나 임의 이미지를 선택하는 과정이 아니다. 실제 배포된 이미지와 장비 설정의 대응이 필요하다.

## 3. VMware 네트워크 연결 (p.14-20)

1. VMware의 Edit → Virtual Network Editor에서 Change Settings를 선택한다.
2. 실습에 사용할 VMnet을 준비한다.
3. GNS3에 C2691 라우터, Ethernet router, Cloud 노드를 배치한다.
4. Cloud1에는 VMware Network Adapter VMnet1을 연결한다.
5. Cloud2에는 VMware Network Adapter VMnet2를 연결한다.
6. 장비의 인터페이스를 지정해 케이블을 연결한다.
7. 교안의 Windows XP VM은 VMnet1, Backtrack VM은 VMnet2를 사용한다.
8. 외부 통신 실습에서는 교안의 NAT 연결 구성을 추가한다.

```text
Windows XP VM ─ VMnet1 ─ Cloud1 ─ 네트워크 장비 ─ Cloud2 ─ VMnet2 ─ Backtrack VM
                                  │
                               NAT 연결
```

위 그림은 연결 관계를 설명하는 요약이다. 인터페이스 번호와 IP는 사용한 프로젝트 구성에 맞춰 기록한다.

## 4. 통신 확인과 장애 분리 (p.21-22)

VM을 구동한 후 주소·마스크·게이트웨이, Cloud의 VMnet 매핑, 케이블과 인터페이스 활성 상태, 라우팅을 순서대로 확인한다. VMnet이 다르면 링크가 있어도 기대한 동일 네트워크에 연결되지 않을 수 있다.

결과에는 VMware 네트워크 설정, GNS3 토폴로지, 라우터 설정, VM 간 ping과 필요 시 외부 통신을 기록한다. 현재 로컬 프로젝트의 실행·연동 성공은 확인하지 않았으며 이 문서는 교안 절차 정리다.

[목차](README.md)
