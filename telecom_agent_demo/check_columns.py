#!/usr/bin/env python3
import pandas as pd

# 设置显示
pd.set_option('display.max_columns', None)

print("=== OAO清单.xlsx ===")
df_oao = pd.read_excel("../线下表数据/OAO清单.xlsx")
print(f"行数: {len(df_oao)}, 列数: {len(df_oao.columns)}")
print("\n列名列表:")
for i, col in enumerate(df_oao.columns):
    print(f"  [{i}] {col}")

print("\n=== 投诉受理清单0313.xlsx ===")
df_complaint = pd.read_excel("../线下表数据/投诉受理清单0313.xlsx")
print(f"行数: {len(df_complaint)}, 列数: {len(df_complaint.columns)}")
print("\n列名列表:")
for i, col in enumerate(df_complaint.columns):
    print(f"  [{i}] {col}")

# 查找共同列
oao_cols = set(df_oao.columns)
complaint_cols = set(df_complaint.columns)
common = oao_cols & complaint_cols
print(f"\n共同列: {common}")
