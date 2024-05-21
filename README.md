# Streamlit load tester

This repo contains two things:

1. **test.py:** A load-testing script that compares Streamlit's handling of concurrent users against
   how Python handles concurrent tasks when Streamlit is not involved. This script runs lots of
   experiments and writes the results to `data/`.

2. **result_browser.py:** A Streamlit app that reads the results stored in the `data/` folder and shows
   them in an easy-to-use UI.


## Browsing official results

If you just want to look at the results of these load tests, you can find them at:

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

1. Let's define a "task" as:
    1. Drawing 100 strings (`num_stuff_to_draw` variable)
    2. Followed by performing between 1M and 1B multiplications of random numbers, either as numbers
       or as matrices (`num_multiplications` and `computation` variables)
    3. ...where you can optionally sleep for 0-0.1s after every few multiplications
       (`sleep_time_between_multiplications`).

2. Then for each type of test described in item 3 below we run the task above 1-50 times concurrently
   (`num_users`).
   
   Tasks are either started all at once or spread out over a 1s interval (`user_arrival_style`).

4. We do this for each of 5 test types:
    - `streamlit_test.py :: run_base_test()`

       This starts a Streamlit app that runs the task above every time a user opens a tab and presses
       "Run test", and then records how long it takes. Then it opens up a headless browser via
       Playwright with a new tab pointing to Streamlit for each of the 1-50 concurrent users we'd
       like to simulate. Once every tab loads, the test clicks "Run test" either all at once or spread
       out over 1s.

    - `streamlit_test.py :: run_processpool_test()`

       This is the same as the test above, but in this case the Streamlit app runs the task inside a
       `ProcessPoolExecutor`, so the heavy lifting is done outside the Streamlit server process and
       in a whole separate Python process (1 process per task). This simulates the best-practice for
       Streamlit apps that perform heavy non-cacheable computations.

    - `threads_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new threads running the task from item 1 above. When
       each thread is done, it records how long the task ran for.

    - `processpool_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new processes running the task from item 1 above with
       a `ProcessPoolExecutor`. When each process is done, it records how long it ran for.

    - `multiprocess_test.py :: run_test()`

       This runs a `for` loop that starts 1-50 new processes running the task from item 1 above with
       `multiprocessing.Process()`. When each process is done, it records how long it ran for.

       (NOTE: We don't include the data for this last test in our official results because they match
       the `ProcessPoolExecutor` results, and therefore just make the official results harder to read)
