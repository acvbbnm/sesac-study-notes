import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


def lambda_handler(event, context):
  if "body" in event and isinstance(event["body"], str):
    try:
      body = json.loads(event["body"])
    except json.JSONDecodeError:
      body = event
  else:
    body = event

  aws_access_key_id = body.get("AWS_ACCESS_KEY_ID")
  aws_secret_access_key = body.get("AWS_SECRET_ACCESS_KEY")
  region = body.get("REGION", "ap-northeast-2")

  if not aws_access_key_id or not aws_secret_access_key:
    return {
        "statusCode": 400,
        "body": json.dumps(
            {
                "service": "S3",
                "title": "S3 버킷 Public Access Block 미설정",
                "severity": "HIGH",
                "result": "취약",
                "resource": "N/A",
                "detail": (
                    "AWS 인증 정보(AWS_ACCESS_KEY_ID,"
                    " AWS_SECRET_ACCESS_KEY)가 누락되었습니다."
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
    }

  # 타임아웃 방지를 위한 boto3 설정 (연결 3초, 읽기 5초)
  aws_config = Config(
      region_name=region,
      connect_timeout=3,
      read_timeout=5,
      retries={"max_attempts": 1},
  )

  try:
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3 = session.client("s3", config=aws_config)
    response = s3.list_buckets()
    buckets = response.get("Buckets", [])
  except ClientError as e:
    return {
        "statusCode": 500,
        "body": json.dumps(
            {
                "service": "S3",
                "title": "S3 버킷 Public Access Block 미설정",
                "severity": "HIGH",
                "result": "취약",
                "resource": "N/A",
                "detail": f"AWS API 호출 중 오류 발생: {e}",
            },
            ensure_ascii=False,
            indent=2,
        ),
    }
  except Exception as e:
    return {
        "statusCode": 500,
        "body": json.dumps(
            {
                "service": "S3",
                "title": "S3 버킷 Public Access Block 미설정",
                "severity": "HIGH",
                "result": "취약",
                "resource": "N/A",
                "detail": f"타임아웃 또는 네트워크 오류 발생: {e}",
            },
            ensure_ascii=False,
            indent=2,
        ),
    }

  diagnostic_results = []

  for bucket in buckets:
    name = bucket["Name"]

    # 4개 옵션 중 하나라도 꺼져 있으면 취약으로 판단한다.
    # ACL 경로(BlockPublicAcls/IgnorePublicAcls), 정책 경로(BlockPublicPolicy),
    # 계정 간 접근 경로(RestrictPublicBuckets) 중 어느 하나만 뚫려도 퍼블릭 노출이 가능하다.
    try:
      pab = s3.get_public_access_block(Bucket=name)
      cfg = pab["PublicAccessBlockConfiguration"]
      disabled_flags = [
          key
          for key in [
              "BlockPublicAcls",
              "IgnorePublicAcls",
              "BlockPublicPolicy",
              "RestrictPublicBuckets",
          ]
          if not cfg.get(key)
      ]
    except ClientError as e:
      code = e.response["Error"]["Code"]
      if code == "NoSuchPublicAccessBlockConfiguration":
        # 설정 자체가 없는 버킷 -> 4개 항목이 전부 꺼진 것과 동일한 위험으로 처리
        disabled_flags = [
            "BlockPublicAcls",
            "IgnorePublicAcls",
            "BlockPublicPolicy",
            "RestrictPublicBuckets",
        ]
      else:
        # 그 외 에러(AccessDenied 등)는 "설정이 없다"는 근거가 아니므로
        # 취약으로 오판하지 않고 이 버킷은 결과에서 건너뛴다.
        continue

    if disabled_flags:
      result = "취약"
      severity = "HIGH"
      detail = (
          "[취약] Public Access Block 4개 옵션 중 일부가 비활성화되어 있어"
          " 버킷 정책/ACL 실수가 그대로 외부 노출로 이어질 수 있습니다."
          f" [비활성 항목]: {', '.join(disabled_flags)}"
      )
    else:
      result = "양호"
      severity = "INFO"
      detail = (
          "[양호] BlockPublicAcls/IgnorePublicAcls/BlockPublicPolicy/"
          "RestrictPublicBuckets 4개 옵션이 모두 활성화되어 있습니다."
      )

    diagnostic_results.append({
        "service": "S3",
        "title": "S3 버킷 Public Access Block 미설정",
        "severity": severity,
        "result": result,
        "resource": name,
        "detail": detail,
    })

  return {
      "statusCode": 200,
      "body": json.dumps(diagnostic_results, ensure_ascii=False, indent=2),
  }
