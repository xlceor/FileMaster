import hashlib
import uuid
import platform
import subprocess
import os
import requests
import time
import json
import jwt # PyJWT library

API_URL = "http://localhost:3000/api/verify"

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvUHzMm3b91GzPl+5QpZX
PJarRoFbUMtotGTFWmJir8sHI9av/UzcCfraFq8165hZQvy1H++fYjY46/6uuEWG
ju/7znLbugqUyoJd44EGtuIIehjAkrWsM8HnKcRyXKP4x9wGRtRdb47C5+HL+Xw4
6SOMuCazz0uOP4jHrzrei/LplVF9jau7sjH7PpO9XgO8b2ShJLuwSi2VWJGJrxJu
C2qngJj5kLiN7uLfHzrUDhfhgRjG7q4MOEDzPZLp1pI0K73Ph6sQZ/n/GTKsoY/z
MnASIs4/9CweqqldyPglDxgAfhhI1OrpdBZuWmTlRJ+X5sq3nJzAyIxPCVNdTSlV
NwIDAQAB
-----END PUBLIC KEY-----
"""

LEASE_FILE = os.path.expanduser("~/.filemaster_lease")

def get_hardware_fingerprint():
    """
    Generates a unique hardware fingerprint using multiple system sources
    for increased stability across Windows and macOS.
    """
    info = {
        "processor": platform.processor(),
        "node": platform.node(),
        "system": platform.system(),
        "machine": platform.machine(),
    }

    # Attempt to get system-specific unique identifiers
    try:
        if platform.system() == "Windows":
            # Motherboard UUID
            info["uuid"] = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split('\n')[1].strip()
            # Disk Serial Number (C: drive)
            info["disk_serial"] = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split('\n')[1].strip()
        elif platform.system() == "Darwin":  # macOS
            # Hardware UUID
            info["uuid"] = subprocess.check_output("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'", shell=True).decode().strip()
            # Serial Number
            info["serial"] = subprocess.check_output("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformSerialNumber/{print $(NF-1)}'", shell=True).decode().strip()
    except Exception:
        # Fallback to base info if specific hardware commands fail
        pass

    fingerprint_str = "|".join([str(v) for v in info.values() if v])
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
