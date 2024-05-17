import threading
import util
import time

def run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):
    """Run tasks using Python's threading.Thread().
    """

    threads = []

    for i in range(num_users):
        thread = threading.Thread(
            target=util.run_test,
            kwargs=dict(
                experiment_name="python-threads",
                user_index=i,
                num_users=num_users,
                user_arrival_style=user_arrival_style,
                num_stuff_to_draw=num_stuff_to_draw,
                computation=computation,
                num_multiplications=num_multiplications,
                sleep_time_between_multiplications=sleep_time_between_multiplications,
                thread_pool_limits=1,
                write_to_file=write_to_file,
            ),
        )
        util.sleep_between_users(user_arrival_style, num_users, i)
        thread.start()
        threads.append(thread)

    # Wait for everything to end before exiting.
    for thread in threads:
        thread.join()
