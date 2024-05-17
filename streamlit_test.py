import contextlib
import re
import urllib
import subprocess
from playwright.sync_api import sync_playwright, expect

import util

STREAMLIT_PORT = 8500
LONG_TIMEOUT_MS = 60 * 60 * 24 * 1000

def load_page(page, **query_params):
    query_params_str = urllib.parse.urlencode(query_params, doseq=False)
    page.goto(f"http://localhost:{STREAMLIT_PORT}?{query_params_str}", timeout=LONG_TIMEOUT_MS)

def check_is_ready(page):
    button_locator = page.locator("[data-testid=baseButton-secondary]")
    expect(button_locator).to_be_visible(timeout=LONG_TIMEOUT_MS)
    return button_locator

def check_is_done(page):
    locator = page.locator("body")
    expect(locator).to_have_text(re.compile("Done!"), timeout=LONG_TIMEOUT_MS)

@contextlib.contextmanager
def get_playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        try:
            yield context
        finally:
            context.close()

def run_base_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):
    """Run tasks in different Streamlit user sessions.
    """
    _run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        thread_pool_limits=-1,
        multiplication_execution_mode="base",
        write_to_file=write_to_file,
    )

def run_processpool_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):
    """Run tasks in a ProcessPoolExecutor(), started from different Streamlit user sessions.
    """
    _run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        thread_pool_limits=1,
        multiplication_execution_mode="processpool",
        write_to_file=write_to_file,
    )

def _run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        thread_pool_limits,
        multiplication_execution_mode,
        write_to_file,
    ):

    streamlit_process = subprocess.Popen([
       "streamlit", "run", "streamlit_test_app.py",
        "--server.headless=true",
        f"--server.port={STREAMLIT_PORT}",
    ])

    try:
        with get_playwright_context() as context:
            for i in range(num_users):
                context.new_page()

            for i in range(num_users):
                load_page(
                    page=context.pages[i],
                    user_index=i,
                    num_users=num_users,
                    user_arrival_style=user_arrival_style,
                    num_stuff_to_draw=num_stuff_to_draw,
                    computation=computation,
                    num_multiplications=num_multiplications,
                    sleep_time_between_multiplications=sleep_time_between_multiplications,
                    thread_pool_limits=thread_pool_limits,
                    multiplication_execution_mode=multiplication_execution_mode,
                    write_to_file=write_to_file,
                )

            button_locators = []

            for i in range(num_users):
                button_locators.append(check_is_ready(context.pages[i]))

            for i, button_locator in enumerate(button_locators):
                button_locator.click()
                util.sleep_between_users(user_arrival_style, num_users, i)

            for i in range(num_users):
                check_is_done(context.pages[i])

    finally:
        streamlit_process.terminate()
        streamlit_process.wait(30) # Some absurdly long time.
