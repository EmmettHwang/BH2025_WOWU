import pandas as pd
import json

# Excel 파일 읽기
df = pd.read_excel('student_template.xlsx')

# 데이터프레임 정보 출력
print("=== Excel 파일 구조 ===")
print(f"행 개수: {len(df)}")
print(f"열 개수: {len(df.columns)}")
print("\n=== 컬럼명 ===")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

print("\n=== 샘플 데이터 (첫 3행) ===")
print(df.head(3).to_string())

print("\n=== 데이터 타입 ===")
print(df.dtypes)

print("\n=== JSON 형식으로 첫 행 출력 ===")
if len(df) > 0:
    first_row = df.iloc[0].to_dict()
    print(json.dumps(first_row, ensure_ascii=False, indent=2, default=str))
