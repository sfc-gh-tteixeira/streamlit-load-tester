import multiprocessing
import util

def run_test(
        num_users,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):

    processes = []

    for i in range(num_users):
        process = multiprocessing.Process(
            target=util.run_test,
            kwargs=dict(
                experiment_name='python-multiprocess',
                write_func=print,
                num_stuff_to_draw=num_stuff_to_draw,
                computation=computation,
                num_multiplications=num_multiplications,
                sleep_time_between_multiplications=sleep_time_between_multiplications,
                thread_pool_limits=1,
                num_users=num_users,
                user_index=i,
                write_to_file=write_to_file,
            ),
        )
        process.start()
        processes.append(process)

    # Wait for everything to end before exiting.
    for process in processes:
        process.join()
