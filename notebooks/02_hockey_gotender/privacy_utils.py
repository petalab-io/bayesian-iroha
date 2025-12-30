import pandas as pd


def obfuscate_name(full_name):
    """
    実名をイニシャル形式（例: Sergei Bobrovsky -> S. B.）に変換し、個人を特定しにくくする
    """
    if pd.isna(full_name) or full_name == '':
        return "Unknown"

    parts = str(full_name).split()
    if len(parts) >= 2:
        # 姓名がある場合: First Initial. Last Initial.
        return f"{parts[0][0]}. {parts[1][0]}."
    else:
        # 名前が１つの場合: 最初の2文字
        return f"{parts[0][:2]}."
