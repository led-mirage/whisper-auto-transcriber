# Whisper Auto Transcriber
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import subprocess
import sys
from pathlib import Path

import openai


APP_NAME = "Whisper Auto Transcriber"
APP_VERSION = "1.0.0"
COPYRIGHT = "© 2025 led-mirage"

AUDIO_EXTENSIONS = [".mp3", ".m4a"]
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"]
WORK_DIR = "./workdir"
OUTPUT_DIR = "./output"
SEGMENT_TIME = 300


def display_app_title():
    """
    アプリケーションのタイトルを表示します。

    戻り値:
        None
    """
    print("-" * 50)
    print(f" {APP_NAME} v{APP_VERSION}")
    print("")
    print(f" {COPYRIGHT}")
    print("-" * 50)
    print("")


def check_openai_api_key():
    """
    環境変数OPENAI_API_KEYが設定されているかを確認します。

    戻り値:
        None

    例外:
        SystemExit: 環境変数が設定されていない場合はプログラムを終了します。
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("環境変数OPENAI_API_KEYが設定されていません。APIキーを設定してください。")
        sys.exit(1)


def check_ffmpeg_installed():
    """
    FFmpegがインストールされているかどうかを確認します。

    戻り値:
        None

    例外:
        SystemExit: 環境変数が設定されていない場合はプログラムを終了します。
    """
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print("ffmpegがインストールされていないか、パスが設定されていません。")
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


def extract_audio_from_video(video_path, output_dir):
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
    subprocess.run([
        "ffmpeg",
        "-hide_banner",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
    
        audio_path
    ], check=True)

    return audio_path


def delete_files_in_directory(directory):
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


def split_audio_file(input_path, output_dir, segment_time=300):
    """
    音声ファイルを指定された秒数ごとに分割して、指定されたディレクトリに保存します。

    引数:
        input_path (str): 分割する音声ファイルのパス。
        output_dir (str): 分割されたファイルを保存するディレクトリのパス。
        segment_time (int): 分割する秒数 (デフォルトは300秒 = 5分)。

    戻り値:
        None

    例外：
        subprocess.CalledProcessError: FFmpegの処理に失敗した場合にスローされます。
    """
    # 出力ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)

    # 出力ファイル名
    filename = os.path.basename(input_path)
    filename_without_ext, file_extension = os.path.splitext(filename)

    # FFmpegを使用して音声ファイルを分割
    subprocess.run([
        "ffmpeg",
        "-hide_banner",
        "-i", input_path,  # 入力ファイル
        "-f", "segment",   # セグメント形式で出力
        "-segment_time", str(segment_time),  # セグメントの長さ
        "-c", "copy",      # データを再エンコードせずにコピー
        os.path.join(output_dir, f"{filename_without_ext}-%03d{file_extension.lower()}")
    ], check=True)


def transcript_with_whisper(input_path):
    """
    音声ファイルの音声認識を行い、結果をテキストファイルに保存します。

    引数:
        input_path (str): 音声認識を行う音声ファイルのパス。

    戻り値:
        str: 音声認識の結果として得られたテキスト。
    """
    client = openai.OpenAI()
    with open(input_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text


def process_transcription_files(input_dir, output_dir, output_filename):
    """
    指定されたディレクトリ内のすべての音声ファイルに対して、音声認識を行い、テキストファイルに出力します。

    引数:
        input_dir (str): 音声認識を行う音声ファイルが保存されているディレクトリのパス。
        output_dir (str): テキストファイルを保存するディレクトリのパス。
        output_filename (str): 出力するテキストファイルのファイル名。

    戻り値:
        None
    """
    # 入力ディレクトリが存在しない場合は何もしない
    dir_path = Path(input_dir)
    if not dir_path.is_dir():
        return

    # 出力ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(output_dir, exist_ok=True)

    # 入力ディレクトリ内の音声ファイルに対して音声認識を行い、テキストファイルに保存
    all_text = ""
    temp_file = []

    audio_files = [file for file in dir_path.iterdir() if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS]
    total_files = len(audio_files)

    for index, file in enumerate(audio_files, start=1):
        file_path = str(file)
        print(f"変換中（{index}/{total_files}）: {file_path} ...", end=" ", flush=True)
        text = transcript_with_whisper(file_path)
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


def main():
    """
    メインの処理を実行します。
    """
    display_app_title()

    # 環境変数 OPENAI_API_KEY が設定されているか確認
    check_openai_api_key()

    # FFmpegがインストールされているか確認
    check_ffmpeg_installed()

    # 作業用ディレクトリを作成（既に存在する場合は何もしない）
    os.makedirs(WORK_DIR, exist_ok=True)
    delete_files_in_directory(WORK_DIR)

    # 変換元ファイルのパスを入力してもらう
    audio_file, extension = get_target_file_path()
    print("")

    # 動画ファイルの場合は音声を抽出すう
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
        split_audio_file(audio_file, WORK_DIR, SEGMENT_TIME)
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
        process_transcription_files(WORK_DIR, OUTPUT_DIR, output_filename)
    except Exception as e:
        print("音声のテキスト化に失敗しました。プログラムを終了します。")
        print(f"エラー: {e}")
        sys.exit(1)
    print("")

    print("処理が完了しました。")
    print(f"出力ファイル：{os.path.join(OUTPUT_DIR, output_filename)}")


if __name__ == "__main__":
    main()
