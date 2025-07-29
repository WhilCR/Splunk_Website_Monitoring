#!/usr/bin/env python3
import os
import json
import requests
import ssl
import socket
import datetime
import urllib.request
import urllib.error
import ssl

def get_cert_expiry(host, port=443):
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.settimeout(5.0)
            sock.connect((host, port))
            cert = sock.getpeercert()
            expires = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            return expires
    except Exception as e:
        return f"Error: {str(e)}"

def get_urls_from_kvstore():
    splunkd_uri = os.environ.get("SPLUNKD_URI", "https://localhost:8089")
    session_key = os.environ.get("SPLUNKD_SESSION_KEY")

    if not session_key:
        raise Exception("Missing SPLUNKD_SESSION_KEY environment variable")

    url = f"{splunkd_uri}/servicesNS/nobody/Splunk_Website_Monitoring/storage/collections/data/url_monitoring_targets"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Splunk {session_key}")
    req.add_header("Content-Type", "application/json")

    # Only for development/testing: ignore SSL validation
    context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read())
            return [entry["url"] for entry in data if "url" in entry]
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTPError fetching URLs: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URLError fetching URLs: {e.reason}")

    return []

def check_url(url):
    result = {
        "url": url,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    try:
        response = requests.get(url, timeout=20)
        result["status_code"] = response.status_code
        result["response_time_ms"] = response.elapsed.total_seconds() * 1000
    except Exception as e:
        result["status_code"] = "Error"
        result["error"] = str(e)

    try:
        host = url.split("://")[1].split("/")[0]
        expiry = get_cert_expiry(host)
        if isinstance(expiry, datetime.datetime):
            result["cert_expiry"] = expiry.isoformat()
            result["days_until_expiry"] = (expiry - datetime.datetime.utcnow()).days
        else:
            result["cert_expiry_error"] = expiry
    except Exception as e:
        result["cert_expiry_error"] = str(e)

    print(json.dumps(result))

if __name__ == "__main__":
    urls = get_urls_from_kvstore()
    if not urls and len(sys.argv) > 1:
        urls = sys.argv[1].split(",")
    for url in urls:
        check_url(url)
