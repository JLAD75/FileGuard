from playwright.sync_api import sync_playwright, Page, expect
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to the home page (which is the login/register page)
    page.goto("http://localhost:3000/")

    # Register a new user
    register_tab = page.get_by_role("tabpanel", name="Register")
    page.get_by_role("tab", name="Register").click()
    register_tab.get_by_label("Email").fill("test.user@example.com")
    register_tab.get_by_label("Password").first.fill("Password123!")
    register_tab.get_by_label("Confirm Password").fill("Password123!")
    register_tab.get_by_label("I accept terms and conditions").check()
    register_tab.get_by_role("button", name="Register").click()

    # Wait for the registration success notification
    expect(page.get_by_text("Registration successful")).to_be_visible(timeout=10000)

    # Log in
    login_tab = page.get_by_role("tabpanel", name="Login")
    login_tab.get_by_label("Email").fill("test.user@example.com")
    login_tab.get_by_label("Password").fill("Password123!")
    login_tab.get_by_role("button", name="Sign in").click()

    # Wait for the login success notification and navigation
    expect(page.get_by_text("Login successful")).to_be_visible()
    expect(page).to_have_url("http://localhost:3000/dashboard")

    # Verify the dashboard is displayed correctly
    expect(page.get_by_role("heading", name="My Files")).to_be_visible()
    expect(page.get_by_text("Drag files here or click to select files")).to_be_visible()
    expect(page.get_by_role("heading", name="All Files")).to_be_visible()

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/dashboard.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)