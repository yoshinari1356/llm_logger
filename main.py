from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()  # .env 読み込み

# OpenAI APIクライアントを初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message

    prompt = f"""
あなたは、日々の出来事を記録・整理するアシスタントです。以下のメッセージを受け取り、「記録日時」「分類」「タイトル」「内容」の形式で整理してください。

【入力】
{user_input}

【出力形式】
{{
  "記録日時": "YYYY-MM-DDTHH:MM:SS",
  "分類": "カテゴリ（例：生活・仕事・学び・健康など）",
  "タイトル": "簡潔なタイトル",
  "内容": "補足・要約を含む、自然な文章"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは日々の記録を整形するアシスタントです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    output_text = response.choices[0].message.content.strip()
    try:
        record = json.loads(output_text)
    except json.JSONDecodeError:
        # JSONパースできなかった場合のフォールバック
        record = {
            "記録日時": datetime.now().isoformat(),
            "分類": "未分類",
            "タイトル": "記録エラー",
            "内容": output_text
        }

    append_to_sheet(record)

    return record

import gspread
from google.oauth2.service_account import Credentials

# Google Sheets 書き込み関数
def append_to_sheet(record: dict):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    CREDS_FILE = "credentials/credentials.json"  # パスを合わせてください
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # URLから抽出

    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # 1枚目のシートを使用

    row = [
        record.get("記録日時"),
        record.get("分類"),
        record.get("タイトル"),
        record.get("内容")
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
