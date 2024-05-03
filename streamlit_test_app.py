import streamlit as st
import util

# Only run the code below if not executing this in a separate process.
# if __name__ == '__main__':
USER_INDEX = getattr(st.query_params, 'user_index', -1)
NUM_USERS = int(getattr(st.query_params, 'num_users', 1))
WRITE_TO_FILE = getattr(st.query_params, 'write_to_file', False)
COMPUTATION = getattr(st.query_params, 'computation', None)
NUM_MULTIPLICATIONS = int(getattr(st.query_params, 'num_multiplications', 1))
NUM_STUFF_TO_DRAW = int(getattr(st.query_params, 'num_stuff_to_draw', 100))
SLEEP_TIME_BETWEEN_MULTIPLICATIONS = float(
    getattr(st.query_params, 'sleep_time_between_multiplications', 0))
THREAD_POOL_LIMITS = int(getattr(st.query_params, 'thread_pool_limits', -1))
MULTIPLICATION_EXECUTION_MODE = getattr(st.query_params, 'multiplication_execution_mode', 'base')

def write_func(out):
    print(out, flush=True)
    st.write(out)

multiplication_executor = None
if MULTIPLICATION_EXECUTION_MODE == 'ray':
    import ray
    # TODO

elif MULTIPLICATION_EXECUTION_MODE == 'processpool':
    import concurrent.futures

    @st.cache_resource
    def get_executor():
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=101)

        print('Prewarming processes...')

        for i in range(NUM_USERS):
            fut = executor.submit(util.do_nothing)
            fut.result()

        print('Done prewarming!')

        return executor

    get_executor()

    def multiplication_executor(fn, /, *args, **kwargs):
        fut = get_executor().submit(fn, *args, **kwargs)
        fut.result() # Wait for result.


# Put the test behind a button click so we can better synchronize multiple
# concurrent users
if st.button("Run test"):
    util.run_test(
        experiment_name=f'streamlit-{MULTIPLICATION_EXECUTION_MODE}-{st.__version__}',
        write_func=write_func,
        num_stuff_to_draw=NUM_STUFF_TO_DRAW,
        computation=COMPUTATION,
        num_multiplications=NUM_MULTIPLICATIONS,
        sleep_time_between_multiplications=SLEEP_TIME_BETWEEN_MULTIPLICATIONS,
        thread_pool_limits=THREAD_POOL_LIMITS,
        multiplication_executor=multiplication_executor,
        num_users=NUM_USERS,
        user_index=USER_INDEX,
        write_to_file=False if WRITE_TO_FILE == "False" else WRITE_TO_FILE,
    )
