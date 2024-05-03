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


def multiply_matrices(num_multiplications, sleep_time_between_multiplications, thread_pool_limits):
    if thread_pool_limits < 1:
        context_manager = no_context_manager()
    else:
        context_manager = threadpoolctl.threadpool_limits(
            limits=thread_pool_limits, user_api='blas')

    with context_manager:
        for i in range(0, num_multiplications):

            # Some random computation
            arr1 = numpy.random.rand(MATRIX_WIDTH, MATRIX_HEIGHT)
            arr2 = numpy.random.rand(MATRIX_WIDTH, MATRIX_HEIGHT)
            arr3 = arr1 @ arr2

            if i % (num_multiplications / 10) == 0:
                print(f'Iteration {i}!', flush=True)

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

        if i % (num_multiplications / 10) == 0:
            print(f'Iteration {i}!', flush=True)

        if sleep_time_between_multiplications > 0:
            time.sleep(sleep_time_between_multiplications)

def run_test(
        experiment_name=None,
        write_func=lambda x: print(x, flush=True),
        num_stuff_to_draw=100,
        computation="multiply numbers",
        num_multiplications=1,
        sleep_time_between_multiplications=0,
        multiplication_executor=None,
        thread_pool_limits=-1,
        num_users=1,
        user_index=-1,
        write_to_file=False,
    ):

    t0 = time.time()
    write_func(f'Loaded! ({user_index})')

    for i in range(num_stuff_to_draw):
        write_func(f'Drawing some stuff {i}')

    write_func(f'Wrote stuff ({user_index})')

    if computation == "multiply matrices":
        computation_func = multiply_matrices
    else:
        computation_func = multiply_numbers

    if multiplication_executor:
        multiplication_executor(
            computation_func, num_multiplications, sleep_time_between_multiplications,
            thread_pool_limits)
    else:
        computation_func(
            num_multiplications, sleep_time_between_multiplications, thread_pool_limits)

    write_func(f'Done! ({user_index})')
    t1 = time.time()

    delta = t1 - t0
    write_func(f'Time ({user_index}) {delta}')

    if write_to_file:
        save_results(
            filename=write_to_file,
            experiment_name=experiment_name,
            computation=computation,
            num_multiplications=num_multiplications,
            num_stuff_to_draw=num_stuff_to_draw,
            sleep_time_between_multiplications=sleep_time_between_multiplications,
            num_users=num_users,
            user_index=user_index,
            session_run_time=delta,
            current_time=now(),
        )

def save_results(filename, **kwargs):
    with open(filename, 'a') as f:
        f.write(json.dumps(kwargs))
        f.write('\n')
        f.flush()
