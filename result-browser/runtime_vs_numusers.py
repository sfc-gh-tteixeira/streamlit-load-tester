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
    """Shows line charts of runtime vs num users, with many controls."""

    filtered_experiment_names = st.multiselect(
        "Experiment types to include",
        sorted(data.all_experiment_names),
        default=data.all_experiment_names,
        key=f"names-{key}",
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

    normalize_run_times = st.toggle(
        "Normalize run times to fastest",
        key=f"normalize-{key}",
    )

    if data is not None:
        exper = data.experiments
        filtered_exper_0 = exper[
            (exper.experiment_name.isin(filtered_experiment_names)) &
            (exper.user_arrival_style == selected_arrival_style) &
            (exper.sleep_time_between_multiplications == selected_sleep_time)
        ]

        run_time_units = "s"

        if normalize_run_times:
            filtered_exper_0.session_run_time /= filtered_exper_0.session_run_time.min()
            run_time_units = "normalized"

        all_computations = filtered_exper_0.computation.unique().tolist()
        all_num_stuff_to_draw = filtered_exper_0.num_stuff_to_draw.unique().tolist()

        st.write("")
        st.write("")

        for curr_num_multiplications in data.all_num_multiplications:
            filtered_exper_1 = filtered_exper_0[
                filtered_exper_0.num_multiplications == curr_num_multiplications]

            st.write(f"""
                #### {curr_num_multiplications}M multiplications
            """)

            st.write("")

            selection = alt.selection_multi(
                fields=["experiment_name"],
                bind="legend",
            )

            c = alt.Chart(
                filtered_exper_1,
                height=300,
            ).encode(
                x=alt.X("num_users:Q", title="Number of users"),
                y=alt.Y("median(session_run_time):Q", title=f"Session run time ({run_time_units})"),
                color=alt.Color(
                    "experiment_name:N",
                    title="Experiment name",
                    legend=alt.Legend(
                        title=None,
                        orient="top-left",
                        symbolType="stroke",
                        symbolOpacity=1,
                        symbolStrokeWidth=2,
                    ),
                ),
            )

            st.altair_chart(
                # Little ticks for each individual experiment.
                c.mark_point(size=50, filled=True).encode(
                    y=alt.Y("session_run_time:Q"),
                    opacity=alt.condition(selection, alt.value(0.125), alt.value(0.0)),
                ) +

                # Lines going through the median points.
                c.mark_line(strokeWidth=2).encode(
                    opacity=alt.condition(selection, alt.value(1.0), alt.value(0.0)),
                ).add_selection(selection) +

                # Points on top of the lines, showing the median.
                c.mark_point(size=50, filled=True).encode(
                    shape=alt.Shape("experiment_name:N", title="Experiment name", legend=None),
                    opacity=alt.condition(selection, alt.value(1.0), alt.value(0.0)),
                ),
            use_container_width=True)

            if not comparison_mode:
                comparison_keys = []
                for curr_computation in all_computations:
                    for curr_num_stuff_to_draw in all_num_stuff_to_draw:
                        comparison_keys.append(util.AnnotationKey(
                            analysis_type="timeseries",
                            computation=curr_computation,
                            num_multiplications=curr_num_multiplications,
                            num_stuff_to_draw=curr_num_stuff_to_draw,
                            num_users=None,
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
