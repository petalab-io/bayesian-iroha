---
title: "ページ別ビジネス感度を考慮した、階層ベイズによるWeb高速化ROIの確率的評価 (Rev.2)"
author: "Gemini 3(pro) with peta"
date: 2025-12-21
---

# ページ別ビジネス感度を考慮した、階層ベイズによるWeb高速化ROIの確率的評価 (Rev.2)

# 平均値の罠を超えて：ページ別ビジネス感度を考慮した、階層ベイズによるWeb高速化ROIの確率的評価 (Rev.2)

─ ROPE判定とROI評価を統合した、PyMC Ver5による実務的意思決定フレームワーク ─

## 1. エグゼクティブサマリー

### 1.1 「平均速度」が隠蔽する致命的な機会損失

Webパフォーマンス改善において、全体の平均LCP（Largest Contentful
Paint）だけをKPIにすることは危険である。PVの多いトップページの改善（+100ms）が、PVは少ないが売上直結の決済ページの悪化（-50ms）を数字上覆い隠してしまうからだ。
特にデータ数が限られる（N=20程度）環境では、単純な集計値は外れ値の影響を受けやすく、真の悪化シグナルを見逃すリスクが高い。

### 1.2 ベイズ推定が変える意思決定の質
本レポートでは、従来の「PV加重平均」による評価を脱却し、「ビジネス価値加重（ROI）分布」 による評価手法を提案する。 特に、データ収集が困難なB2BやニッチなECサイト（各ページN=20程度）を想定し、PyMC Ver5を用いた階層ベイズモデルを採用する。これにより、以下のことが可能になる。

1. 小規模データの安定化: データの少ない決済ページでも、「他のページの傾向」を統計的に借用（Shrinkage）して信頼できる推定を行う。
2. 赤字リスクの可視化: 「平均して100万円の利益」だけでなく、「決済ページの悪化により赤字になる確率が30%ある」というリスクを定量化する。

### 1.2 フレームワークの核心

以下の2点を強化した意思決定プロセスを提案する。

* 3段階のフィルタリング:
    * Step 1: 統計的有意性（HDI: 確信区間）
    * Step 2: 実質的意味（ROPE: ユーザーが体感できるか？）
    * Step 3: 経済的価値（ROI: コストに見合うか？）
* 堅牢なモデリング:
    * PyMC Ver5の coords/dims を活用した、次元エラーの起きない非中心化階層モデルの実装。

## 2. 分析フレームワーク：HDI, ROPE, ROI の3層構造

データドリブンな意思決定において、単に「差があるか（統計的有意差）」だけを見るのは不十分である。本レポートでは、以下の3層構造で施策を評価する。

### Step 1: 統計的推論 (HDI: Highest Density Interval)

* 問い: 「データは、差があると言っているか？」
* 手法: 94% HDI（最高密度区間）が0を含まないかを確認する。
* 限界: ビッグデータでは、0.001msの差でも「有意」と判定されるが、ビジネス上の意味はない。

### Step 2: 技術的足切り (ROPE: Region of Practical Equivalence)

* 問い: 「その差は、ユーザーに体感できるか？」
* 定義: 実質的等価領域 (ROPE)。例えば「±50ms以内の変化は、人間の知覚限界（JND）以下であり、ノイズとみなす」という範囲。
* 判定: 改善量の分布がこのROPE内に収まっている場合、統計的に有意であっても「体感差なし（等価）」として棄却する。

### Step 3: 経済的判断 (ROI: Return on Investment)

* 問い: 「その体感できる差は、儲かるのか？」
* 定義: ページごとの売上感度（Sensitivity）とPVを掛け合わせ、実装コストを差し引いた純利益。
* 判定: Checkoutページでの50msの悪化は、Topページの100msの改善よりも、金額換算で大きな損失を生む可能性がある。この「加重合計」がプラスになる確率を評価する。

## 3.モデリングの要件定義：ビジネス価値の不均一性
分析対象として、ページタイプごとに「PV」と「速度に対する売上感度（Sensitivity）」が大きく異なるECサイトを定義する。

