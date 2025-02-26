# Whisper Auto Transcriber

Copyright (c) 2025 led-mirage

## 概要

**Whisper Auto Transcriber**は、音声または動画ファイルからテキストを抽出する便利なツールです。このアプリケーションは、OpenAIもしくはAzure OpenAI ServiceのWhisperモデル（API）を使用して高精度の音声認識を行い、結果をテキストファイルとして出力します。

## 主な機能

- **マルチクラウド対応**: OpenAI と Azure OpenAI Service に対応しています。
- **対応ファイル形式**: mp3, m4a, mp4, avi, mov, mkv
- **動画自動変換**: 動画ファイルはffmpegを使用して自動的に音声ファイルに変換されます。
- **音声の自動分割**: Whisper APIの制限に対応するため、FFmpegで音声ファイルを5分ごとに分割します。
- **音声認識**: Whisper APIで分割された音声ファイルをテキストに変換します。
- **出力管理**: 変換されたテキストは1つのファイルに統合され、`output`ディレクトリに保存されます。

## 主な用途

会議の録音など長時間の音声データをテキストとして保存したいときに便利です。出力されたテキストをAIに入力し要約させることで、簡単に議事録を作成できます。

## 事前準備

- Python
    - Python 3.8 以上が必要です。仮想環境（venv）の利用を推奨します。
    - ※このソフトウェアは Python 3.12.0 で動作確認済みです。

- ffmpeg
    - [ffmpegのサイト](https://www.ffmpeg.org/)からダウンロードし、パスを通してください。
    - ffmpeg version n7.1で動作確認済みです。

- OpenAIのAPIキー
    - [OpenAI Platform](https://platform.openai.com/)に登録し、APIキーを発行してください。

- または、Azure OpenAI Serviceの設定
    - Azure OpenAI Serviceを利用する場合は、APIキーとエンドポイントを取得してください。くわえて、**Whisperモデル**をAzure上でデプロイして使用できる状態にしてください。

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
## 設定

- OpenAIを使用する場合は、環境変数`OPENAI_API_KEY`にAPIキーを設定してください。
- Azure OpenAI Serviceを使用する場合は、`settings.ini`のAPI typeを`azure`にし、モデル、APIキー、エンドポイントの設定を行ってください。
- `settings.ini`ではその他詳細な設定が可能です。詳しくは以下の`設定ファイル（settings.ini）`の項目を参照してください。

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

## 設定ファイル (`settings.ini`)

アプリケーションを実行する前に、`settings.ini`ファイルを正しく設定してください。このファイルでは、APIタイプやモデル名、APIキーの設定を行います。

### APIセクション

- **type**: 使用するAPIの種類を指定します。`openai` もしくは `azure` を設定してください。デフォルトは`openai`です。

### OpenAIセクション

- **model_name**: 使用するOpenAIモデルを指定します。デフォルトは `whisper-1` です。
- **api_key**: OpenAIのAPIキーを直接指定する場合に使用します。環境変数を使用する場合は空にしてください。
- **api_key_env**: APIキーを指定する際の環境変数名を入力してください。デフォルトは `OPENAI_API_KEY` ですが、ユーザーが自由に環境変数名を設定できます。

### Azureセクション

- **model_name**: 使用するAzureモデルを指定します。デフォルトは `whisper` です。
- **api_key**: AzureのAPIキーを直接指定する場合に使用します。環境変数を使用する場合は空にしてください。
- **endpoint**: エンドポイントを直接指定する場合に使用します。環境変数を使用する場合は空にしてください。
- **api_key_env**: APIキーを指定する際の環境変数名を入力してください。デフォルトは `AZURE_OPENAI_API_KEY` ですが、ユーザーが自由に設定できます。
- **endpoint_env**: エンドポイントを指定する際の環境変数名を入力してください。デフォルトは `AZURE_OPENAI_ENDPOINT` ですが、ユーザーが自由に設定できます。

### Generalセクション

- **audio_segment_time**: 音声を分割する単位を秒単位で指定します。デフォルトは300秒です。

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

### 2.0.0 (2025/02/27)

- HotFix: 動画を指定した場合、テキスト化が途中で停止する問題を修正しました。
- Azure OpenAI Serviceに対応しました。
- 設定を`settings.ini`ファイルに移動しました。

### 1.0.0 (2025/02/26)

- ファーストリリース
