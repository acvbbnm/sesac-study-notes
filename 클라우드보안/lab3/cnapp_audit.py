"""
Lab3 - CNAPP boto3 자동 진단 스크립트

실행 예:
  python cnapp_audit.py --region ap-northeast-2 --tag-key Project --tag-value CloudSecurityLab --output audit-report.json

필요 권한: EC2/S3/IAM/CloudTrail 읽기 전용(ReadOnly) - Lab3 실습용 자격증명 사용
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


# ---------------------------------------------------------------------------
# 1. EC2 IMDSv1 허용 여부 (HIGH) - 웹페이지에서 제공된 샘플 코드
# ---------------------------------------------------------------------------
def check_ec2_imds(ec2_client, tag_key, tag_value):
    findings = []
    response = ec2_client.describe_instances(
        Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}]
    )

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_id = instance["InstanceId"]
            tokens = instance.get("MetadataOptions", {}).get("HttpTokens", "unknown")
            if tokens != "required":
                findings.append({
                    "service": "EC2",
                    "title": "IMDSv1 allowed",
                    "severity": "HIGH",
                    "resource": instance_id,
                    "detail": "HttpTokens is not required",
                })
            else:
                findings.append({
                    "service": "EC2",
                    "title": "IMDSv2 enforced",
                    "severity": "LOW",
                    "resource": instance_id,
                    "detail": "HttpTokens is required",
                })

            # 10. EC2 Public IP 부여 여부 (LOW)
            public_ip = instance.get("PublicIpAddress")
            if public_ip:
                findings.append({
                    "service": "EC2",
                    "title": "Public IP assigned",
                    "severity": "LOW",
                    "resource": instance_id,
                    "detail": f"PublicIpAddress={public_ip}",
                })

    return findings


# ---------------------------------------------------------------------------
# 5/6. 보안그룹 인바운드 전체공개 (MEDIUM) - 관리포트는 별도 표시
# ---------------------------------------------------------------------------
MANAGEMENT_PORTS = {22, 3389}


def check_security_groups(ec2_client):
    findings = []
    response = ec2_client.describe_security_groups()

    for sg in response.get("SecurityGroups", []):
        sg_id = sg["GroupId"]
        for perm in sg.get("IpPermissions", []):
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            for ip_range in perm.get("IpRanges", []):
                if ip_range.get("CidrIp") != "0.0.0.0/0":
                    continue

                is_management = (
                    from_port is not None
                    and to_port is not None
                    and any(from_port <= p <= to_port for p in MANAGEMENT_PORTS)
                )
                findings.append({
                    "service": "EC2/SG",
                    "title": "Management port open to 0.0.0.0/0" if is_management
                              else "Port open to 0.0.0.0/0",
                    "severity": "MEDIUM",
                    "resource": sg_id,
                    "detail": f"port {from_port}-{to_port} open to 0.0.0.0/0",
                })

    return findings


# ---------------------------------------------------------------------------
# 2/7/9. S3 퍼블릭 정책 / 기본 암호화 / 버저닝 (TODO 과제 항목)
# ---------------------------------------------------------------------------
def check_s3_buckets(s3_client):
    findings = []
    buckets = s3_client.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]

        # 2. 퍼블릭 정책 허용 여부 (HIGH)
        try:
            status = s3_client.get_bucket_policy_status(Bucket=name)
            is_public = status["PolicyStatus"]["IsPublic"]
            findings.append({
                "service": "S3",
                "title": "Bucket policy is public" if is_public else "Bucket policy is not public",
                "severity": "HIGH" if is_public else "LOW",
                "resource": name,
                "detail": f"IsPublic={is_public}",
            })
        except ClientError as err:
            code = err.response["Error"]["Code"]
            if code != "NoSuchBucketPolicy":
                findings.append({
                    "service": "S3",
                    "title": "Bucket policy status check failed",
                    "severity": "LOW",
                    "resource": name,
                    "detail": code,
                })

        # 7. 기본 암호화 미설정 (MEDIUM) - 호출 실패(=미설정)를 MEDIUM으로 처리
        try:
            s3_client.get_bucket_encryption(Bucket=name)
        except ClientError as err:
            findings.append({
                "service": "S3",
                "title": "Default encryption not configured",
                "severity": "MEDIUM",
                "resource": name,
                "detail": err.response["Error"]["Code"],
            })

        # 9. 버저닝 비활성 (LOW)
        versioning = s3_client.get_bucket_versioning(Bucket=name)
        if versioning.get("Status") != "Enabled":
            findings.append({
                "service": "S3",
                "title": "Versioning disabled",
                "severity": "LOW",
                "resource": name,
                "detail": f"Status={versioning.get('Status', 'Disabled')}",
            })

    return findings


# ---------------------------------------------------------------------------
# 8. IAM 사용자 활성 Access Key 과다 (MEDIUM) - TODO 과제 항목
# ---------------------------------------------------------------------------
def check_iam_active_keys(iam_client):
    findings = []
    users = iam_client.list_users().get("Users", [])

    for user in users:
        user_name = user["UserName"]
        keys = iam_client.list_access_keys(UserName=user_name).get("AccessKeyMetadata", [])
        active_count = sum(1 for k in keys if k["Status"] == "Active")

        if active_count >= 2:
            findings.append({
                "service": "IAM",
                "title": "Too many active access keys",
                "severity": "MEDIUM",
                "resource": user_name,
                "detail": f"active keys={active_count}",
            })

    return findings


# ---------------------------------------------------------------------------
# 3/4. CloudTrail 미구성 / 로깅 중지 (HIGH) - TODO 과제 항목
# ---------------------------------------------------------------------------
def check_cloudtrail(cloudtrail_client):
    findings = []
    trails = cloudtrail_client.describe_trails().get("trailList", [])

    if not trails:
        findings.append({
            "service": "CloudTrail",
            "title": "No CloudTrail configured",
            "severity": "HIGH",
            "resource": "account",
            "detail": "describe_trails returned no trail",
        })
        return findings

    for trail in trails:
        name = trail["Name"]
        status = cloudtrail_client.get_trail_status(Name=trail["TrailARN"])
        is_logging = status.get("IsLogging", False)

        findings.append({
            "service": "CloudTrail",
            "title": "Logging stopped" if not is_logging else "Logging enabled",
            "severity": "HIGH" if not is_logging else "LOW",
            "resource": name,
            "detail": f"IsLogging={is_logging}",
        })

    return findings


# ---------------------------------------------------------------------------
# [추가 A] EC2: 기본 보안그룹 규칙 잔존 / EBS 미암호화 / AMI 퍼블릭 공개
# ---------------------------------------------------------------------------
def check_ec2_extra(ec2_client):
    findings = []

    # 기본 SG에 인바운드/아웃바운드 규칙이 남아있는지
    sgs = ec2_client.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": ["default"]}]
    ).get("SecurityGroups", [])
    for sg in sgs:
        if sg.get("IpPermissions") or sg.get("IpPermissionsEgress"):
            findings.append({
                "service": "EC2/SG",
                "title": "Default security group has rules",
                "severity": "MEDIUM",
                "resource": sg["GroupId"],
                "detail": "default SG는 규칙이 비어있어야 정상",
            })

    # EBS 볼륨 미암호화
    # describe_volumes 하나가 막혀도 위에서 이미 계산한 default SG 결과는 지켜야 하므로
    # 이 호출만 따로 try/except로 감싼다.
    try:
        volumes = ec2_client.describe_volumes().get("Volumes", [])
        for vol in volumes:
            if not vol.get("Encrypted", False):
                findings.append({
                    "service": "EC2/EBS",
                    "title": "EBS volume not encrypted",
                    "severity": "MEDIUM",
                    "resource": vol["VolumeId"],
                    "detail": "Encrypted=False",
                })
    except ClientError as err:
        print(f"[WARN] EBS 점검 건너뜀(권한 부족): {err.response['Error']['Code']}", file=sys.stderr)

    # 자체 소유 AMI 퍼블릭 공개
    try:
        images = ec2_client.describe_images(Owners=["self"]).get("Images", [])
        for image in images:
            if image.get("Public", False):
                findings.append({
                    "service": "EC2/AMI",
                    "title": "AMI is public",
                    "severity": "HIGH",
                    "resource": image["ImageId"],
                    "detail": "Public=True",
                })
    except ClientError as err:
        print(f"[WARN] AMI 점검 건너뜀(권한 부족): {err.response['Error']['Code']}", file=sys.stderr)

    return findings


# ---------------------------------------------------------------------------
# [추가 B] S3: Public Access Block 미설정 / 접근 로그(access logging) 미설정
# ---------------------------------------------------------------------------
def check_s3_extra(s3_client):
    findings = []
    buckets = s3_client.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]

        try:
            pab = s3_client.get_public_access_block(Bucket=name)
            cfg = pab["PublicAccessBlockConfiguration"]
            if not all([
                cfg.get("BlockPublicAcls"), cfg.get("IgnorePublicAcls"),
                cfg.get("BlockPublicPolicy"), cfg.get("RestrictPublicBuckets"),
            ]):
                findings.append({
                    "service": "S3",
                    "title": "Public Access Block not fully enabled",
                    "severity": "HIGH",
                    "resource": name,
                    "detail": str(cfg),
                })
        except ClientError as err:
            findings.append({
                "service": "S3",
                "title": "Public Access Block not configured",
                "severity": "HIGH",
                "resource": name,
                "detail": err.response["Error"]["Code"],
            })

        logging_cfg = s3_client.get_bucket_logging(Bucket=name)
        if "LoggingEnabled" not in logging_cfg:
            findings.append({
                "service": "S3",
                "title": "Access logging not configured",
                "severity": "LOW",
                "resource": name,
                "detail": "LoggingEnabled missing",
            })

    return findings


# ---------------------------------------------------------------------------
# [추가 C] IAM: 콘솔 사용자 MFA 미설정 / 계정 비밀번호 정책 / 사용자 직결 admin 권한
# ---------------------------------------------------------------------------
def check_iam_extra(iam_client):
    findings = []
    users = iam_client.list_users().get("Users", [])

    for user in users:
        user_name = user["UserName"]

        has_console_access = True
        try:
            iam_client.get_login_profile(UserName=user_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchEntity":
                has_console_access = False

        # list_mfa_devices가 막혀도 아래 AdministratorAccess 점검은 계속 돌아야 하므로
        # 사용자 한 명 단위로 try/except를 건다 (함수 전체가 죽지 않도록).
        if has_console_access:
            try:
                mfa_devices = iam_client.list_mfa_devices(UserName=user_name).get("MFADevices", [])
                if not mfa_devices:
                    findings.append({
                        "service": "IAM",
                        "title": "Console user without MFA",
                        "severity": "HIGH",
                        "resource": user_name,
                        "detail": "login profile exists, no MFA device",
                    })
            except ClientError as err:
                print(f"[WARN] {user_name} MFA 점검 건너뜀(권한 부족): {err.response['Error']['Code']}", file=sys.stderr)

        try:
            attached = iam_client.list_attached_user_policies(UserName=user_name).get("AttachedPolicies", [])
            for policy in attached:
                if policy["PolicyName"] == "AdministratorAccess":
                    findings.append({
                        "service": "IAM",
                        "title": "AdministratorAccess attached directly to user",
                        "severity": "HIGH",
                        "resource": user_name,
                        "detail": "role를 통하지 않고 사용자에 직접 관리자 권한 연결",
                    })
        except ClientError as err:
            print(f"[WARN] {user_name} 정책 점검 건너뜀(권한 부족): {err.response['Error']['Code']}", file=sys.stderr)

    try:
        iam_client.get_account_password_policy()
    except ClientError as err:
        if err.response["Error"]["Code"] == "NoSuchEntity":
            findings.append({
                "service": "IAM",
                "title": "Account password policy not configured",
                "severity": "MEDIUM",
                "resource": "account",
                "detail": "get_account_password_policy: NoSuchEntity",
            })

    return findings


# ---------------------------------------------------------------------------
# [추가 D] CloudTrail: 멀티리전 미설정 / 로그 파일 무결성 검증 미설정
# ---------------------------------------------------------------------------
def check_cloudtrail_extra(cloudtrail_client):
    findings = []
    trails = cloudtrail_client.describe_trails().get("trailList", [])

    for trail in trails:
        name = trail["Name"]

        if not trail.get("IsMultiRegionTrail", False):
            findings.append({
                "service": "CloudTrail",
                "title": "Trail is not multi-region",
                "severity": "MEDIUM",
                "resource": name,
                "detail": "IsMultiRegionTrail=False",
            })

        if not trail.get("LogFileValidationEnabled", False):
            findings.append({
                "service": "CloudTrail",
                "title": "Log file validation disabled",
                "severity": "MEDIUM",
                "resource": name,
                "detail": "LogFileValidationEnabled=False",
            })

    return findings


# ---------------------------------------------------------------------------
# 실행부
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Lab3 CNAPP boto3 audit")
    parser.add_argument("--region", required=True)
    parser.add_argument("--tag-key", required=True)
    parser.add_argument("--tag-value", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    session = boto3.Session(region_name=args.region)
    ec2 = session.client("ec2")
    s3 = session.client("s3")
    iam = session.client("iam")
    cloudtrail = session.client("cloudtrail")

    findings = []
    checks = [
        ("EC2 IMDS/PublicIP", lambda: check_ec2_imds(ec2, args.tag_key, args.tag_value)),
        ("Security Groups", lambda: check_security_groups(ec2)),
        ("S3 buckets", lambda: check_s3_buckets(s3)),
        ("IAM active keys", lambda: check_iam_active_keys(iam)),
        ("CloudTrail", lambda: check_cloudtrail(cloudtrail)),
        # --- Top10 목록 외 추가 진단 항목 ---
        ("EC2 extra (default SG/EBS/AMI)", lambda: check_ec2_extra(ec2)),
        ("S3 extra (Public Access Block/logging)", lambda: check_s3_extra(s3)),
        ("IAM extra (MFA/password policy/admin)", lambda: check_iam_extra(iam)),
        ("CloudTrail extra (multi-region/validation)", lambda: check_cloudtrail_extra(cloudtrail)),
    ]

    for label, fn in checks:
        try:
            findings.extend(fn())
        except ClientError as err:
            print(f"[WARN] {label} 점검 중 오류(권한 부족 등): {err}", file=sys.stderr)

    summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in findings:
        summary[item["severity"]] = summary.get(item["severity"], 0) + 1

    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "region": args.region,
        "tagKey": args.tag_key,
        "tagValue": args.tag_value,
        "summary": summary,
        "findings": findings,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"총 {len(findings)}건 진단 완료 -> {args.output}")
    print(f"요약: {summary}")


if __name__ == "__main__":
    main()