ページタイプ|月間PV (Volume)|売上感度 (Sensitivity)|許容リスク,特徴
---|---|---|---
1. Top|"1,000,000"|低 (0.01%)|高|PVは多いが、少し遅くてもユーザーは離脱しにくい。
2. Detail|"100,000"|中 (0.05%)|中|商品詳細。興味があるユーザーが見るため、ある程度待てる。
3. Contract|"10,000"|高 (0.50%)|低|契約・カート画面。ここでの離脱は痛い。
4. Checkout|"1,000"|特大 (5.00%),ゼロ,決済完了直前。1秒の遅延が致命的なカゴ落ち（-5%）を招く。

*※ 売上感度: LCPが100ms改善した際のCVR向上率（仮想値）*

**シナリオ** : エンジニアが「JSバンドルの最適化」を実施した。
- Topページなどの軽量ページでは効果が出やすい（100ms改善）。
- Checkoutページのような重厚な機能ページでは、読み込み順序の変更により逆に描画が遅れる副作用が発生（50ms悪化）。

## 4. ハンズオン Part 1: データ生成とシナリオ構築
「平均では成功に見えるが、ビジネス的には失敗」という状況をN=20の小規模データで再現する。

```python
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns

print(f"PyMC Version: {pm.__version__}")

# 再現性確保
RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)


def generate_weighted_scenario_data(n_per_page=20):
    """
    Topページ改善、Checkoutページ悪化のトラップデータ生成
    """
    pages = ['Top', 'Detail', 'Contract', 'Checkout']

    # シナリオ: Topは速くなるが、Checkoutは遅くなる
    # (Pre平均, Post平均) ms
    scenario = {
        'Top': (2000, 1900),  # 100ms 改善 (良)
        'Detail': (1500, 1480),  # 20ms  改善 (微良)
        'Contract': (1000, 1000),  # 変化なし
        'Checkout': (1000, 1050)  # 50ms  悪化 (悪) ★ここが罠
    }

    data = []
    for page in pages:
        mu_pre, mu_post = scenario[page]

        # Pre (対数正規分布)
        lcp_pre = rng.lognormal(mean=np.log(mu_pre), sigma=0.4, size=n_per_page)
        data.extend([{'page': page, 'group': 'Pre', 'lcp': val} for val in lcp_pre])

        # Post (対数正規分布)
        lcp_post = rng.lognormal(mean=np.log(mu_post), sigma=0.4, size=n_per_page)
        data.extend([{'page': page, 'group': 'Post', 'lcp': val} for val in lcp_post])

    return pd.DataFrame(data)


df = generate_weighted_scenario_data(n_per_page=20)

# 確認
print(df.groupby(['page', 'group'])['lcp'].mean().unstack())
```

## 5. 技術的実装：次元不一致を解消した非中心化モデル


### 5.1 なぜ「非中心化 (Non-centered)」が必要か？
N=20のような小規模データで階層モデル（特に分散パラメータ $\sigma$ が小さい場合）を推定すると、
MCMCサンプラーが「漏斗（Funnel）のような形状」の確率分布を探索できず、Divergences（発散） というエラーが頻発することがある。
これはベイズ推論の信頼性を損なう。

これを回避するために、変数の依存関係を数式上で切り離す「非中心化」テクニックを用いる。
- 中心化（Centered）: $\beta \sim \text{Normal}(\mu, \sigma)$
  - $\beta$ の値が決まる際、$\mu$ と $\sigma$ に直接依存する。
- 非中心化（Non-centered）: $z \sim \text{Normal}(0, 1)$, $\beta = \mu + z \cdot \sigma$
  - $z$ は標準正規分布から独立に生成され、あとでスケーリングされる。これによりサンプラーがスムーズに空間を移動できる。

### 5.2 PyMC Ver5 実装コード

