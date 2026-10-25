"""Put only measured dev observations into the original 第8回 template sections."""
from collections import defaultdict
from pathlib import Path
from statistics import mean
from observations import read_observations

PLAN = Path(__file__).resolve().parent / "PROTOTYPE_EVAL_PLAN.md"


def section_replace(text: str, name: str, replacement: str) -> str:
    start = f"<!-- {name}_BEGIN -->"
    end = f"<!-- {name}_END -->"
    if start not in text or end not in text:
        raise ValueError(f"記入位置がありません: {name}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + "\n" + replacement + "\n" + end + after


def safe(s: str) -> str:
    return str(s or "").replace("|", "／").replace("\n", " ")


def main():
    rows = read_observations()
    if not rows:
        print("実測値がありません。まずStreamlitで試行を記録してください。文書は変更していません。")
        return
    text = PLAN.read_text(encoding="utf-8")
    first = rows[0]
    first_data = (
        "```text\n"
        f"入力: mode={first['input_mode']} shape={first['shape']} "
        f"dtype={first['dtype']} pixel_range=[{first['min']}, {first['max']}]\n"
        f"モデル出力（実測）: label={first['predicted_label']} score={first['score'] or 'N/A'} "
        f"num_hands={first['num_hands']} landmarks={first['num_landmarks']} "
        f"handedness={first['handedness'] or 'N/A'}\n"
        f"生のcategories: {first['raw_categories']}\n"
        f"推論時間: {first['inference_ms']} ms / 実行予定環境 CPU\n"
        "```"
    )
    text = section_replace(text, "ACTUAL_INPUT_OUTPUT", first_data)

    lines = ["| 入力 | 画面に表示された結果 | 期待どおりか |", "|---|---|---|"]
    for r in rows:
        intro = f"{safe(r['source'])}・{safe(r['lighting'])}・正解={safe(r['expected_label'])}"
        if r["notes"]:
            intro += f"（{safe(r['notes'])}）"
        detail = f"{safe(r['predicted_label'])} score={r['score'] or 'N/A'} / {safe(r['action'])}"
        result = "○" if r["correct"] == "1" else "×（誤認識）"
        lines.append(f"| {intro} | {detail} | {result} |")
    if not any(r["expected_label"] == "None" for r in rows):
        lines.append("| 対象外の入力 | **未測定：必須の追加試行** | 未確認 |")
    text = section_replace(text, "ACTUAL_CHECK_TABLE", "\n".join(lines))

    groups = defaultdict(list)
    for r in rows:
        groups[r["lighting"]].append(r)
    lines = ["```text", f"dev 実測の合計: {len(rows)} 独立試行"]
    for key, items in sorted(groups.items()):
        hit = sum(r["correct"] == "1" for r in items)
        false_triggers = sum(r["expected_label"] == "None" and r["action"] != "NO_ACTION（発動なし）" for r in items)
        latency = mean(float(r["inference_ms"]) for r in items)
        lines.append(f"{key}: 認識成功={hit}/{len(items)} ({hit/len(items):.1%}), 対象外誤発動={false_triggers}, 平均推論={latency:.1f} ms")
    if not ("normal" in groups and "dim" in groups):
        lines.append("条件比較: 片方の照明データが不足。比較結果はまだ出せない。")
    lines.append("```")
    text = section_replace(text, "ACTUAL_DEV_RESULT", "\n".join(lines))
    text = text.replace(
        "- [ ] モデルの入出力を、実際に表示した値で確認した（**ローカル実行後**）",
        "- [x] モデルの入出力を、実際に表示した値で確認した（ローカル実行ログ）",
    )
    if any(r["expected_label"] == "None" for r in rows) and any(r["expected_label"] != "None" for r in rows):
        text = text.replace(
            "- [ ] 入力から出力までの動作確認を、対象外の入力も含めて記録した（**ローカル実行後**）",
            "- [x] 入力から出力までの動作確認を、対象外の入力も含めて記録した（ローカル実行ログ）",
        )
    PLAN.write_text(text, encoding="utf-8")
    print(f"実測値 {len(rows)} 件を {PLAN.name} に反映しました。最後に内容を確認してください。")

if __name__ == "__main__":
    main()
