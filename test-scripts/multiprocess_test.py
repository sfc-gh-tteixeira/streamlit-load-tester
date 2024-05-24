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

import multiprocessing
import util

def run_test(
        num_users,
        user_arrival_style,
        num_stuff_to_draw,
        computation,
        num_multiplications,
        sleep_time_between_multiplications,
        write_to_file,
    ):
    """Run tasks using Python's multiprocessing.Process().
    """

    processes = []

    for i in range(num_users):
        process = multiprocessing.Process(
            target=util.run_test,
            kwargs=dict(
                experiment_name="python-multiprocess",
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

        process.start()
        processes.append(process)

    # Wait for everything to end before exiting.
    for process in processes:
        process.join()
