#!/usr/bin/python3
###################################################
# pwdecode.py :
#      Ver.1 2024-02-24
#      Ver.0 2024-02-23
# ■ 更新
#     ・ 正規表現を更新
#     ・ バイト列への変換のエラー処理を追加
# ■ 概要
#     PukiWiki の wiki/ 以下のファイル名はエンコードされている。
#     これを読めるようにする。実用上は、ls を使うはずなので、
#     ls に対してパイプラインで実行することを想定している。
# ■ 使用例
#     ls -ltr | cat -n | pwdecode.py
#     ※ cat -n を入れておくと、実際のファイル名と簡単に対応付けられる。
###################################################
import sys
import re

# 文字列をバイト列にしてからデコード
def try_decode(hex_str):
    try:
        # 16進数の文字列からバイト列に変換を試みる
        decoded_bytes = bytes.fromhex(hex_str)

    except ValueError:
        # 16進数の文字列が無効な場合はあきらめる
        print(f"Invalid hexadecimal number: {hex_str}")
        return None
        
    try:
        # EUC-JPとして decode する
        return decoded_bytes.decode('euc_jp')
    except UnicodeDecodeError:
        # 失敗したら次へ
        pass  
        
    try:
        # UTF-8 として decode する
        return decoded_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return None
        
# 各行のデコード
def decode_pukiwiki_filename(encoded_strings):
    decoded_filename = ''
    hex_pattern = re.compile(r'(?:(?<=^)|(?<=[\s_]))([0-9A-Fa-f]{6,})(?=[\._]|$)') # エンコードされたファイル名部分を抽出
    pos = 0

    for match in hex_pattern.finditer(encoded_strings):
        start, end = match.span()
        decoded_filename += encoded_strings[pos:start]  # 16進数でない部分を追加
        
        hex_str = match.group(1)
        decoded_part = try_decode(hex_str)
        if decoded_part is not None:
            decoded_filename += decoded_part
        else:
            decoded_filename += hex_str  # デコードに失敗した場合は元の16進数の文字列を追加
        pos = end

    decoded_filename += encoded_strings[pos:]  # 残りの部分を追加

    return decoded_filename

# 標準入力を受け取り、エンコードされた部分だけをデコード。
for line in sys.stdin:
    line = line.strip()
    decoded_filename = decode_pukiwiki_filename(line)
    print(decoded_filename)
