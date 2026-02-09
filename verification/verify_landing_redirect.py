import time
import subprocess
import os
import sys
from playwright.sync_api import sync_playwright

def verify_landing_redirect():
    # Set environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite:///devispro.db'
    env['FLASK_APP'] = 'app.py'

    print("Starting Flask application...")
    # Start the app in the background
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid # Create a new session group to kill all children later
    )

    try:
        # Give it time to start
        time.sleep(5)

        print("Starting Playwright verification...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Capture console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: console_errors.append(str(exc)))

            # Navigate to root (/)
            print("Navigating to / (expecting redirect to /login)...")
            try:
                response = page.goto("http://localhost:5000/", timeout=10000)
                if not response:
                    print(f"FAILED: Page load failed.")
                    return False
            except Exception as e:
                print(f"FAILED: Could not reach /: {e}")
                return False

            # Check if redirected to /login
            current_url = page.url
            if "/login" in current_url:
                print(f"SUCCESS: Redirected to {current_url}")
            else:
                print(f"FAILED: Did not redirect to /login. Current URL: {current_url}")
                page.screenshot(path="verification/error_redirect.png")
                return False

            # Verify login page content
            try:
                # Check for login form or specific text
                page.wait_for_selector('form[data-submit-loading]', timeout=5000)
                print("SUCCESS: Login form found.")
            except Exception:
                print("FAILED: Login form not found.")
                return False

            # Take screenshot of the login page
            page.screenshot(path="verification/landing_redirect_login.png")
            print("Screenshot saved to verification/landing_redirect_login.png")

            if console_errors:
                print("\n[!] Console Errors detected:")
                for err in console_errors:
                    print(f"  - {err}")
            else:
                print("\n[+] No console errors detected.")

            browser.close()
            print("\nVerification finished.")
            return True

    finally:
        print("Stopping Flask application...")
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        stdout, stderr = process.communicate()
        if stderr:
            # Filter out the usual warnings
            errors = stderr.decode()
            if "WARNING: This is a development server" not in errors:
                print("Server Errors:\n", errors)

if __name__ == "__main__":
    success = verify_landing_redirect()
    if not success:
        sys.exit(1)
