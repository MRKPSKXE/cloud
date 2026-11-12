import base64
import os
from flask import Flask, jsonify, request
from google import genai
from google.genai import types

app = Flask(__name__)

# Lấy API Key từ biến môi trường được cấu hình bảo mật trên Cloud
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/chat", methods=["POST"])
def chat():
  try:
    data = request.json
    audio_b64 = data.get("audio")
    if not audio_b64:
      return jsonify({"reply": "Thiếu dữ liệu audio."}), 400

    print("[CLOUD] Nhận audio từ ESP32, đang gọi Gemini...")
    audio_bytes = base64.b64decode(audio_b64)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(
                data=audio_bytes, mime_type="audio/pcm;rate=16000"
            ),
            (
                "Hãy nghe đoạn âm thanh này và trả lời ngắn gọn, thân thiện bằng"
                " tiếng Việt (tối đa 2 câu)."
            ),
        ],
    )

    reply_text = (
        response.text
        if response.text
        else "Tôi không nghe rõ, bạn nói lại nhé."
    )
    print(f"[CLOUD] Phản hồi: {reply_text}")
    return jsonify({"reply": reply_text})

  except Exception as e:
    print(f"[CLOUD ERROR]: {e}")
    return jsonify({"reply": "Lỗi xử lý server."}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)