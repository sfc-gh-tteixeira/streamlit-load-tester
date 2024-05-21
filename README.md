# Streamlit load tester

This repo contains two things:

1. **test.py:** A load-testing script that compares Streamlit's handling of concurrent users against
   how Python handles concurrent tasks (when Streamlit is not involved). This script runs lots of
   experiments and writes the results to `data/`.

2. **result_browser.py:** A Strealmit app that reads the results from `data/` and shows them in
   an easy-to-use UI.


## Browsing official results

If you just want to look at the results of these load-tests, you can find them at:

https://load-tests.streamlit.app


## Running the load tests yourself

1. Install requirements:

   ```sh
   $ pip install -r requirements.txt
   ```

2. Start the tests:

   ```sh
   $ python test.py
   ```

3. Go fly a kite. The results will be ready in ~24-48h.

   The script from (2) will save a file of type `.rowjson` in `data/`. Those are your test results.


## Running the result browser app

1. Install requirements if you haven't done so already:

   ```sh
   $ pip install -r requirements.txt
   ```

2. Start the app:

   ```sh
   $ streamlit run result_browser.py
   ```

## How the load test works

The load test consists of:

1. Let's define a "task" as:
    1. Drawing 100 strings (`num_stuff_to_draw` variable)
    2. Followed by performing between 1M and 1B multiplications of random numbers, either as numbers
       or as matrices (`num_multiplications` and `computation` variables)
    3. ...where you can optionally sleep for 0-0.1s after every few multiplications
       (`sleep_time_between_multiplications`).

2. Then for each test type below we run the task above 1-50 times concurrently (`num_users`).
    - Tasks are either started all at once or spread out over a 1s interval (`user_arrival_style`).

3. We do this for each of 5 test types:
    - `streamlit_test.py :: run_base_test()`

       This runs a Streamlit app that runs the task above every time a user opens a tab and presses
       "start", and then records how long it takes. Then it opens up a headless browser via
       Playwright with a new tab pointing to Streamlit for each of the 1-50 concurrent users we'd
       like to simluate. Once every tab loads, the test clicks "start" either all at once or spread
       out over 1s.

    - `streamlit_test.py :: run_processpool_test()`

       This is the same as the test above, but in this the Streamlit app runs the task inside a
       `ProcessPoolExecutor`, so they heavy lifting is done outside the Streamlit server process and
       in a whole separate Python process (1 process per task).

    - `threads_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new threads running the task above. When each thread
       is done, it writes it records how long it ran for.

    - `processpool_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new processes running the task above (using a
       `ProcessPoolExecutor`). When each process is done, it writes it records how long it ran for.

    - `multiprocess_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new processes running the task above (using
       `multiprocessing.Process()`). When each process is done, it writes it records how long it ran
       for.

       (NOTE: We don't include the data for this in our official results because they match the
       `ProcessPoolExecutor` results, and therefore just make the official results harder to read)
