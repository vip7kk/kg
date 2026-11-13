#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成 config/sh*.json

用法（脚本位于 .github/workflows/，生成结果写入仓库根目录的 config/）:
    python generate_sh.py --start 11 --end 30              # 生成 sh11.json ~ sh30.json
    python generate_sh.py --start 2  --end 2  --overwrite  # 允许覆盖已存在的文件
    python generate_sh.py --range 11-30                    # 等价写法
可选参数:
    --prefix sh        文件名前缀，默认 sh
    --short "A,B,C"    覆盖模板里的 short 列表
    --pad 2            编号补零位数（sh02 -> 2 位）
"""

import argparse
import copy
import json
import os
import sys

# ======================================================================
# 模板配置：与 config/sh07.json 内容一致，需要改内容时只改这一块即可
# ======================================================================
DEFAULT_TEMPLATE = {
    "data": {
        "title": "welcome",
        "id": "123",
        "short": ["A", "B", "C"],
    }
}


def main():
    ap = argparse.ArgumentParser(description="批量生成 sh*.json")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--start", type=int, help="起始编号")
    g.add_argument("--range", dest="rng", help="范围，如 11-30")
    ap.add_argument("--end", type=int, help="结束编号（与 --start 搭配）")
    ap.add_argument("--prefix", default="sh")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在的文件")
    ap.add_argument("--short", help="覆盖 short 列表，逗号分隔，如 A,B,C")
    ap.add_argument("--pad", type=int, default=2, help="编号补零位数，默认 2")
    args = ap.parse_args()

    if args.rng:
        try:
            start_s, end_s = args.rng.split("-")
            start, end = int(start_s), int(end_s)
        except ValueError:
            sys.exit("--range 格式应为 11-30")
    else:
        if args.end is None:
            sys.exit("使用 --start 时必须同时给 --end，或改用 --range 11-30")
        start, end = args.start, args.end
    if end < start:
        sys.exit("结束编号不能小于起始编号")

    # 模板拷贝，避免污染全局
    template = copy.deepcopy(DEFAULT_TEMPLATE)
    if args.short:
        template["data"]["short"] = [s.strip() for s in args.short.split(",") if s.strip()]

    # 输出目录 = 仓库根目录下的 config/（脚本在 .github/workflows/，向上两级）
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_dir = os.path.join(repo_root, "config")
    created, skipped = [], []

    for n in range(start, end + 1):
        name = "{}{}.json".format(args.prefix, str(n).zfill(args.pad))
        path = os.path.join(out_dir, name)
        if os.path.exists(path) and not args.overwrite:
            skipped.append(name)
            continue
        with open(path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        created.append(name)

    print("生成 {} 个: {}".format(len(created), ", ".join(created) or "无"))
    if skipped:
        print("跳过已存在 {} 个: {}（加 --overwrite 可覆盖）".format(len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
