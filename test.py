import textwrap
import random

import util
import multiprocess_test
import processpool_test
import streamlit_test
import threads_test


COMPUTATION = ["multiply_numbers", "multiply_matrices"]
NUM_USERS = [1, 2, 5, 10, 25, 50]
USER_ARRIVAL_STYLE = ["together", "spread_out"]
NUM_STUFF_TO_DRAW = [100]
NUM_MULTIPLICATIONS = [1, 10, 100, 1000]
SLEEP_TIME_BETWEEN_MULTIPLICATIONS = [0, 0.001, 0.01]
WRITE_TO_FILE = f"data/test_results_{util.now()}.rowjson"

TESTS_TO_RUN = [
    processpool_test.run_test,
    streamlit_test.run_base_test,
    streamlit_test.run_processpool_test,
    threads_test.run_test,
    multiprocess_test.run_test,
]

if __name__ == "__main__":
    for computation in COMPUTATION:
        for num_multiplications in NUM_MULTIPLICATIONS:
            for num_users in NUM_USERS:
                for user_arrival_style in USER_ARRIVAL_STYLE:
                    for num_stuff_to_draw in NUM_STUFF_TO_DRAW:
                        for sleep_time_between_multiplications in SLEEP_TIME_BETWEEN_MULTIPLICATIONS:
                            for test_fn in random.sample(TESTS_TO_RUN, k=len(TESTS_TO_RUN)):
                                print(textwrap.dedent(f"""
                                    Running test:
                                    - test_fn={test_fn.__module__}.{test_fn.__qualname__}
                                    - {num_users=}
                                    - {user_arrival_style=}
                                    - {num_stuff_to_draw=}
                                    - {num_multiplications=}
                                    - {sleep_time_between_multiplications=}
                                    {util.now()}
                                """))

                                test_fn(
                                    num_users=num_users,
                                    user_arrival_style=user_arrival_style,
                                    num_stuff_to_draw=num_stuff_to_draw,
                                    computation=computation,
                                    num_multiplications=num_multiplications,
                                    sleep_time_between_multiplications=sleep_time_between_multiplications,
                                    write_to_file=WRITE_TO_FILE,
                                )
