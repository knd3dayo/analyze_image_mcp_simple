# ClineとMCPサーバーでエビデンスチェック

## 概要
* ClineとMCPサーバーを用いて設計書の画像とエビデンス画像を比較、チェックするためのサンプル。

### 前提条件
* 以下のソフトウェアがインストール済みであること
    * vscode
    * cline
    * Python
    * uv

* OpenAIのAPIキーを取得していること

## 準備
1. このGitリポジトリをclineします。
    ```bash
    git clone https://github.com/knd3dayo/analyze_image_mcp_simple.git
    ```

1. Python仮想環境を作成します.
    ```batch
    python -m venv venv
    ```

1. venv環境を有効にして、画像比較用MCPサーバーをインストールします
    ```batch
    venv\Scripts\Activate
    pip install .
    ```

1. `sample_cline_mcp_settings.json`の内容を編集して、`cline_mcp_settings.json`に追加します.
    PATH_TO_VENVはvenvへのパス、OPENAI_API_KEYはOpenAIのAPIキーを設定。

    ```json
    "analyze_image_mcp_simple": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "<PATH_TO_VENV>", 
        "run",
        "-m",
        "analyze_image_mcp_simple.mcp_modules.mcp_app_server"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-****************",
        "OPENAI_COMPLETION_MODEL": "gpt-4.1"
      }
    }
    ```

1. ClineのMCPサーバー一覧に`analyze_image_mcp_simple`が表示されて有効になっていれば設定完了です。


## 実行
1. `data/design_doc_images`ディレクトリにチェックしたい設計書の画像を格納します。
1. `data/evidence_images`ディレクトリに、設計書に基づき設定を行った際のエビデンス画像を格納します。
1. Clineで`memory-bankを初期化して`と指示します。
1. Clineで`エビデンスチェックして`と指示します。
1. エビデンスのチェックが実行され、`progress.md`に結果が出力されます。


