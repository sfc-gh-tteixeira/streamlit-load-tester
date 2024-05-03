import concurrent.futures
import util
import time

def do_nothing():
    pass

def run_test(
        num_users,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_users) as executor:
        # Prewarm the processes.
        for i in range(num_users):
            fut = executor.submit(do_nothing)
            fut.result()

        for i in range(num_users):
            executor.submit(
                util.run_test,
                experiment_name='python-processpool',
                write_func=print,
                num_stuff_to_draw=num_stuff_to_draw,
                computation=computation,
                num_multiplications=num_multiplications,
                sleep_time_between_multiplications=sleep_time_between_multiplications,
                thread_pool_limits=1,
                num_users=num_users,
                user_index=i,
                write_to_file=write_to_file,
            )

        # Wait for everything to end before exiting.
        executor.shutdown(wait=True)
