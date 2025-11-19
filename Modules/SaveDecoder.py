import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Modules.error import SaveFileError

# --- Configuration ---
HOLLOW_KNIGHT_KEY = b'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'
C_SHARP_HEADER = bytes([
    0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0,
    0, 0, 0, 0, 6, 1, 0, 0, 0
])
C_SHARP_FOOTER = b'\x0b'

# --- Helper Functions ---

def remove_header(data: bytes) -> bytes:
    """Removes the C# BinaryFormatter header from the save data."""
    if not data.startswith(C_SHARP_HEADER):
        return data
    processed_data = data[len(C_SHARP_HEADER):-1]
    offset = 0
    while offset < len(processed_data):
        byte = processed_data[offset]
        offset += 1
        if (byte & 0x80) == 0:
            break
    return processed_data[offset:]

def add_header(data: bytes) -> bytes:
    """Adds the C# BinaryFormatter header to the data."""
    length = len(data)
    length_prefix = bytearray()
    while length >= 0x80:
        length_prefix.append((length | 0x80) & 0xFF)
        length >>= 7
    length_prefix.append(length & 0x7F)
    return C_SHARP_HEADER + bytes(length_prefix) + data + C_SHARP_FOOTER

def aes_decrypt(data: bytes) -> bytes:
    """Decrypts data using AES (ECB mode) and removes PKCS7 padding."""
    cipher = AES.new(HOLLOW_KNIGHT_KEY, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(data)
    try:
        return unpad(decrypted_data, AES.block_size)
    except ValueError:
        return decrypted_data # Return as-is if unpadding fails

def aes_encrypt(data: bytes) -> bytes:
    cipher = AES.new(HOLLOW_KNIGHT_KEY, AES.MODE_ECB)
    padded_data = pad(data, AES.block_size)
    return cipher.encrypt(padded_data)

# --- Core Logic ---

def decrypt_hollow_knight_save(data: bytes) -> str:
    try:
        processed_data = remove_header(data)
        decoded_data = base64.b64decode(processed_data)
        decrypted_data = aes_decrypt(decoded_data)
        json_string = decrypted_data.decode('utf-8')
        json.loads(json_string) # Verify it's valid JSON
        return json_string
    except Exception as e:
        # Raised as a custom error to be caught by AppManager
        raise SaveFileError(f"Failed to decrypt save file. Error: {e}")

def encrypt_hollow_knight_save(json_data: dict) -> bytes:
    try:
        json_string = json.dumps(json_data, separators=(',', ':'))
        json_bytes = json_string.encode('utf-8')
        encrypted_data = aes_encrypt(json_bytes)
        encoded_data = base64.b64encode(encrypted_data)
        final_data = add_header(encoded_data)
        return final_data
    except Exception as e:
        # Raised as a custom error to be caught by AppManager
        raise SaveFileError(f"Failed to encrypt save data. Error: {e}")
