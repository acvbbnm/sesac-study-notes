# Lab3 CNAPP 진단 결과서 — 추가 항목: S3 Public Access Block

| | |
|---|---|
| 진단 대상 계정 | 885296137678 |
| 조회 자격증명 | lab-cloudsec-dev-lab3-student |
| 진단 리전 | ap-northeast-2 |
| 진단 시각 | 2026-09-07 06:07:41 UTC (KST 15:07:41) |
| 진단 항목 | CNAPP Top 10 외 추가 항목 — S3 버킷 Public Access Block 설정 여부 |

---

## 1. 진단 기준

| 서비스 | 진단 항목 | 중요도 | 취약 기준 | 양호 기준 | 진단 방법 |
|---|---|---|---|---|---|
| S3 | Public Access Block 미설정 | HIGH | `BlockPublicAcls`/`IgnorePublicAcls`/`BlockPublicPolicy`/`RestrictPublicBuckets` 중 하나 이상 `False` (또는 설정 자체 없음) | 4개 항목 모두 `True` | `s3:GetBucketPublicAccessBlock` 호출 결과의 `PublicAccessBlockConfiguration` 값으로 판정 |

**필요 권한:** `s3:ListAllMyBuckets`, `s3:GetBucketPublicAccessBlock` (읽기 전용)

**Top10과의 관계:** Top10 2번 항목("S3 버킷 퍼블릭 정책 허용 여부")은 정책 자체가 퍼블릭인지만 본다. 이 항목은 그 정책 실수를 막아줄 **최종 안전장치**가 켜져 있는지를 별도로 확인한다.

**4개 설정을 각각 확인하는 이유:** 퍼블릭 노출로 이어지는 경로가 하나가 아니라 네 가지이므로, 하나만 봐서는 다른 경로로 뚫릴 수 있다.

| 플래그 | 막는 경로 |
|---|---|
| `BlockPublicAcls` | 새 객체/버킷에 퍼블릭 ACL이 설정되는 것 자체를 차단 |
| `IgnorePublicAcls` | 이미 걸려있는 퍼블릭 ACL을 무시(무효화) |
| `BlockPublicPolicy` | 버킷 정책에 퍼블릭 허용 문구가 들어가는 것을 차단 |
| `RestrictPublicBuckets` | 정책/ACL과 무관하게, 다른 AWS 계정에서의 접근까지 제한 |

네 개 중 하나라도 꺼져 있으면 그 경로 하나만으로도 퍼블릭 노출이 가능해지므로, 진단 기준은 "4개 모두 True"를 양호로 판정한다.

## 2. 진단 결과

총 15개 버킷 중 **HIGH 6건**, LOW 9건.

| 서비스 | 진단명 | 중요도 | 대상 리소스 | 상세 근거 |
|---|---|---|---|---|
| S3 | Public Access Block not fully enabled | **HIGH** | lab-cloudsec-dev-sa-apnortheast2-885296137678 | disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block not fully enabled | **HIGH** | lab-cloudsec-dev-pb-apnortheast2-885296137678 | disabled=['BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block not fully enabled | **HIGH** | jamo.peanutz.site | disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block not fully enabled | **HIGH** | pub-share-dttlo1557 | disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block not fully enabled | **HIGH** | resume-cv.peanutz.site | disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block not fully enabled | **HIGH** | s3share.peanutz.site | disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'] |
| S3 | Public Access Block fully enabled | LOW | access-log-peanutz | all four flags True |
| S3 | Public Access Block fully enabled | LOW | aws-cloudtrail-logs-885296137678-25816a06 | all four flags True |
| S3 | Public Access Block fully enabled | LOW | croner-buckt-quefnoi | all four flags True |
| S3 | Public Access Block fully enabled | LOW | do-not-delete-ssm-diagnosis-885296137678-ap-northeast-2-f85sb | all four flags True |
| S3 | Public Access Block fully enabled | LOW | fininfra-win-validate-1773066249-28654 | all four flags True |
| S3 | Public Access Block fully enabled | LOW | lab-cloudsec-dev-lg-apnortheast2-885296137678 | all four flags True |
| S3 | Public Access Block fully enabled | LOW | lab-cloudsec-dev-tr-apnortheast2-885296137678 | all four flags True |
| S3 | Public Access Block fully enabled | LOW | lightasil-wireguard-accesslog | all four flags True |
| S3 | Public Access Block fully enabled | LOW | web-scan-pipeliner | all four flags True |

