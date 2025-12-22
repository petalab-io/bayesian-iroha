# bayesian-iroha
小規模データ×階層ベイズでビジネスの勝率を導く「意思決定のいろは」。PyMC v5を用い、単なる有意差検定を超えたROPE/ROI分析によるリスク可視化フレームワークを実装・蓄積するナレッジベース。

---
このレポジトリは、**「小規模データ（Small Data）」** におけるビジネス意思決定を、**「階層ベイズモデル」** を用いて科学的に行うためのナレッジベース兼ハンズオンログです。

平均値による単純な比較ではなく、**ROPE（実質的な差）** や **ROI（投資対効果）** の確率分布を可視化し、リスクを考慮した経営判断を行うためのフレームワークを蓄積しています。

## 🧠 コンセプト

* **Small Data is Beautiful**: N=20程度のデータでも、階層モデルによる「情報の借用」で最大限の推論を行う。
* **Probability over P-value**: 有意差検定ではなく、事後分布を用いた「勝率」と「期待損失」で判断する。
* **Business First**: 技術的な指標を、最終的に「金額（円）」や「アクション」に翻訳する。

## 📂 ディレクトリ構成

Quarto を用いてドキュメントサイトとしてビルド可能な構成にしています。パッケージ管理には **Poetry** を使用します。

```text
bayesian-iroha/
├── _quarto.yml             # サイト構成設定
├── index.qmd               # サイトのトップページ
├── pyproject.toml          # ★Poetry設定ファイル
├── poetry.lock             # ★依存関係ロックファイル
│
├── src/                    # 共通分析ライブラリ
│   ├── models.py           # PyMCモデル定義（非中心化実装など）
│   └── viz.py              # ROPE/ROI可視化関数
│
└── notebooks/              # 学習テーマごとのコンテンツ
    ├── 01_web_performance/
    │   ├── README.md       # [理論] DeepResearchによるレポート
    │   └── analysis.ipynb  # [実践] PyMCによるハンズオンコード
    │
    └── ...
```

## 🛠 環境構築

WSL (Ubuntu) 上の Pyenv + Poetry 環境で構築します。

### 1. Python環境の準備 (Terminal)

プロジェクトルートで以下のコマンドを実行し、環境をセットアップしてください。

```bash
# 1. PyenvでPythonバージョンを指定 (PyMC v5推奨環境)
pyenv local 3.11.9

# 2. Poetry環境をPyenvのPythonに紐づけ
poetry env use $(pyenv which python)

# 3. 依存ライブラリのインストール
# (初回作成時)
poetry init
poetry add pymc arviz pandas numpy seaborn matplotlib jupyter ipykernel
# (2回目以降/clone時)
poetry install
```

### 2. DataSpell (IDE) の設定

JetBrains DataSpell で Poetry 環境を認識させます。

1.  DataSpell でプロジェクトフォルダを開く。
2.  右下のインタープリタ表示（または `File` > `Settings` > `Project: bayesian-iroha` > `Python Interpreter`）をクリック。
3.  `Add New Interpreter` > `On WSL...` を選択。
4.  `Poetry Environment` を選択。
    * **Base interpreter**: Pyenv で指定したパス（自動検出されるはずです）。
    * **Poetry executable**: WSL上のパス（例: `/home/user/.local/bin/poetry`）。
5.  `OK` を押して環境を作成・適用します。

### 3. Quarto (ドキュメント生成ツール)
[Quarto公式サイト](https://quarto.org/docs/get-started/) からCLIをインストールしてください（WSL上であれば `.deb` パッケージ推奨）。

```bash
# Ubuntu/Debian (WSL)
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.3.450/quarto-1.3.450-linux-amd64.deb
sudo dpkg -i quarto-1.3.450-linux-amd64.deb
```

## 🚀 学習・更新ワークフロー

新しいビジネス課題（ユースケース）を追加する際の手順です。

### Step 1. Gem (Bayesian Strategy Partner) に相談
カスタムGemに課題を投げ、レポート構成とコードを出力させます。

> **プロンプト例:**
> 「小売店における『価格弾力性』の検証をしたいです。データは各店舗2週間分しかありません。DeepResearchへの依頼用プロンプトと、PyMCの実装方針を提示してください。」

### Step 2. DeepResearch でレポート作成
Gem が出力したプロンプトを DeepResearch に入力し、理論的背景とビジネスロジックを含むレポートを生成させます。

### Step 3. コンテンツの配置
1.  `notebooks/` 配下に連番でディレクトリを作成します（例: `03_hr_analytics`）。
2.  DeepResearch のレポートを **`README.md`** として保存します。
    * **重要**: 先頭にQuarto用のYAMLヘッダー（以下参照）を追加してください。
    
    ```yaml
    ---
    title: "レポートのタイトル"
    author: "Author Name"
    date: "2025-01-01"
    ---
    ```

3.  Gem/DeepResearch のコードを元に **`analysis.ipynb`** を作成し、実行します。
    * DataSpell 上でカーネルとして **「Poetry (bayesian-iroha)」** が選択されていることを確認してください。
    * 必要に応じて `src` の共通関数を import してコードをスリム化してください。

### Step 4. サイトへの追加
ルート直下にある `_quarto.yml` の `sidebar` セクションに、新しいファイルへのパスを追加します。

```yaml
      - section: "HR Analytics"
        contents:
          - text: "理論: 採用媒体のABテスト"
            file: notebooks/03_hr_analytics/README.md
          - text: "実践: 階層ベータモデル"
            file: notebooks/03_hr_analytics/analysis.ipynb
```

### Step 5. レンダリング
以下のコマンドでローカルプレビューを行い、問題なければコミットします。

```bash
quarto preview
```

## 📚 共通ライブラリ (`src/`) について

* **`models.py`**: 小規模データで頻発する Divergences を防ぐための「非中心化（Non-centered Parameterization）」を実装したモデルファクトリー。
* **`viz.py`**: ROPE（実質的等価領域）や ROI分布を描画する定型プロット関数。

## 🤖 Gem 設定情報 (Reference)

このレポジトリのコンテンツ生成に使用しているカスタムGemの設定概要です。

* **Name**: Bayesian Strategy Partner
* **Focus**: SMB市場, PyMC v5, Non-centered param, ROPE/ROI Analysis
* **Knowledge**: `pymc_v5_best_practices.txt`, `bayesian_business_glossary.txt` を参照済み。

---
Author: petaLab
