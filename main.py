# 消費税申告（簡易課税）2025年分（令和7年分）/ 第5種(50%) / 10%のみ / 税込経理
# 入力: 2025年の事業収入（税込）＋（任意）基準期間の課税売上高（税抜）＋ 中間納付（国税/地方）
# 出力: 第一表・第二表・付表5-3 に「記入する値」を全部プリント（0の欄も出す）

from decimal import Decimal, ROUND_DOWN
from typing import Optional

YEAR = 2025
REIWA = 7

DEEMED_PURCHASE_RATE = Decimal("0.50")  # 第5種（みなし仕入率50%）
NATIONAL_RATE = Decimal("0.078")  # 標準税率10%のうち国税7.8%
LOCAL_NUM = Decimal("22")  # 地方＝国税差引 × 22/78
LOCAL_DEN = Decimal("78")


def yen_floor(x: Decimal) -> int:
    """円未満切捨て"""
    return int(x.quantize(Decimal("1"), rounding=ROUND_DOWN))


def hundred_yen_floor_int(n: int) -> int:
    """100円未満切捨て（= 1円単位の値を100円単位に切捨て）"""
    return (n // 100) * 100


def thousand_yen_floor(x: Decimal) -> int:
    """千円未満切捨て（課税標準額）"""
    return int((x // Decimal("1000")) * Decimal("1000"))


def ask_int_yen(
    prompt: str, default: Optional[int] = None, allow_blank: bool = False
) -> int:
    while True:
        s = input(prompt).strip()
        if s == "":
            if allow_blank and default is not None:
                return default
            if default is not None:
                return default
        s2 = s.replace(",", "")
        try:
            v = int(Decimal(s2))
            if v < 0:
                print("  -> 0以上で入力してください。")
                continue
            return v
        except Exception:
            print("  -> 数値で入力してください（例：12101430）。")


def calc_all(
    gross_sales_yen: int,
    base_period_sales_excl_yen: int,
    interim_national_yen: int,
    interim_local_yen: int,
):
    gross = Decimal(gross_sales_yen)

    # A) この課税期間の課税売上高（税抜、円単位）
    # 税込額 / 1.10 で割り切れない場合は円未満切捨て
    taxable_sales_excl = gross / Decimal("1.10")
    taxable_sales_excl_yen = yen_floor(taxable_sales_excl)  # 円未満切捨て

    # B) 課税標準額（千円未満切捨て）
    taxable_base_yen = thousand_yen_floor(Decimal(taxable_sales_excl_yen))

    # C) 消費税額（国税7.8%）…円未満切捨て
    national_tax_raw = yen_floor(Decimal(taxable_base_yen) * NATIONAL_RATE)

    # D) 基礎となる消費税額（調整なし前提）
    base_national_tax = national_tax_raw

    # E) 控除対象仕入税額（簡易課税）＝基礎×みなし仕入率（円未満切捨て）
    input_tax_credit = yen_floor(Decimal(base_national_tax) * DEEMED_PURCHASE_RATE)

    # F) 差引税額（国税）＝基礎 − 控除対象仕入税額
    national_net_raw = base_national_tax - input_tax_credit
    # ★あなたの期待に合わせ「100円未満切捨て」をここで適用
    national_net = hundred_yen_floor_int(national_net_raw)

    # G) 中間納付（国税）…入力値（手引き上は“実際に納付したかどうかにかかわらず合計額を記入”）
    interim_national = interim_national_yen

    # H) 納付税額（国税）＝差引税額 − 中間納付
    national_payable_raw = national_net - interim_national
    national_payable = hundred_yen_floor_int(national_payable_raw)

    # I) 地方消費税の課税標準となる消費税額（= 国税の差引税額を基礎にする運用）
    local_tax_base = national_net

    # J) 地方消費税額（譲渡割額）＝基礎×22/78 …円未満切捨て → 100円未満切捨て（手引き例）
    local_tax_raw = yen_floor(Decimal(local_tax_base) * LOCAL_NUM / LOCAL_DEN)
    local_tax = hundred_yen_floor_int(local_tax_raw)

    # K) 中間納付（地方）…入力
    interim_local = interim_local_yen

    # L) 納付譲渡割額（地方）＝地方税額 − 中間納付
    local_payable_raw = local_tax - interim_local
    local_payable = hundred_yen_floor_int(local_payable_raw)

    # M) 合計（納付）税額
    total_payable = national_payable + local_payable

    return {
        "gross_sales": gross_sales_yen,
        "taxable_sales_excl": taxable_sales_excl_yen,  # この課税期間の課税売上高（税抜）
        "base_period_sales_excl": base_period_sales_excl_yen,  # 基準期間の課税売上高（税抜）
        "taxable_base": taxable_base_yen,  # 第一表①
        "national_tax_raw": national_tax_raw,  # 第一表②（7.8%）
        "base_national_tax": base_national_tax,  # 付表5-3 基礎
        "input_tax_credit": input_tax_credit,  # 付表5-3/第一表（控除対象仕入税額相当）
        "national_net_raw": national_net_raw,
        "national_net": national_net,  # 第一表⑨（差引税額）
        "interim_national": interim_national,
        "national_payable_raw": national_payable_raw,
        "national_payable": national_payable,  # 第一表⑪（納付税額）
        "local_tax_base": local_tax_base,  # 第一表（地方の基礎）
        "local_tax_raw": local_tax_raw,
        "local_tax": local_tax,  # 第一表⑳（納税額イメージ）
        "interim_local": interim_local,
        "local_payable_raw": local_payable_raw,
        "local_payable": local_payable,  # 第一表㉒（納付譲渡割額イメージ）
        "total_payable": total_payable,  # 第一表㉖（合計）
    }


def print_forms(r: dict):
    print("\n" + "=" * 72)
    print(f"【{YEAR}年分（令和{REIWA}年分）】消費税申告（簡易課税・第5種） 出力")
    print("前提：10%のみ／税込経理／非課税・不課税・売上以外収入なし／調整なし")
    print(
        "端数：課税標準額＝千円未満切捨て、差引・納付・地方＝100円未満切捨て（運用合わせ）"
    )
    print("=" * 72)
    print("\n■ 0固定としている前提（ここが崩れると差が出るので注意）")
    print("  ・軽減税率(8%)売上なし")
    print("  ・非課税/不課税取引なし（立替・補助金・利息等なし）")
    print("  ・返品・値引・貸倒・資産譲渡等の調整なし")
    print("=" * 72)

    # 付表4-3（簡易課税）
    print("\n■ 付表4-3: 税率別消費税額計算表（簡易課税用, 第5種：みなし仕入率50%）")
    print(
        f"  ・課税標準額（税率7.8%）①                          ：{r['taxable_base']:,} 円"
    )
    print(
        f"  ・課税資産の譲渡等の対価の額（税率7.8%）① -1           ：{r['taxable_sales_excl']:,} 円"
    )
    print(
        f"  ・消費税額（税率7.8%）②                          ：{r['national_tax_raw']:,} 円"
    )
    print(
        f"  ・控除税額: 控除対象仕入税額（税率7.8%）④           ：{r['input_tax_credit']:,} 円"
    )
    print(
        f"  ・控除税額: 控除税額小計（税率7.8%）⑦           ：{r['input_tax_credit']:,} 円"
    )
    # 差引税額 = ② + ③ - ⑦（③は0とみなす）
    fusenhyo4_3_sashihiki = r["national_tax_raw"] - r["input_tax_credit"]
    fusenhyo4_3_sashihiki_100 = (fusenhyo4_3_sashihiki // 100) * 100  # 100円未満切捨て
    print(
        f"  ・差引税額⑨と⑪（②+③-⑦）【100円未満切捨て】  ：{fusenhyo4_3_sashihiki_100:,} 円"
        f"（参考：切捨て前 {fusenhyo4_3_sashihiki:,} 円）"
    )
    print(
        f"  ・譲渡割額: 納税額 ⑬                         ：{r['local_tax']:,} 円"
    )

    # 付表5-3（簡易課税）
    print("\n■ 付表5-3: 控除対象仕入れ税額等の計算表（簡易課税用, 第5種：みなし仕入率50%）")
    print(
        f"  ・課税標準額に対する消費税額（税率7.8%）①        ：{r['national_tax_raw']:,} 円"
    )
    print(
        f"  ・基礎となる消費税額 ④                         ：{r['base_national_tax']:,} 円（調整なし前提）"
    )
    print("  ・みなし仕入率                                 ：50%（第5種）")
    print(
        f"  ・控除対象仕入税額（= 基礎×50%）               ：{r['input_tax_credit']:,} 円"
    )
    # print(
    #     f"  ・この課税期間の課税売上高（税抜）             ：{r['taxable_sales_excl']:,} 円（不足分として追加）"
    # )
    # print(
    #     f"  ・課税標準額（千円未満切捨て）                 ：{r['taxable_base']:,} 円（→ 第一表①/第二表へ）"
    # )
    # print(
    #     f"  ・消費税額（税率7.8%）                         ：{r['national_tax_raw']:,} 円（→ 第一表②/第二表へ）"
    # )

    # 控除税額ブロック
    control_3 = 0  # ③ 貸倒れに係る税額等（前提で0）
    control_4 = r["input_tax_credit"]  # ④ 控除対象仕入税額（簡易課税）
    control_5 = 0  # ⑤ 返還等（前提で0）
    control_6 = 0  # ⑥ その他（前提で0）
    control_7 = control_4 + control_5 + control_6  # ⑦ ④+⑤+⑥
    # ⑧ 控除不足還付税額 = ⑦ - ② - ③（⑦が②+③を上回る場合のみ発生）
    shortfall = control_7 - r["national_tax_raw"] - control_3
    control_8 = max(shortfall, 0)  # マイナスなら還付なし（0）

    print(
        "\n■ 申告書 第一表（消費税：国税分）に記入する値"
    )
    print(
        f"  第一表① 課税標準額                              ：{r['taxable_base']:,} 円"
    )
    print(
        f"  第一表② 消費税額（7.8%）                        ：{r['national_tax_raw']:,} 円"
    )
    print("  第一表③ 貸倒れに係る税額等                      ：0 円（前提）")

    print(f"  第一表④ 控除対象仕入税額（簡易課税）             ：{control_4:,} 円")
    print(f"  第一表⑤ 返還等対価に係る税額等                  ：{control_5:,} 円")
    print(f"  第一表⑥ その他の控除税額等                      ：{control_6:,} 円")
    print(f"  第一表⑦ 控除税額の計（④+⑤+⑥）                  ：{control_7:,} 円")
    print(f"  第一表⑧ 控除不足還付税額（⑦−②−③）              ：{control_8:,} 円")

    # ※差引税額の計算は「②（基礎）−⑦（控除税額計）」でOK
    national_net_raw = r["base_national_tax"] - control_7
    national_net = (national_net_raw // 100) * 100  # 100円未満切捨て（要検討）

    print(
        f"  第一表⑨ 差引税額 (②−⑦)【100円未満切捨て】      ：{national_net:,} 円"
        f"（参考：切捨て前 {national_net_raw:,} 円）"
    )
    print(
        f"  第一表⑩ 中間納付税額（国税）                     ：{r['interim_national']:,} 円"
    )

    national_payable_raw = national_net - r["interim_national"]
    national_payable = (national_payable_raw // 100) * 100  # 100円未満切捨て

    print(
        f"  第一表⑪ 納付税額（国税）【100円未満切捨て】       ：{national_payable:,} 円"
        f"（参考：切捨て前 {national_payable_raw:,} 円）"
    )
    print(
        "  第一表⑫ 中間納付還付税額                         ：0 円（今回は未計算/必要なら分岐）"
    )
    print(
        f"  第一表⑮ この課税期間の課税売上高（税抜）           ：{r['taxable_sales_excl']:,} 円"
    )
    print(
        f"  第一表⑯ 基準期間の課税売上高（税抜）               ：{r['base_period_sales_excl']:,} 円"
    )

    # 第一表（地方消費税）
    print("\n■ 申告書 第一表（地方消費税）に記入する値")
    print(
        f"  第一表⑱ 地方課税標準となる消費税額（基礎：差引税額）       ：{r['local_tax_base']:,} 円"
    )
    print(
        f"  第一表⑳ 譲渡割額（納税額）【100円未満切捨て】          ：{r['local_tax']:,} 円"
        f"（参考：切捨て前 {r['local_tax_raw']:,} 円）"
    )
    print(
        f"  第一表㉑ 中間納付譲渡割額（地方）                            ：{r['interim_local']:,} 円"
    )
    print(
        f"  第一表㉒ 納付譲渡割額（地方）【100円未満切捨て】              ：{r['local_payable']:,} 円"
        f"（参考：切捨て前 {r['local_payable_raw']:,} 円）"
    )

    # 合計
    print("\n■ 消費税及び地方消費税の合計（納付）税額")
    print(
        f"  第一表㉖ 合計納付税額（国税＋地方）                           ：{r['total_payable']:,} 円"
    )

    # 第二表（内訳）
    print("\n■ 申告書 第二表（税率別内訳：10%のみ想定）に記入する値")
    print(
        f"  第二表① 課税標準額                              ：{r['taxable_base']:,} 円"
    )
    print("  【7.8%適用分（標準税率10%の国税分）】")
    print(
        f"  第二表⑥  課税資産の譲渡等の対価の額の合計額（7.8%適用分: 税抜）          ：{r['taxable_sales_excl']:,} 円"
    )
    print(
        f"  第二表⑦  ②-⑥の合計                                    ：{r['taxable_sales_excl']:,} 円"
    )
    print(
        f"  第二表⑪  消費税額                                       ：{r['national_tax_raw']:,} 円"
    )
    print(
        f"  第二表⑯  ⑪の内訳（7.8%適用分）                          ：{r['national_tax_raw']:,} 円"
    )
    print(
        f"  第二表⑳  地方消費税の課税標準となる消費税額（㉑-㉓の合計）    ：{r['local_tax_base']:,} 円"
    )
    print(
        f"  第二表㉓  地方消費税の課税標準となる消費税額（7.8%適用分）    ：{r['local_tax_base']:,} 円"
    )
    print("=" * 72)


def main():
    print(
        f"=== 消費税申告（簡易課税）{YEAR}年分（令和{REIWA}年分）/ 第5種(50%) / 10%のみ ==="
    )
    print(
        "入力：所得税の確定申告書 第一表「収入金額等（事業）」の金額（税込）を想定します。"
    )
    print("（前提：非課税・不課税・売上以外収入・8%売上・調整事項なし）\n")

    gross = ask_int_yen("今季の事業収入（税込）を入力してください: ")

    base_sales = ask_int_yen(
        "基準期間（2期前）の課税売上高（税抜）を入力してください: "
    )

    interim_nat = ask_int_yen(
        "中間納付（国税）があれば入力（なければ空欄/0）: ", default=0, allow_blank=True
    )
    interim_loc = ask_int_yen(
        "中間納付（地方）があれば入力（なければ空欄/0）: ", default=0, allow_blank=True
    )

    r = calc_all(gross, base_sales, interim_nat, interim_loc)
    print_forms(r)


if __name__ == "__main__":
    main()
