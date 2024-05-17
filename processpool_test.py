import concurrent.futures
import util
import time

def do_nothing():
    pass

def run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):
    """Run tasks using Python's ProcessPoolExecutor().
    """

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_users) as executor:
        # Prewarm the processes.
        for i in range(num_users):
            util.sleep_between_users(user_arrival_style, num_users, i)
            fut = executor.submit(do_nothing)
            fut.result()

        for i in range(num_users):
            executor.submit(
                util.run_test,
                experiment_name="python-processpool",
                user_index=i,
                num_users=num_users,
                user_arrival_style=user_arrival_style,
                num_stuff_to_draw=num_stuff_to_draw,
                computation=computation,
                num_multiplications=num_multiplications,
                sleep_time_between_multiplications=sleep_time_between_multiplications,
                thread_pool_limits=1,
                write_to_file=write_to_file,
            )

        # Wait for everything to end before exiting.
        executor.shutdown(wait=True)