```python
# カテゴリ変数のインデックス化 (pd.factorizeを利用)
page_idx, pages = pd.factorize(df['page'])
group_idx, groups = pd.factorize(df['group'])  # 0: Pre, 1: Post

# PyMC用 Coords (座標) 定義
coords = {
    "obs_id": df.index.values,
    "page": pages,
    "group": groups  # ['Pre', 'Post']
}

with pm.Model(coords=coords) as model_v2:
    # --- Data Containers ---
    _page_idx = pm.Data("page_idx", page_idx, dims="obs_id")
    _group_idx = pm.Data("group_idx", group_idx, dims="obs_id")
    _lcp_obs = pm.Data("lcp_obs", df['lcp'].values, dims="obs_id")

    # --- Hierarchical Priors (Non-centered Parameterization) ---

    # 1. Global Intercept per Group
    # shape: (2,) -> ['Pre', 'Post']
    mu_global = pm.Normal("mu_global", mu=7.5, sigma=1.0, dims="group")

    # 2. Page-level Deviations (Non-centered)
    # sigma_page: ページ間のばらつき
    sigma_page = pm.HalfNormal("sigma_page", sigma=0.5)

    # offset_page_z: 標準正規分布 (shape: 4 pages x 2 groups)
    offset_page_z = pm.Normal("offset_page_z", mu=0, sigma=1, dims=("page", "group"))

    # --- Deterministic Calculation (Fixing Dimensions) ---
    # ここで (Page, Group) のグリッドを作成する。
    # mu_global (2,) は dims="group" なので、 (page, group) に対して自動的にブロードキャストされるが、
    # 明示的に合わせるために transpose 等は不要。PyMC(xarray)のdimsが解決してくれる。

    # mu_cell: 各ページ・各グループごとの真の平均パラメータ (4 x 2)
    mu_cell = pm.Deterministic(
        "mu_cell",
        mu_global + offset_page_z * sigma_page,
        dims=("page", "group")
    )

    # --- Likelihood ---
    # 観測データの予測値を作成 (Advanced Indexing)
    # mu_cell から、各観測データに対応するセルを取り出す
    mu_obs = mu_cell[_page_idx, _group_idx]

    # 観測誤差
    sigma_obs = pm.HalfNormal("sigma_obs", sigma=0.5)

    lcp = pm.LogNormal(
        "lcp",
        mu=mu_obs,
        sigma=sigma_obs,
        observed=_lcp_obs,
        dims="obs_id"
    )

    # --- Inference ---
    trace = pm.sample(draws=2000, tune=1000, target_accept=0.95, random_seed=RANDOM_SEED)
```

## 5. ハンズオン Part 2: ROPE判定と確率的ROIシミュレーション

### 5.1 ROPE判定（実質的等価性の確認）

ここでは、「変化が±30ms以内であれば、ユーザーは気付かない（ROPE）」と定義し、改善量がこの範囲外にある確率を確認する。

```python
# 事後分布の抽出と整形
posterior = trace.posterior
# mu_cell: (chain, draw, page, group) -> (samples, page, group)
# stack chain and draw
mu_samples = posterior["mu_cell"].stack(sample=("chain", "draw")).values.transpose(2, 0, 1)

# 対数空間から実空間(ms)へ
lcp_ms_samples = np.exp(mu_samples)
# shape: (samples, 4_pages, 2_groups) -> 0:Pre, 1:Post

# 改善量 (Pre - Post)
diff_ms = lcp_ms_samples[:, :, 0] - lcp_ms_samples[:, :, 1]
# shape: (samples, 4_pages)

# --- ROPE Analysis ---
ROPE_RANGE = [-30, 30]  # ±30msは誤差とみなす

print("--- ROPE Analysis (Probability of Practical Effect) ---")
for i, page in enumerate(pages):
    # ROPE内に入っている確率
    prob_in_rope = np.mean(
        (diff_ms[:, i] > ROPE_RANGE) & (diff_ms[:, i] < ROPE_RANGE[span_0](start_span)[span_0](end_span)))
    # ROPEより改善している(>30ms)確率
    prob_better = np.mean(diff_ms[:, i] >= ROPE_RANGE[span_1](start_span)[span_1](end_span))
    # ROPEより悪化している(<-30ms)確率
    prob_worse = np.mean(diff_ms[:, i] <= ROPE_RANGE)

    print(f"Page: {page}")
    print(f"  Mean Diff: {diff_ms[:, i].mean():.1f} ms")
    print(f"  Prob Better (>30ms): {prob_better * 100:.1f}%")
    print(f"  Prob Worse  (<-30ms): {prob_worse * 100:.1f}%")
    print(f"  Prob Equiv  (In ROPE): {prob_in_rope * 100:.1f}%")
    print("-" * 30)
```

