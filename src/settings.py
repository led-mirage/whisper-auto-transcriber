# Whisper Auto Transcriber
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import configparser

class Settings:
    """
    アプリケーション設定を保持するクラス。

    このクラスは、指定された設定ファイルと環境変数から設定情報を取得します。
    """
    
    def __init__(self, config_file:str="settings.ini"):
        """
        設定インスタンスを作成します。

        引数:
            config_file (str): 設定ファイルのパス。デフォルトは"settings.ini"。
        """        
        self.config = configparser.ConfigParser()
        self.config.read(config_file, "UTF-8")


    def _get(self, section:str, key:str, key_env:str):
        """
        設定ファイルおよび環境変数から設定値を取得します。

        引数:
            section (str): 設定ファイルのセクション名。
            key (str): 設定ファイルのキー名。
            key_env (str): 環境変数のキー名。

        戻り値:
            strまたはNone: 見つかった設定値。
        """
        if key_value := self.config.get(section, key):
            return key_value
        if key_env_value := self.config.get(section, key_env):
            return os.getenv(key_env_value)
        return None


    def _get_section(self):
        """
        使用するAPIのセクションを取得します。

        戻り値:
            str: APIのセクション名。

        例外:
            ValueError: APIタイプがサポートされていない場合に発生。
        """
        api_type = self.get_api_type()
        if api_type == "openai":
            return "OpenAI"
        elif api_type == "azure":
            return "Azure"
        else:
            raise ValueError(f"API type '{api_type}' is not supported.")


    def get_audio_segment_time(self):
        """
        音声の分割時間を取得します。

        戻り値:
            int: 分割時間（秒）。
        """
        return self.config.get("General", "audio_segment_time")


    def get_api_type(self):
        """
        使用するAPIタイプを取得します。

        戻り値:
            str: APIタイプ。
        """
        return self.config.get("API", "type").lower()


    def get_model_name(self):
        """
        モデル名を取得します。

        戻り値:
            str: モデル名。
        """
        section = self._get_section()
        return self.config.get(section, "model_name")


    def get_api_key(self):
        """
        APIキーを取得します。

        戻り値:
            strまたはNone: APIキー。
        """
        section = self._get_section()
        return self._get(section, "api_key", "api_key_env")


    def get_endpoint(self):
        """
        Azureのエンドポイントを取得します（OpenAIの場合はNoneを返す）。

        戻り値:
            strまたはNone: エンドポイント。
        """
        section = self._get_section()
        if section == "Azure":
            return self._get(section, "endpoint", "endpoint_env")
        else:
            return None


    def validate(self):
        """
        設定が正しいかどうかを検証します。

        戻り値:
            tuple: 検証結果とエラーメッセージ（エラーがない場合はNone）。
        """
        # APIタイプが正しいかどうかを確認
        api_type = self.get_api_type()
        if api_type not in ["openai", "azure"]:
            error_message = f"API type '{api_type}' はサポートされていません。"
            return False, error_message

        section = self._get_section()

        # モデル名が設定されているかどうかを確認
        if not self.get_model_name():
            error_message = f"{section} モデル名が設定されていません。"
            return False, error_message

        # APIキーが設定されているかどうかを確認
        if not self.get_api_key():
            error_message = f"{section} APIキーの値が書かれていないか、環境変数が設定されていません。"
            return False, error_message
        
        # Azureの場合、エンドポイントが設定されているかどうかを確認
        if api_type == "azure" and not self.get_endpoint():
            error_message = f"{section} エンドポイントの値が書かれていないか、環境変数が設定されていません。"
            return False, error_message
        
        return True, None
