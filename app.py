import os
from flask import Flask, request
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twilio credentials (optional - for sending messages via API)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

SYSTEM_PROMPT = """
You are a helpful WhatsApp business assistant.
Rules:
1. Keep replies short and clear.
2. Be polite and professional.
3. If asked about pricing, timing, address, services, or booking, answer based on provided business info.
4. If you do not know, say: 'Please contact the business directly for that detail.'
"""

# Example business data
BUSINESS_INFO = """
Business Name: Smart Clinic
Services: General checkup, dental consultation, skin consultation
Timing: Monday to Saturday, 9 AM to 7 PM
Address: Gurugram, Haryana
Booking: Share your name, phone number, preferred date, and time
Pricing: Basic consultation starts at Rs 500
"""

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI bot is running."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if not incoming_msg:
        response = MessagingResponse()
        response.message("Please send a message.")
        return str(response)

    prompt = f"""
Business information:
{BUSINESS_INFO}

Customer message:
{incoming_msg}

Respond as the business assistant on WhatsApp.
"""

    try:
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )

        reply_text = ai_response.choices[0].message.content.strip()

        if not reply_text:
            reply_text = "Sorry, I could not generate a response right now."

    except Exception as e:
        print(f"Error: {e}")
        reply_text = f"Sorry, the assistant is temporarily unavailable. Error: {str(e)[:100]}"

    twilio_response = MessagingResponse()
    twilio_response.message(reply_text)
    return str(twilio_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
