# ida_mcp_diag.py
# IDA 안에서 File > Script file... 로 실행하세요.
# ida-pro-mcp 플러그인이 왜 안 뜨는지 진단합니다.

import os
import sys
import traceback

print("=" * 60)
print("  IDA MCP 플러그인 진단")
print("=" * 60)

# 1) IDA 파이썬 버전 (3.11 이상이어야 함)
print(f"[1] Python: {sys.version}")
if sys.version_info < (3, 11):
    print("    >>> [문제] ida-pro-mcp 는 Python 3.11 이상이 필요합니다.")
    print("    >>> idapyswitch 로 IDA 의 파이썬을 3.11+ 로 바꿔야 합니다.")
else:
    print("    OK")

# 2) IDA 가 실제로 보는 사용자 디렉터리 / 플러그인 경로
try:
    import ida_diskio

    user_dir = ida_diskio.get_user_idadir()
    print(f"[2] IDA user dir: {user_dir}")
    print(f"    IDAUSR 환경변수: {os.environ.get('IDAUSR', '(설정 안 됨)')}")

    try:
        subdirs = ida_diskio.get_ida_subdirs("plugins")
        print("    plugins 검색 경로:")
        for d in subdirs:
            print(f"      - {d}  (존재: {os.path.isdir(d)})")
    except Exception:
        pass

    plugdir = os.path.join(user_dir, "plugins")
    print(f"[3] 사용자 plugins 폴더: {plugdir}")
    if not os.path.isdir(plugdir):
        print("    >>> [문제] 폴더가 없습니다. ida-pro-mcp --install 이 실행되지 않았습니다.")
    else:
        entries = sorted(os.listdir(plugdir))
        print(f"    내용물 ({len(entries)}개): {entries}")
        loader = os.path.join(plugdir, "ida_mcp.py")
        pkg = os.path.join(plugdir, "ida_mcp")
        print(f"    ida_mcp.py  존재: {os.path.lexists(loader)}")
        print(f"    ida_mcp/    존재: {os.path.lexists(pkg)}")
        if os.path.lexists(loader):
            try:
                print(f"    ida_mcp.py -> {os.path.realpath(loader)}")
            except Exception:
                pass
        if not os.path.lexists(loader) or not os.path.lexists(pkg):
            print("    >>> [문제] 두 개가 모두 있어야 합니다.")
            print("    >>> Windows 관리자 CMD 에서:  ida-pro-mcp --install")
except Exception:
    print("[2/3] 경로 확인 실패")
    traceback.print_exc()

# 4) 실제로 import 되는지 (여기서 나는 에러가 진짜 원인)
print("[4] 플러그인 import 테스트")
try:
    import ida_diskio

    plugdir = os.path.join(ida_diskio.get_user_idadir(), "plugins")
    if plugdir not in sys.path:
        sys.path.insert(0, plugdir)
    import ida_mcp  # noqa: F401

    print("    OK - ida_mcp 패키지 import 성공")
except Exception:
    print("    >>> [문제] import 실패. 아래 에러가 원인입니다:")
    traceback.print_exc()

# 5) 로드된 플러그인 목록
print("[5] 현재 로드된 MCP 관련 모듈")
hits = [m for m in sys.modules if "mcp" in m.lower()]
print(f"    {hits if hits else '(없음 - 플러그인이 로드되지 않았습니다)'}")

# 6) 데이터베이스 로드 여부
try:
    import ida_nalt

    print(f"[6] 열린 파일: {ida_nalt.get_root_filename()}")
except Exception:
    print("[6] 열린 데이터베이스 없음 (바이너리를 먼저 열어야 합니다)")

print("=" * 60)
print("  진단 끝 - 위 [문제] 표시된 줄을 확인하세요")
print("=" * 60)
