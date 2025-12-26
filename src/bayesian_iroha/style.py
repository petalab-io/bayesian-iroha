"""
src/bayesian_iroha/style.py

プロジェクト共通の可視化スタイルとカラーパレットを定義するモジュール。
"""
import matplotlib.pyplot as plt
import seaborn as sns
from cycler import cycler

# ==========================================
# 🎨 Brand Color Definitions
# ==========================================
# 意図: 意味論的な変数名で定義し、HEXコードの変更に強くする
COLOR_PURPLE = "#9B5DE5"  # Main: 事後分布・HDI
COLOR_YELLOW = "#F9C74F"  # Warning: ROPE領域
COLOR_GREEN = "#06D6A0"  # Positive: 改善判定
COLOR_RED = "#EF476F"  # Negative: 悪化判定
COLOR_GRAY = "#8D99AE"  # Neutral: 等価判定

# パレットとして外部から参照できるようにする
PALETTE = [COLOR_PURPLE, COLOR_YELLOW, COLOR_GREEN, COLOR_RED, COLOR_GRAY]


def apply_style():
    """
    Matplotlib と Seaborn のグローバルスタイルを適用する。
    Notebook の冒頭でこの関数を呼び出すことで、デザインを統一する。
    """
    # 1. Matplotlib Defaults
    plt.rcParams['axes.prop_cycle'] = cycler(color=PALETTE)
    plt.rcParams['figure.figsize'] = (11, 7)  # デフォルトサイズも統一推奨
    # plt.rcParams['font.family'] = 'IPAexGothic'  # 日本語フォント設定（環境に合わせて調整）

    # 2. Seaborn Style
    sns.set_style("whitegrid")
    sns.set_palette(PALETTE)

    # 3. 適用確認ログ
    print("Bayesian Iroha Style Loaded: Purple/Yellow/Green/Red/Gray")