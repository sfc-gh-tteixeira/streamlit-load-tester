import threading
import util

import time

def run_test(
        num_users,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):

    threads = []

    for i in range(num_users):
        thread = threading.Thread(
            target=util.run_test,
            kwargs=dict(
                experiment_name='python-threads',
                write_func=print,
                num_stuff_to_draw=num_stuff_to_draw,
                computation=computation,
                num_multiplications=num_multiplications,
                sleep_time_between_multiplications=sleep_time_between_multiplications,
                thread_pool_limits=-1,
                num_users=num_users,
                user_index=i,
                write_to_file=write_to_file,
            ),
        )
        thread.start()
        threads.append(thread)

    # Wait for everything to end before exiting.
    for thread in threads:
        thread.join()
