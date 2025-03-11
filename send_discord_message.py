import os
import requests

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
STATUS_FILE = "status.txt"
CHUNK_SIZE = 1800  # Discord message limit is ~2000 characters, keeping margin

def read_status():
    """Read status from file."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: status.txt not found.")
        return None

def split_message(message, chunk_size):
    """Splits the message into chunks without breaking sentences."""
    words = message.split(" ")
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:
            current_chunk += f" {word}" if current_chunk else word
        else:
            chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def send_to_discord(message):
    """Send the message to Discord in chunks."""
    if not DISCORD_WEBHOOK:
        print("Error: DISCORD_WEBHOOK is not set.")
        return
    
    headers = {"Content-Type": "application/json"}
    chunks = split_message(message, CHUNK_SIZE)

    for chunk in chunks:
        payload = {"content": chunk}
        response = requests.post(DISCORD_WEBHOOK, json=payload, headers=headers)

        if response.status_code != 204:
            print(f"Failed to send message: {response.text}")
        else:
            print("Message sent successfully.")

if __name__ == "__main__":
    message = read_status()
    if message:
        send_to_discord(message)
    else:
        print("No status message to send.")
