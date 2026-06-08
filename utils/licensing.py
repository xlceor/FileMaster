import hashlib
import uuid
import platform
import subprocess
import os
import requests
import time
import json
import jwt # PyJWT library

# API URL - can be hardcoded as it's not a secret
API_URL = "https://api.yourdomain.com/verify"

# PUBLIC KEY for verifying the server-signed JWT lease
# This is NOT a secret and can be hardcoded.
# REPLACE WITH YOUR ACTUAL RSA PUBLIC KEY IN PEM FORMAT
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyJ23j... (your public key) ...nB8Z/wIDAQAB
-----END PUBLIC KEY-----"""

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

def verify_license(license_key: str):
    """
    Sends the activation request to the server.
    The server will return a signed JWT lease upon successful activation.
    """
    fingerprint = get_hardware_fingerprint()
    
    response = requests.post(
        API_URL,
        json={"key": license_key, "fingerprint": fingerprint},
        timeout=10
    )
    
    if response.status_code == 200:
        # Expecting the server to return a JWT token in the 'lease_token' field
        response_data = response.json()
        lease_token = response_data.get('lease_token')
        if lease_token:
            save_local_lease(lease_token)
            return True
    return False

def check_local_lease():
    """
    Checks if a valid, non-expired local JWT lease exists and is valid.
    """
    if not os.path.exists(LEASE_FILE):
        return False
    
    try:
        with open(LEASE_FILE, 'r') as f:
            lease_token = f.read()
        
        # Verify the JWT token using the public key
        # 'verify_exp=True' checks the 'exp' claim for expiration
        # 'verify_signature=True' checks the signature against PUBLIC_KEY_PEM
        decoded_lease = jwt.decode(lease_token, PUBLIC_KEY_PEM, algorithms=["RS256"], options={"verify_exp": True, "verify_signature": True})
        
        # Additional check: ensure the fingerprint in the lease matches the current machine
        current_fingerprint = get_hardware_fingerprint()
        if decoded_lease.get('fingerprint') != current_fingerprint:
            return False

        return True
    except jwt.ExpiredSignatureError:
        print("Local lease expired.")
        return False
    except jwt.InvalidTokenError as e:
        print(f"Invalid local lease token: {e}")
        return False
    except Exception as e:
        print(f"Error checking local lease: {e}")
        return False

def save_local_lease(lease_token: str):
    """
    Saves the JWT lease token locally.
    """
    try:
        with open(LEASE_FILE, 'w') as f:
            f.write(lease_token)
    except Exception as e:
        print(f"Error saving local lease: {e}")
