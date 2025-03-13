import ssl
import os

# Find certificate path
cert_path = os.path.join(os.path.dirname(ssl.__file__), "cert.pem")
print(f"Certificate path: {cert_path}")

# Check if it exists
if not os.path.exists(cert_path):
    import certifi
    print(f"Using certifi path: {certifi.where()}")
    # Create symlink or copy certificates
    os.symlink(certifi.where(), cert_path)
    print("Certificates installed!")
else:
    print("Certificates already exist.")