FROM python:3.10-slim

# 作業ディレクトリ作成
WORKDIR /app

# 必要ファイルをコピー
COPY main.py /app
COPY requirements.txt /app
COPY .env /app

# パッケージインストール
RUN pip install --no-cache-dir -r requirements.txt

# ポート開放
EXPOSE 8000

# 実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
