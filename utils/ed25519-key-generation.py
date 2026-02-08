# https://pypi.org/project/PyNaCl/

import nacl
import nacl.signing
import secrets

seed = secrets.token_bytes(32)

# Generate a new random signing key
signing_key = nacl.signing.SigningKey(seed)

# Obtain the hex-encoded signing key
print("Signing key:")
print(signing_key.encode().hex())

# Obtain the hex-encoded verify key for the given signing key
# Use this in the Anchorage Digital Web Dashboard when creating an API key
print("Public key:")
print(signing_key.verify_key.encode().hex())
