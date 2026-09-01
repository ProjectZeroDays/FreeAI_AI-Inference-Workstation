import sys
import json
import urllib.request
import urllib.error

API_URL = "https://api.agnes-ai.com/v1/chat/completions"
API_KEY = "sk-gE940pJBd02SRt3c8hBZPvQ3RsnM2gM14EuWJO3DkXeSbtb4"

def stream_chat(messages):
    data = json.dumps({"model": "agnes-2.0-flash", "messages": messages, "stream": True}).encode()
    req = urllib.request.Request(API_URL, data=data, headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        for line in response:
            line = line.decode().strip()
            if line.startswith("data: "):
                try:
                    chunk = json.loads(line[6:])
                    token = chunk["choices"][0]["delta"].get("content", "")
                    if token:
                        sys.stdout.write(token)
                        sys.stdout.flush()
                except Exception:
                    pass

if __name__ == "__main__":
    print("Streaming Chat Demo - Type 'quit' to exit")
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        messages.append({"role": "user", "content": user_input})
        print("Agnes: ", end="", flush=True)
        stream_chat(messages)
        print()
        messages.append({"role": "assistant", "content": ""})
    print("Goodbye!")
