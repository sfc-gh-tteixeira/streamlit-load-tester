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

import streamlit as st
import altair as alt

import util


def draw(data, comparison_mode, key):
    """Shows runtime bar charts, with many controls."""

    selected_num_multiplications = st.radio(
        "Number of multiplications, in millions (i.e. how complex are your app's calculations?)",
        sorted(data.all_num_multiplications),
        horizontal=True,
        key=f"mult-{key}",
    )

    selected_arrival_style = st.radio(
        "How do users arrive",
        sorted(data.all_arrival_styles, reverse=True),
        horizontal=True,
        key=f"style-{key}",
    )

    selected_sleep_time = st.radio(
        "Sleep time between every million multiplications (seconds)",
        sorted(data.all_sleep_times),
        horizontal=True,
        key=f"sleep-{key}",
    )

    st.write("")
    st.write("")

    sort_by_winner = st.toggle(
        "Sort by winner",
        True,
        key=f"sort-{key}",
    )

    st.write("")
    st.write("")

    filtered_exper_0 = data.experiments

    filtered_exper_0 = filtered_exper_0[
        (filtered_exper_0.num_multiplications == selected_num_multiplications) &
        (filtered_exper_0.user_arrival_style == selected_arrival_style) &
        (filtered_exper_0.sleep_time_between_multiplications == selected_sleep_time)
    ]

    all_computations = filtered_exper_0.computation.unique().tolist()
    all_num_stuff_to_draw = filtered_exper_0.num_stuff_to_draw.unique().tolist()

    if sort_by_winner:
        sort_args = dict(sort="x")
    else:
        sort_args = {}

    for curr_num_users in data.all_num_users:
        st.write(f"""
            #### {curr_num_users} concurrent user{ 's' if curr_num_users > 1 else '' }
        """)

        st.write("")

        filtered_exper_1 = filtered_exper_0[filtered_exper_0.num_users == curr_num_users]

        c = alt.Chart(
            filtered_exper_1,
            height=40 * len(data.all_experiment_names),
        ).encode(
            y=alt.Y(
                "experiment_name:N",
                title="Experiment name",
                axis=alt.Axis(title=None),
                **sort_args),
            color=alt.Color(
                "experiment_name:N",
                title="Experiment name",
                legend=None,
            ),
        )

        st.altair_chart(
            c.mark_bar(opacity=0.667).encode(
                alt.X("median(session_run_time):Q", title="Median run time (s)"),
            ) +

            c.mark_point(size=20, filled=True, opacity=0.5).encode(
                alt.X("session_run_time:Q"),
                alt.YOffset("user_index:Q"),
            ),
            use_container_width=True,
        )

        if not comparison_mode:
            comparison_keys = []
            for curr_computation in all_computations:
                for curr_num_stuff_to_draw in all_num_stuff_to_draw:
                    comparison_keys.append(util.AnnotationKey(
                        analysis_type="shootout",
                        computation=curr_computation,
                        num_multiplications=selected_num_multiplications,
                        num_stuff_to_draw=curr_num_stuff_to_draw,
                        num_users=curr_num_users,
                        sleep_time_between_multiplications=selected_sleep_time,
                        user_arrival_style=selected_arrival_style,
                    ))

            curr_annots = []

            for comparison_key in comparison_keys:
                for annot in data.annotations[comparison_key]:
                    curr_annots.append(annot)


            if curr_annots:
                st.caption("\n\n".join(curr_annots))

                st.write("")
                st.write("")