**판정: 취약 (HIGH 6건).** 특히 `lab-cloudsec-dev-sa-apnortheast2-885296137678`는 Lab1 실습에서 실제로 접근했던 버킷으로, 4개 방어 옵션이 전부 꺼져 있어 정책 실수가 그대로 외부 노출로 이어질 수 있는 상태임을 확인함.

## 3. 원본 결과 (JSON)

```json
{
  "generatedAt": "2026-09-07T06:07:41.783094+00:00",
  "region": "ap-northeast-2",
  "check": "S3 Public Access Block (Top10 외 추가 항목)",
  "summary": {
    "CRITICAL": 0,
    "HIGH": 6,
    "MEDIUM": 0,
    "LOW": 9
  },
  "findings": [
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "access-log-peanutz", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "aws-cloudtrail-logs-885296137678-25816a06", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "croner-buckt-quefnoi", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "do-not-delete-ssm-diagnosis-885296137678-ap-northeast-2-f85sb", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "fininfra-win-validate-1773066249-28654", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "jamo.peanutz.site", "detail": "disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "lab-cloudsec-dev-lg-apnortheast2-885296137678", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "lab-cloudsec-dev-pb-apnortheast2-885296137678", "detail": "disabled=['BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "lab-cloudsec-dev-sa-apnortheast2-885296137678", "detail": "disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "lab-cloudsec-dev-tr-apnortheast2-885296137678", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "lightasil-wireguard-accesslog", "detail": "all four flags True" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "pub-share-dttlo1557", "detail": "disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "resume-cv.peanutz.site", "detail": "disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block not fully enabled", "severity": "HIGH", "resource": "s3share.peanutz.site", "detail": "disabled=['BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets']" },
    { "service": "S3", "title": "Public Access Block fully enabled", "severity": "LOW", "resource": "web-scan-pipeliner", "detail": "all four flags True" }
  ]
}
```

## 4. 확인되지 않은 사항

| 항목 | 사유 |
|---|---|
| 각 버킷의 실제 객체 내용물(민감정보 포함 여부) | `GetBucketPublicAccessBlock` API 응답 범위 밖(별도 객체 조회 필요) |
| `jamo.peanutz.site`, `resume-cv.peanutz.site` 등 `peanutz.site` 계열 버킷이 이 랩 실습과 무관한 리소스인지 여부 | 계정이 랩 전용으로 격리되어 있지 않아, 이 진단 자격증명(`lab-cloudsec-dev-lab3-student`)이 계정 전체 S3를 조회 가능한 범위임을 확인함. 소유 목적은 별도 확인 필요 |
| 버킷 정책(Bucket Policy) 자체의 퍼블릭 여부와의 교차 확인 | Top10 2번 항목(`check_s3_buckets`)의 별도 결과와 대조 필요 |

## 5. 권장 조치

- **HIGH 6건**에 대해 `put_public_access_block`으로 4개 옵션(`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`) 전부 `True`로 설정
- 특히 `lab-cloudsec-dev-sa-apnortheast2-885296137678`는 Lab1에서 실제 침투 경로로 확인된 버킷이므로 최우선 조치 대상
- 퍼블릭 접근이 업무상 반드시 필요한 버킷(예: 정적 웹호스팅용)은 예외 처리하되, 허용 범위를 prefix 단위로 최소화
- 이 자격증명의 S3 조회 범위가 계정 전체인지, 태그 기반으로 제한 가능한지 인프라팀에 확인 권장(위 "확인되지 않은 사항" 참고)

## 6. 사용 코드

```python
def check_public_access_block(s3_client):
    """S3 버킷의 Public Access Block 4개 옵션 활성화 여부를 점검합니다."""
    findings = []
    buckets = s3_client.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]
        try:
            pab = s3_client.get_public_access_block(Bucket=name)
            cfg = pab["PublicAccessBlockConfiguration"]
            disabled_flags = [
                key for key in
                ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"]
                if not cfg.get(key)
            ]
            if disabled_flags:
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block not fully enabled",
                    "severity": "HIGH",
                    "resource": name,
                    "detail": f"disabled={disabled_flags}",
                })
            else:
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block fully enabled",
                    "severity": "LOW",
                    "resource": name,
                    "detail": "all four flags True",
                })
        except ClientError as err:
            code = err.response["Error"]["Code"]
            if code == "NoSuchPublicAccessBlockConfiguration":
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block not configured",
                    "severity": "HIGH",
                    "resource": name,
                    "detail": code,
                })
    return findings
```

전체 스크립트: `s3_public_access_block_audit.py` (별첨)

---
*본 보고서는 실습용 AWS 계정에 대해 읽기 전용 API로 수행한 진단 결과이며, 실제 운영 환경의 보안 상태를 대표하지 않습니다.*
