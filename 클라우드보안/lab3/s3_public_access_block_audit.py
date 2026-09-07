"""
S3 Public Access Block 단일 진단 스크립트 (CNAPP Top10 외 추가 항목)

실행 예:
  python s3_public_access_block_audit.py --region ap-northeast-2 --output pab-report.json

필요 권한: s3:ListAllMyBuckets, s3:GetBucketPublicAccessBlock (ReadOnly)
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


def check_public_access_block(s3_client):
    findings = []
    buckets = s3_client.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]

        try:
            pab = s3_client.get_public_access_block(Bucket=name)
            cfg = pab["PublicAccessBlockConfiguration"]
            # 4개 옵션 중 하나라도 False(꺼짐)면 그 이름을 모아둔다.
            # ACL 경로(BlockPublicAcls/IgnorePublicAcls), 정책 경로(BlockPublicPolicy),
            # 계정 간 접근 경로(RestrictPublicBuckets) 중 어느 하나만 뚫려도 퍼블릭 노출이 가능하다.
            disabled_flags = [
                key for key in
                ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"]
                if not cfg.get(key)
            ]

            if disabled_flags:
                # 하나라도 꺼져 있으면 "지금 당장 퍼블릭인지"와 무관하게
                # 향후 정책/ACL 실수를 막아줄 안전장치가 없는 상태이므로 HIGH로 기록.
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block not fully enabled",
                    "severity": "HIGH",
                    "resource": name,
                    "detail": f"disabled={disabled_flags}",
                })
            else:
                # 4개 옵션이 전부 켜져 있으면 정책/ACL 실수가 나도 AWS가 강제로 막아주는 상태 -> 양호.
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
                # 설정 자체가 한 번도 만들어진 적 없는 버킷 -> 4개 항목이 전부 꺼진 것과
                # 동일한 위험이므로 disabled_flags 케이스와 똑같이 HIGH로 처리한다.
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block not configured",
                    "severity": "HIGH",
                    "resource": name,
                    "detail": code,
                })
            else:
                # 그 외 에러(예: AccessDenied)는 "설정이 없다"는 근거가 아니라 "확인 자체가
                # 안 됐다"는 뜻이므로, 취약으로 오판하지 않고 경고만 남긴 뒤 건너뛴다.
                print(f"[WARN] {name} 점검 실패({code})", file=sys.stderr)

    return findings


def parse_args():
    parser = argparse.ArgumentParser(description="S3 Public Access Block audit")
    parser.add_argument("--region", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    s3 = boto3.Session(region_name=args.region).client("s3")

    findings = check_public_access_block(s3)
    summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in findings:
        summary[item["severity"]] = summary.get(item["severity"], 0) + 1

    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "region": args.region,
        "check": "S3 Public Access Block (Top10 외 추가 항목)",
        "summary": summary,
        "findings": findings,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"총 {len(findings)}건 진단 완료 -> {args.output}")
    print(f"요약: {summary}")


if __name__ == "__main__":
    main()
