# Whisper Auto Transcriber

Copyright (c) 2025 led-mirage

**Whisper Auto Transcriber**は、音声または動画ファイルからテキストを抽出する便利なツールです。このアプリケーションは、OpenAIのWhisperモデル（API）を使用して高精度の音声認識を行い、結果をテキストファイルとして出力します。

## 主な機能

- **対応ファイル形式**: mp3, m4a, mp4, avi, mov, mkv
- **動画自動変換**: 動画ファイルはffmpegを使用して自動的に音声ファイルに変換されます。
- **音声の自動分割**: Whisper APIの制限に対応するため、FFmpegで音声ファイルを5分ごとに分割します。
- **音声認識**: Whisper APIで分割された音声ファイルをテキストに変換します。
- **出力管理**: 変換されたテキストは1つのファイルに統合され、`output`ディレクトリに保存されます。

## 主な用途

会議の録音など長時間の音声データをテキストとして保存したいときに便利です。出力されたテキストをAIに入力し要約させることで、簡単に議事録を作成できます。

## 必要なもの

- Python
    - Python 3.8 以上が必要です。仮想環境（venv）の利用を推奨します。
    - ※このソフトウェアは Python 3.12.0 で動作確認済みです。

- OpenAIのAPIキー
    - [OpenAI Platform](https://platform.openai.com/)に登録し、APIキーを発行してください。
    - 取得したAPIキーは、OSの環境変数OPENAI_API_KEYに設定します。

- ffmpeg
    - [ffmpegのサイト](https://www.ffmpeg.org/)からダウンロードし、パスを通してください。
    - ffmpeg version n7.1で動作確認済みです。

## インストール

1. プロジェクト用ディレクトリを作成し、移動します。
2. GitHubからソースを取得します：
    ```
    git clone https://github.com/led-mirage/whisper-auto-transcriber.git
    ```
3. 仮想環境を作成し、アクティベートします（推奨）：
    ```
    python -m venv venv
    venv\Scripts\activate   # macOS/Linuxの場合は source venv/bin/activate
    ```
4. 必要なライブラリの取得します：
    ```
    pip install -r requirements.txt
    ```

## 実行方法

1. 起動します：
    ```
    python src/main.py
    ```
2. テキスト化する音声または動画ファイルのパスを入力してEnterキーを押します：
    ```
    変換元のファイルのパスを入力してください: c:\temp\test.mp3
    ```
3. 出力：  
    結果は`output`ディレクトリ内にテキストファイルとして出力されます。  
    ファイル名は`[元のファイル名（拡張子を除く）].txt`になります。

## Whisper APIの利用料金

Whisperの利用料金は、変換元の音声の長さに基づいており、１分あたり`$0.006`※です。例えば１時間の音声または動画ファイルをテキスト化すると、$0.36かかります。

※価格の詳細は[OpenAIの料金ページ](https://openai.com/ja-JP/api/pricing/)で確認してください。

## 使用しているライブラリ

### 🔖 openai 1.63.2
ホームページ： https://github.com/openai/openai-python
ライセンス： Apache License 2.0

## ライセンス

© 2025 led-mirage

本アプリケーションは MITライセンス の下で公開されています。詳細については、プロジェクトに含まれる LICENSE ファイルを参照してください。

## バージョン履歴

### 1.0.0 (2025/02/26)

- ファーストリリース
