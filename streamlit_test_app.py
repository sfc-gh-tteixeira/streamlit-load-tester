# Copyright (c) Snowflake Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import util

import streamlit as st

USER_INDEX = getattr(st.query_params, "user_index", -1)
NUM_USERS = int(getattr(st.query_params, "num_users", 1))
USER_ARRIVAL_STYLE = getattr(st.query_params, "user_arrival_style", "spread_out")
WRITE_TO_FILE = getattr(st.query_params, "write_to_file", False)
COMPUTATION = getattr(st.query_params, "computation", None)
NUM_MULTIPLICATIONS = int(getattr(st.query_params, "num_multiplications", 1))
NUM_STUFF_TO_DRAW = int(getattr(st.query_params, "num_stuff_to_draw", 100))
SLEEP_TIME_BETWEEN_MULTIPLICATIONS = float(
    getattr(st.query_params, "sleep_time_between_multiplications", 0))
THREAD_POOL_LIMITS = int(getattr(st.query_params, "thread_pool_limits", -1))
MULTIPLICATION_EXECUTION_MODE = getattr(st.query_params, "multiplication_execution_mode", "base")

def write_func(out, also_print=False):
    st.write(out)
    if also_print:
        print(out, flush=True)

multiplication_executor = None

if MULTIPLICATION_EXECUTION_MODE == "processpool":
    import concurrent.futures

    @st.cache_resource
    def get_executor():
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=101)

        print("Prewarming processes...")

        for i in range(NUM_USERS):
            fut = executor.submit(util.do_nothing)
            fut.result()

        print("Done prewarming!")

        return executor

    get_executor()

    def multiplication_executor(fn, /, *args, **kwargs):
        fut = get_executor().submit(fn, *args, **kwargs)
        fut.result() # Wait for result.


# Put the test behind a button click so we can better synchronize multiple
# concurrent users
if st.button("Run test"):
    util.run_test(
        experiment_name=f"streamlit-{MULTIPLICATION_EXECUTION_MODE}-{st.__version__}",
        write_func=write_func,
        user_index=USER_INDEX,
        num_users=NUM_USERS,
        user_arrival_style=USER_ARRIVAL_STYLE,
        num_stuff_to_draw=NUM_STUFF_TO_DRAW,
        computation=COMPUTATION,
        num_multiplications=NUM_MULTIPLICATIONS,
        sleep_time_between_multiplications=SLEEP_TIME_BETWEEN_MULTIPLICATIONS,
        thread_pool_limits=THREAD_POOL_LIMITS,
        multiplication_executor=multiplication_executor,
        write_to_file=False if WRITE_TO_FILE == "False" else WRITE_TO_FILE,
    )