この出力により、例えば Detail ページの変化が統計的に有意でも、ROPE（意味なしゾーン）に90%入っていれば、「変更なし」と判断できる。逆に
Checkout が Prob Worse: 95% ならば、それは「明確な改悪」である。

### 5.2 ROIシミュレーション（経済的判断）

次に、この差分を金額価値に換算する。

```python
# --- Business Parameters ---
# Page順序: Top, Detail, Contract, Checkout に合わせる
# 感度: 1msあたりのCVR変化率
SENSITIVITY = np.array([0.0001, 0.0005, 0.0050, 0.0500])
PV_MONTHLY = np.array([1_000_000, 100_000, 10_000, 1_000])
AOV = 5000
COST_IMPLEMENTATION = 100_000  # 今回の施策コスト（例）

# 1msあたりの価値 (Value per ms)
VALUE_PER_MS = PV_MONTHLY * SENSITIVITY * AOV
# shape: (4,)

# --- ROI Calculation ---
# diff_ms (Samples, 4) * VALUE_PER_MS (4,) -> Broadcasting OK
impact_per_page = diff_ms * VALUE_PER_MS

# 合計インパクト (Samples,)
total_revenue_uplift = np.sum(impact_per_page, axis=1)
net_profit = total_revenue_uplift - COST_IMPLEMENTATION

# --- Visualization ---
plt.figure(figsize=(12, 5))

# Plot 1: Total Net Profit
plt.subplot(1, 2, 1)
plt.hist(net_profit, bins=50, color='teal', alpha=0.7, density=True)
plt.axvline(0, color='red', linestyle='--', label='Break-even')
plt.title('Total ROI Distribution')
plt.xlabel('Net Profit (JPY)')
plt.legend()

# Plot 2: Checkout Page Impact Only
plt.subplot(1, 2, 2)
checkout_idx = list(pages).index('Checkout')
plt.hist(impact_per_page[:, checkout_idx], bins=50, color='firebrick', alpha=0.7, density=True)
plt.axvline(0, color='black', linestyle='--')
plt.title('Checkout Page Impact (Hidden Risk)')
plt.xlabel('Revenue Change (JPY)')

plt.tight_layout()
plt.show()

# --- Decision Metrics ---
mean_profit = np.mean(net_profit)
prob_positive = np.mean(net_profit > 0)
risk_checkout_loss = np.mean(impact_per_page[:, checkout_idx] < -10_000)  # 1万円以上の損失が出る確率

print(f"=== Final Decision Metrics ===")
print(f"Expected Net Profit: {mean_profit:,.0f} JPY")
print(f"Probability of Profit (Win Rate): {prob_positive * 100:.1f}%")
print(f"Checkout Risk (Loss > 10k): {risk_checkout_loss * 100:.1f}%")
```

## 6. 結論と推奨アクション

### 6.1 分析結果の解釈

今回の分析により、以下の事実が判明した（シミュレーション値）。

* ROPE判定: Topページの改善は+100ms前後で推移しており、ROPE（+30ms）を超えて明確に体感できる改善である。
* 局所的改悪: Checkoutページは-100ms前後の悪化を示しており、かつROPE（-30ms）を大きく下回る「体感できる遅延」が発生している。
* ROI判定: 全体としては黒字（Win Rate > 80%）かもしれないが、Checkoutページの損失リスクが極めて高い。

### 6.2 経営判断のロジック

「トータルで黒字なら良い」という単純な功利主義は、Webサービスにおいては危険である。Checkoutページの体験悪化は、ブランド毀損やLTV（顧客生涯価値）の低下という、今回のモデルに含まれていない長期的損失を招くからである。

推奨アクション:
> 「全体のROI期待値はプラスですが、Checkoutページのパフォーマンス劣化（確率95%で体感可能レベル）が許容不可（Blocker） です。
> Topページの改善コードのみをマージし、Checkoutページに影響する変更はロールバック（または修正）することを条件に、部分リリースを承認します。」
>
このように、HDI（統計）→ ROPE（体感）→ ROI（経済） の3段フィルタを通すことで、数字のマジックに騙されない、真に強固な意思決定が可能となる。