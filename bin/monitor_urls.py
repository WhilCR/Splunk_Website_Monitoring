#!/usr/bin/env python3
import requests, ssl, socket, datetime,json, sys

def get_cert_expiry(host, port=443):
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.settimeout(5.0)
            sock.connect((host,port))
            cert = sock.getpeercert()
            expires = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            return expires
    except Exception as e:
        return f"Error: {str(e)}"
    
def check_url(url):
    result = {
        "url": url,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    try: 
        response = requests.get(url, timeout=20)
        result["status_code"] = response.status.code
        result["response_time_ms"] = response.elapsed.total_seconds() * 1000
    except Exception as e:
        result["status_code"] = "Error"
        result["error"] = str(e)
        
    try:
        host = url.split("://")[1].split("/")[0]
        expiry = get_cert_expiry(host)
        if isinstance(expiry, datetime.datetime):
            result["cert_expiry_error"] = expiry.isoformat()
            result["days_until_expiry"] = (expiry - datetime.datetime.utcnow()).days
        else:
            result["cert_expiry_error"] = expiry
    except Exception as e:
        result["cert_expiry_error"] = str(e)
        
    print(json.dumps(result))
    
if __name__ == "__main__":
    # Example: pass URLs as a comma-separated list in argument
    urls = sys.argv[1].split(",") if len(sys.argv) > 1 else []
    for url in urls:
        check_url(url)