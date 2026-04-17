import openpyxl
import json

wb = openpyxl.load_workbook('../excel/设备统计_测试用例.xlsx')
ws = wb.active

# 读取所有数据
data = []
for row in ws.iter_rows(min_row=1, max_row=100, values_only=False):
    row_data = []
    for cell in row:
        row_data.append({
            'value': cell.value,
            'coordinate': cell.coordinate
        })
    data.append(row_data)

# 打印数据
print("=" * 80)
print("测试用例内容：")
print("=" * 80)
for idx, row in enumerate(data[:30], 1):
    print(f"\n行 {idx}:")
    for cell_data in row:
        if cell_data['value'] is not None:
            print(f"  {cell_data['coordinate']}: {cell_data['value']}")
