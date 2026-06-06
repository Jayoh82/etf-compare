"""
비밀번호 해시 생성기
사용법: python make_password.py
"""
import bcrypt

print("=" * 40)
print("ETF 앱 비밀번호 해시 생성기")
print("=" * 40)

while True:
    pw = input("\n비밀번호 입력 (종료: q): ").strip()
    if pw.lower() == "q":
        break
    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    print(f"해시값: {hashed}")
    print("→ secrets.toml의 password 항목에 복사하세요")
