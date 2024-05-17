import contextlib
import datetime
import json
import random
import time

import numpy
import threadpoolctl

MATRIX_WIDTH = 1000
MATRIX_HEIGHT = 1000

def now():
    return datetime.datetime.now().isoformat()

def do_nothing():
    pass

@contextlib.contextmanager
def no_context_manager():
    yield


def sleep_between_users(user_arrival_style, num_users, user_number):
    sleep_time = 0

    if user_number == 0:
        sleep_time = 0

    elif user_arrival_style == "together":
        sleep_time = 0

    elif user_arrival_style == "spread_out":
        sleep_time = 1.0 / num_users

    else:
        raise ValueError(f"Illegal {user_arrival_style=}")

    time.sleep(sleep_time)

def multiply_matrices(num_multiplications, sleep_time_between_multiplications, thread_pool_limits):
    if thread_pool_limits < 1:
        context_manager = no_context_manager()
    else:
        context_manager = threadpoolctl.threadpool_limits(
            limits=thread_pool_limits, user_api="blas")

    with context_manager:
        for i in range(0, num_multiplications):

            # Some random computation
            arr1 = numpy.random.rand(MATRIX_WIDTH, MATRIX_HEIGHT)
            arr2 = numpy.random.rand(MATRIX_WIDTH, MATRIX_HEIGHT)
            arr3 = arr1 @ arr2

            if sleep_time_between_multiplications > 0:
                time.sleep(sleep_time_between_multiplications)

def multiply_numbers(num_multiplications, sleep_time_between_multiplications, thread_pool_limits):
    for i in range(0, num_multiplications):

        # Some random computation
        for _ in range(MATRIX_WIDTH):
            x = random.random()
            for _ in range(MATRIX_HEIGHT):
                y = random.random()
                b = x * y

        if sleep_time_between_multiplications > 0:
            time.sleep(sleep_time_between_multiplications)

def run_test(
        experiment_name=None,
        write_func=lambda x, also_print=False: print(x, flush=True),
        user_index=-1, # Only used for display and save_results
        num_users=1, # Only used in save_results
        user_arrival_style=None, # Only used in save_results
        num_stuff_to_draw=100,
        computation="multiply_numbers",
        num_multiplications=1,
        sleep_time_between_multiplications=0,
        multiplication_executor=None,
        thread_pool_limits=-1,
        write_to_file=False,
    ):

    t0 = time.time()
    write_func(f"Loaded! ({user_index})", also_print=True)

    for i in range(num_stuff_to_draw):
        write_func(f"Drawing some stuff {i}")

    write_func(f"Wrote stuff ({user_index})")

    if computation == "multiply_numbers":
        computation_func = multiply_numbers
    elif computation == "multiply_matrices":
        computation_func = multiply_matrices
    else:
        raise ValueError(f"Illegal value of {computation=}")

    if multiplication_executor:
        multiplication_executor(
            computation_func, num_multiplications, sleep_time_between_multiplications,
            thread_pool_limits)
    else:
        computation_func(
            num_multiplications, sleep_time_between_multiplications, thread_pool_limits)

    write_func(f"Done! ({user_index})")
    t1 = time.time()

    delta = t1 - t0
    write_func(f"Time ({user_index}) {delta}", also_print=True)

    if write_to_file:
        save_results(
            filename=write_to_file,
            experiment_name=experiment_name,
            user_index=user_index,
            num_users=num_users,
            user_arrival_style=user_arrival_style,
            num_stuff_to_draw=num_stuff_to_draw,
            computation=computation,
            num_multiplications=num_multiplications,
            sleep_time_between_multiplications=sleep_time_between_multiplications,
            thread_pool_limits=thread_pool_limits,
            session_run_time=delta,
            current_time=now(),
        )

def save_results(filename, **kwargs):
    with open(filename, "a") as f:
        f.write(json.dumps(kwargs))
        f.write("\n")
        f.flush()
