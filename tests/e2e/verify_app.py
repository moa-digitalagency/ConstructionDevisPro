import time
import subprocess
import os
import sys
from playwright.sync_api import sync_playwright

def verify_app():
    # Set environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite:///devispro.db'
    env['DEMO_SUPERADMIN_EMAIL'] = 'admin@devispro.com'
    env['DEMO_SUPERADMIN_PASSWORD'] = 'Admin123!'
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

            # 1. Login
            print("Navigating to Login...")
            try:
                response = page.goto("http://localhost:5000/login", timeout=10000)
                if not response or response.status != 200:
                    print(f"FAILED: Login page load failed. Status: {response.status if response else 'None'}")
                    return False
            except Exception as e:
                print(f"FAILED: Could not reach login page: {e}")
                return False

            print("Logging in...")
            page.fill('input[name="email"]', 'admin@devispro.com')
            page.fill('input[name="password"]', 'Admin123!')
            page.click('button[type="submit"]')

            # Wait for redirect to dashboard
            try:
                page.wait_for_url("**/dashboard", timeout=10000)
                print("SUCCESS: Login successful, redirected to Dashboard.")
            except Exception:
                print(f"FAILED: Did not redirect to dashboard. Current URL: {page.url}")
                page.screenshot(path="error_login.png")
                return False

            # Check visual integrity of Dashboard
            page.screenshot(path="verify_dashboard.png")

            # 2. Check Projects
            print("Navigating to Projects...")
            response = page.goto("http://localhost:5000/projects")
            if response.status != 200:
                 print(f"FAILED: Projects page returned {response.status}")
            else:
                 print("SUCCESS: Projects page loaded.")
            page.screenshot(path="verify_projects.png")

            # 3. Check Quotes
            print("Navigating to Quotes...")
            response = page.goto("http://localhost:5000/quotes")
            if response.status != 200:
                 print(f"FAILED: Quotes page returned {response.status}")
            else:
                 print("SUCCESS: Quotes page loaded.")
            page.screenshot(path="verify_quotes.png")

            # Check BPU
            print("Navigating to BPU...")
            response = page.goto("http://localhost:5000/bpu")
            if response.status != 200:
                 print(f"FAILED: BPU page returned {response.status}")
            else:
                 print("SUCCESS: BPU page loaded.")
            page.screenshot(path="verify_bpu.png")

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
        # print("Server Output:\n", stdout.decode())
        if stderr:
            print("Server Errors:\n", stderr.decode())

if __name__ == "__main__":
    success = verify_app()
    if not success:
        sys.exit(1)
