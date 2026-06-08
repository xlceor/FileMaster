import hashlib
import uuid
import platform
import subprocess
import os
import requests
import hmac
import time
import json
from cryptography.fernet import Fernet
 
API_URL = os.getenv("LICENSE_API_URL", "https://api.yourdomain.com/verify")
SECRET_KEY = os.getenv("LICENSE_SECRET_KEY", "default-insecure-key-change-this").encode()
ENCRYPTION_KEY = os.getenv("LICENSE_ENCRYPTION_KEY", "u-l_Jj23u-l_Jj23u-l_Jj23u-l_Jj23u-l_Jj23u-M=").encode()
LEASE_FILE = os.path.expanduser("~/.filemaster_lease")

def get_hardware_fingerprint():
    """
    Generates a unique hardware fingerprint.
    """
    info = {
        "processor": platform.processor(),
        "node": platform.node(),
        "system": platform.system(),
        "machine": platform.machine(),
    }
    
    if platform.system() == "Windows":
        try:
            cmd = "wmic csproduct get uuid"
            uuid_str = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            info["uuid"] = uuid_str
        except Exception:
            pass

    fingerprint_str = "|".join([str(v) for v in info.values()])
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()

def sign_request(payload: str):
    """Signs a payload using HMAC-SHA256."""
    return hmac.new(SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()

def verify_license(license_key: str):
    """
    Sends the activation request to the server.
    """
    fingerprint = get_hardware_fingerprint()
    payload = f"{license_key}:{fingerprint}"
    signature = sign_request(payload)
    
    response = requests.post(
        API_URL,
        json={"key": license_key, "fingerprint": fingerprint, "signature": signature},
        timeout=10
    )
    
    if response.status_code == 200:
        save_local_lease(response.json())
        return True
    return False

def check_local_lease():
    """
    Checks if a valid, non-expired local lease exists.
    """
    if not os.path.exists(LEASE_FILE):
        return False
    
    try:
        cipher = Fernet(ENCRYPTION_KEY)
        with open(LEASE_FILE, 'rb') as f:
            data = cipher.decrypt(f.read())
        lease = json.loads(data)
        
        # Check if expired
        if time.time() > lease.get('expires_at', 0):
            return False
            
        return True
    except Exception:
        return False

def save_local_lease(token_data):
    """
    Saves a lease file locally after successful activation.
    Lease duration: 30 days
    """
    lease = {
        "expires_at": time.time() + (30 * 24 * 60 * 60),
        "data": token_data
    }
    
    cipher = Fernet(ENCRYPTION_KEY)
    encrypted_data = cipher.encrypt(json.dumps(lease).encode())
    
    with open(LEASE_FILE, 'wb') as f:
        f.write(encrypted_data)
