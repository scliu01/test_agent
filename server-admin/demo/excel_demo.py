import io

import pandas as pd


def generate_single_sheet_excel():
    """在本地生成一个Excel表格"""
    # 1. 构造测试数据（字典格式，key为列名，value为列数据列表）
    data = {
        "用户ID": [1001, 1002, 1003, 1004, 1005],
        "用户名": ["张三", "李四", "王五", "赵六", "钱七"],
        "年龄": [25, 32, 28, 40, 35],
        "城市": ["北京", "上海", "广州", "深圳", "杭州"],
        "注册时间": ["2024-01-10", "2024-02-15", "2024-03-20", "2024-04-25", "2024-05-30"]
    }

    df = pd.DataFrame(data)
    excel_file_path = "单个工作表示例.xlsx"
    df.to_excel(
        excel_file_path,
        index=False,  # 关键参数：是否保留 DataFrame 的行索引（默认 True，通常需要关闭）
        header=True,  # 是否保留列名（默认 True，通常需要开启）
        sheet_name="用户信息表",  # 工作表名称（默认 Sheet1）
        engine="openpyxl"  # 指定引擎（生成 .xlsx 用 openpyxl，生成 .xls 用 xlwt）
    )


def generate_single_sheet_excel_in_memory():
    """在内存中生成单个工作表的Excel（使用io.BytesIO，不写入本地磁盘）"""
    # 1. 构造测试数据
    data = {
        "用户ID": [1001, 1002, 1003, 1004, 1005],
        "用户名": ["张三", "李四", "王五", "赵六", "钱七"],
        "年龄": [25, 32, 28, 40, 35],
        "城市": ["北京", "上海", "广州", "深圳", "杭州"],
        "注册时间": ["2024-01-10", "2024-02-15", "2024-03-20", "2024-04-25", "2024-05-30"]
    }

    # 2. 转换为 pandas DataFrame
    df = pd.DataFrame(data)

    # 3. 初始化 io.BytesIO 内存字节流对象（核心：替代本地文件）
    output = io.BytesIO()

    # 4. 向内存字节流中写入 Excel 数据
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,  # 关闭行索引
            header=True,  # 保留列名
            sheet_name="用户信息表",
            freeze_panes=(1, 0)  # 冻结表头（第一行），提升Excel使用体验
        )

    # 5. 关键操作：将文件指针重置到字节流起始位置（否则后续读取会得到空数据）
    output.seek(0)

if __name__ == '__main__':
    # generate_single_sheet_excel()
    generate_single_sheet_excel_in_memory()
