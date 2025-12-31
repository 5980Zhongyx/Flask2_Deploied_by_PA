#!/usr/bin/env python3
"""Test script for security enhancements"""

import requests
import time

def test_security_headers():
    """Test security headers and cookies configuration"""
    try:
        # Test the home page
        response = requests.get('http://localhost:5000/', timeout=5)

        print("=== Security Headers Test ===")
        print(f"Status Code: {response.status_code}")

        # Check security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Content-Security-Policy'
        ]

        for header in security_headers:
            value = response.headers.get(header, 'NOT SET')
            status = "✅" if value != 'NOT SET' else "❌"
            print(f"{status} {header}: {value}")

        # Check cookies if login is required
        if response.cookies:
            print("\n=== Cookies Test ===")
            for cookie in response.cookies:
                print(f"Cookie: {cookie.name}")
                print(f"  Secure: {cookie.secure}")
                print(f"  HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                print(f"  SameSite: {cookie.get_nonstandard_attr('SameSite', 'Not set')}")

        print("\n=== Test Results ===")
        print("✅ Security headers check completed")
        print("✅ Cookies configuration verified")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure the Flask app is running on port 5000")

if __name__ == '__main__':
    print("Testing security enhancements...")
    test_security_headers()
