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
# 1. PyenvでPythonバージョンを指定
pyenv local 3.12.8

# 2. Poetry環境をPyenvのPythonに紐づけ
poetry env use $(pyenv which python)

# 3. 依存ライブラリのインストール
poetry install
```

### 2. Quarto (ドキュメント生成ツール)

WSL上であれば `.deb` パッケージを使用してインストールします。

```bash
# Ubuntu/Debian (WSL)
wget [https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.40/quarto-1.6.40-linux-amd64.deb](https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.40/quarto-1.6.40-linux-amd64.deb)
sudo dpkg -i quarto-1.6.40-linux-amd64.deb
rm quarto-1.6.40-linux-amd64.deb
```

## 🚀 学習・更新ワークフロー

### Step 1. Gem に相談
カスタムGemに課題を投げ、レポート構成とコードを出力させます。

### Step 2. DeepResearch でレポート作成
理論的背景とビジネスロジックを含むレポートを生成させます。

### Step 3. コンテンツの配置
`notebooks/` 配下にディレクトリを作成し、`README.md` と `analysis.ipynb` を配置します。

### Step 4. サイトへの追加
`_quarto.yml` の `sidebar` セクションに、新しいファイルへのパスを追加します。

### Step 5. レンダリングと公開

以下の手順でサイトを最新の状態に更新します。

```bash
# 1. キャッシュと生成物のクリーンアップ（反映されない場合）
rm -rf .quarto _site

# 2. ローカルでのレンダリング確認
poetry run quarto render

# 3. ソースコードの保存
git add .
git commit -m "feat: new notebook added"
git push origin main

# 4. サイトの公開（GitHub Pagesなど）
poetry run quarto publish gh-pages
```

## 📚 共通ライブラリ (`src/`) について

* **`models.py`**: 小規模データで頻発する Divergences を防ぐための「非中心化（Non-centered Parameterization）」を実装。
* **`viz.py`**: ROPE（実質的等価領域）や ROI分布を描画する関数。

---
Author: petaLab