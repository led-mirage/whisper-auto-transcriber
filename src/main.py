# Whisper Auto Transcriber
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import openai

from settings import Settings


APP_NAME = "Whisper Auto Transcriber"
APP_VERSION = "3.1.1"
EXE_NAME = "audioscribe.exe"
COPYRIGHT = "© 2025 led-mirage"

SETTINGS_FILE = "settings.ini"
AUDIO_EXTENSIONS = [".mp3", ".m4a"]
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"]
WORK_DIR = "./workdir"
OUTPUT_DIR = "./output"


def display_app_title():
    """
    アプリケーションのタイトルを表示します。

    戻り値:
        None
    """
    print("-" * 60)
    if getattr(sys, "frozen", False):
        print(f" {APP_NAME} ({EXE_NAME}) v{APP_VERSION}")
    else:
        print(f" {APP_NAME} v{APP_VERSION}")
    print("")
    print(f" {COPYRIGHT}")
    print("-" * 60)
    print("")


def get_ffmpeg_path():
    """
    FFmpegのパスを取得します。

    戻り値:
        str: FFmpegのパス。FFmpegが見つからない場合はNoneを返します。
    """
    # バンドルされたFFmpegのパスを取得
    if getattr(sys, "frozen", False):
        # PyInstallerなどでパッケージ化された場合
        application_path = os.path.dirname(sys.executable)
    else:
        # 通常のPythonスクリプトとして実行される場合
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    if sys.platform.startswith("win"):
        ffmpeg_path = os.path.join(application_path, "ffmpeg", "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(application_path, "ffmpeg", "ffmpeg")

    if os.path.exists(ffmpeg_path):
        # バンドルされたFFmpegが見つかった場合は、そのパスを返す
        return ffmpeg_path
    else:
        # バンドルされたFFmpegが見つからない場合は、システムのFFmpegを探す
        return shutil.which("ffmpeg")


def check_ffmpeg_installed():
    """
    FFmpegがインストールされているかどうかを確認します。

    戻り値:
        None

    例外:
        SystemExit: 環境変数が設定されていない場合はプログラムを終了します。
    """
    if get_ffmpeg_path() is None:
        print("FFmpegが見つかりません。FFmpegをインストールしてパスを設定してください。")
        sys.exit(1)


def get_target_file_path():
    """
    ユーザーに変換元ファイルのパスを入力してもらいます。

    戻り値:
        str: 変換元ファイルのパスと拡張子を含むタプル。
    """
    while True:
        file_path = input("変換元のファイルのパスを入力してください: ")
        file_path = file_path.strip('"')

        if not os.path.exists(file_path):
            print("ファイルが見つかりません。もう一度入力してください。\n")
            continue
        
        file_extension = os.path.splitext(file_path)[1]
        if file_extension.lower() in (AUDIO_EXTENSIONS + VIDEO_EXTENSIONS):
            return file_path, file_extension
        else:
            print("非対応のファイル形式です。もう一度入力してください。")
            print(f"対応しているファイル形式: {", ".join(AUDIO_EXTENSIONS + VIDEO_EXTENSIONS)}\n")


def extract_audio_from_video(video_path:str, output_dir:str):
    """
    動画ファイルから音声を抽出し、指定したディレクトリに保存します。

    引数:
        video_path (str): 動画ファイルのパス。
        output_dir (str): 抽出した音声ファイルを保存するディレクトリ。

    戻り値:
        str: 抽出された音声ファイルのパス。

    例外：
        subprocess.CalledProcessError: FFmpegの処理に失敗した場合にスローされます。
    """
    filename = os.path.basename(video_path)
    filename_without_ext = os.path.splitext(filename)[0]
    audio_path = os.path.join(output_dir, f"{filename_without_ext}.m4a")

    # 出力ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)
    
    # FFmpegを使用して音声を抽出
    ffmpeg_path = get_ffmpeg_path()
    subprocess.run([
        ffmpeg_path,
        "-hide_banner",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_path
    ], check=True)

    return audio_path


def delete_files_in_directory(directory:str):
    """
    指定されたディレクトリ内のすべてのファイルを削除します（サブディレクトリのファイルは削除しません）。

    引数:
        directory (str): ファイルを削除する対象のディレクトリのパス。

    戻り値:
        None

    注意:
        この関数は指定されたディレクトリの直下にあるファイルのみを削除し、サブディレクトリやその中のファイルには影響を与えません。
        必要なバックアップを確認してから実行してください。
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)


def split_audio_file(input_path:str, output_dir:str, segment_time:int=300):
    """
    音声ファイルを指定された秒数ごとに分割して、指定されたディレクトリに保存します。

    引数:
        input_path (str): 分割する音声ファイルのパス。
        output_dir (str): 分割されたファイルを保存するディレクトリのパス。
        segment_time (int): 分割する秒数 (デフォルトは300秒 = 5分)。

    戻り値:
        list: 分割された音声ファイルのパスのリスト。

    例外：
        subprocess.CalledProcessError: FFmpegの処理に失敗した場合にスローされます。
    """
    # 出力ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)

    # 出力ファイル名
    filename = os.path.basename(input_path)
    filename_without_ext, file_extension = os.path.splitext(filename)

    # FFmpegを使用して音声ファイルを分割
    ffmpeg_path = get_ffmpeg_path()
    subprocess.run([
        ffmpeg_path,
        "-hide_banner",
        "-i", input_path,  # 入力ファイル
        "-f", "segment",   # セグメント形式で出力
        "-segment_time", str(segment_time),  # セグメントの長さ
        "-c", "copy",      # データを再エンコードせずにコピー
        os.path.join(output_dir, f"{filename_without_ext}-%03d{file_extension.lower()}")
    ], check=True)

    dir_path = Path(output_dir)
    audio_files = [file for file in dir_path.iterdir() if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS and file.name != filename]
    return audio_files


def create_client(settings:Settings):
    """
    OpenAI APIのクライアントを作成します。

    引数:
        settings (Settings): 設定情報を保持するSettingsクラスのインスタンス。

    戻り値:
        openai.OpenAI: OpenAI APIのクライアント。
    """
    type = settings.get_api_type()
    if type == "openai":
        client = openai.OpenAI(api_key=settings.get_api_key())
    elif type == "azure":
        client = openai.AzureOpenAI(
            api_key = settings.get_api_key(),
            api_version = "2024-02-01",
            azure_endpoint = settings.get_endpoint()
        )
    return client


def transcript_with_whisper(settings:Settings, input_path:str):
    """
    音声ファイルの音声認識を行い、結果をテキストファイルに保存します。

    引数:
        settings (Settings): 設定情報を保持するSettingsクラスのインスタンス。
        input_path (str): 音声認識を行う音声ファイルのパス。

    戻り値:
        str: 音声認識の結果として得られたテキスト。
    """
    client = create_client(settings)
    with open(input_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=settings.get_model_name(), 
            file=audio_file
        )
    return transcription.text


def process_transcription_files(settings:Settings, input_files:list, output_dir:str, output_filename:str):
    """
    指定されたディレクトリ内のすべての音声ファイルに対して、音声認識を行い、テキストファイルに出力します。

    引数:
        settings (Settings): 設定情報を保持するSettingsクラスのインスタンス。
        input_files (list): 音声ファイルのパスのリスト。
        output_dir (str): テキストファイルを保存するディレクトリのパス。
        output_filename (str): 出力するテキストファイルのファイル名。

    戻り値:
        None
    """
    # 出力ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)

    # 入力ディレクトリ内の音声ファイルに対して音声認識を行い、テキストファイルに保存
    all_text = ""
    temp_file = []
    total_files = len(input_files)
    for index, file in enumerate(input_files, start=1):
        file_path = str(file)
        print(f"変換中（{index}/{total_files}）: {file_path} ...", end=" ", flush=True)
        text = transcript_with_whisper(settings, file_path)
        all_text += text + "\n"
        filename = os.path.basename(file_path)
        output_name = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(output_dir, output_name)
        # 途中で処理が失敗した場合に備えて、一時ファイルとして保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        temp_file.append(output_path)
        print("完了")

    # テキストファイルを結合
    with open(os.path.join(output_dir, output_filename), "w", encoding="utf-8") as f:
        f.write(all_text)

    # 一時ファイルを削除
    for file in temp_file:
        os.remove(file)


def open_directory(path):
    """
    指定されたディレクトリをエクスプローラーで開きます。

    引数:
        path (str): 開くディレクトリのパス。

    戻り値:
        None
    """
    # フルパスに変換
    path = os.path.abspath(path)
    
    # ファイルの場合は親ディレクトリを取得
    if os.path.isfile(path):
        path = os.path.dirname(path)
    
    # OSによって処理を分ける
    system = platform.system()
    
    if system == 'Windows':
        subprocess.run(['explorer', path])
    elif system == 'Darwin':
        subprocess.run(['open', path])
    elif system == 'Linux':
        subprocess.run(['xdg-open', path])
    else:
        print(f"未対応のOS: {system}")


def main():
    """
    メインの処理を実行します。
    """
    display_app_title()

    # 設定ファイルを読み込む
    settings = Settings(SETTINGS_FILE)
    is_valid, error_message = settings.validate()
    if not is_valid:
        print(f"{error_message}\n設定ファイル `settings.ini` を確認してください。\n")
        sys.exit(1)

    # FFmpegがインストールされているか確認
    check_ffmpeg_installed()

    # 作業用ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(WORK_DIR, exist_ok=True)
    delete_files_in_directory(WORK_DIR)

    # 使用するAPIを表示
    print(f"API：{settings.get_api_type()}")
    print()

    # 変換元ファイルのパスを入力してもらう
    audio_file, extension = get_target_file_path()
    print("")

    # 動画ファイルの場合は音声を抽出する
    if extension in VIDEO_EXTENSIONS:
        print("動画から音声を抽出します。")
        try:
            audio_file = extract_audio_from_video(audio_file, WORK_DIR)
        except Exception as e:
            print("音声の抽出に失敗しました。プログラムを終了します。")
            print(f"エラー: {e}")
            sys.exit(1)
        print("")

    # 音声ファイルを分割
    print("音声を分割します。")
    try:
        split_files = split_audio_file(audio_file, WORK_DIR, settings.get_audio_segment_time())
    except Exception as e:
        print("音声の分割に失敗しました。プログラムを終了します。")
        print(f"エラー: {e}")
        sys.exit(1)
    print("")

    # 音声認識を行い、テキストファイルに保存
    print("音声をテキストに変換します。")
    output_filename = os.path.basename(audio_file)
    output_filename = os.path.splitext(output_filename)[0] + ".txt"
    try:
        process_transcription_files(settings, split_files, OUTPUT_DIR, output_filename)
    except Exception as e:
        print("音声のテキスト化に失敗しました。プログラムを終了します。")
        print(f"エラー: {e}")
        sys.exit(1)
    print("")

    print("処理が完了しました。")
    print(f"出力ファイル：{os.path.join(OUTPUT_DIR, output_filename)}")
    open_directory(OUTPUT_DIR)

    if getattr(sys, "frozen", False):
        print("")
        input("Enterキーを押して終了してください。")


if __name__ == "__main__":
    main()
