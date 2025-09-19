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

import collections
import io
import json
import pathlib
import types

import streamlit as st
import pandas as pd

import runtime_shootout
import runtime_vs_numusers
import util

st.set_page_config(
    page_title="Load test results browser",
    page_icon=":fire:",
    layout="wide",
)

_, col, _ = st.columns([1, 2, 1])

with col:
    """
    # :fire: Load test results browser
    """

    ""

    # Get experiment files and make their names readable.
    data_folder = pathlib.Path(__file__).parent / "../data"
    file_paths = sorted(data_folder.glob("*.rowjson"))
    names_to_paths = {f.name: f for f in file_paths}
    file_names = list(names_to_paths.keys())

    selected_file_names = st.multiselect(
        "Result files", file_names, default=file_names[-1]
    )
    selected_file_paths = [data_folder / f for f in selected_file_names]

    data = None

    if selected_file_paths:
        experiments = util.read_data(selected_file_paths)

        data = types.SimpleNamespace(
            experiments=experiments,
            annotations=util.read_annotations(selected_file_paths),
            all_num_users=experiments.num_users.unique().tolist(),
            all_experiment_names=experiments.experiment_name.unique().tolist(),
            all_num_multiplications=experiments.num_multiplications.unique().tolist(),
            all_sleep_times=experiments.sleep_time_between_multiplications.unique().tolist(),
            all_arrival_styles=experiments.user_arrival_style.unique().tolist(),
        )

    ""

    if "analysis_type" not in st.session_state:
        st.session_state.analysis_type = None

    ANALYSIS_OPTIONS = {
        ":gun: Shootout": runtime_shootout,
        ":chart_with_upwards_trend: Time series": runtime_vs_numusers,
    }

    selection = st.pills(
        "Analysis type",
        options=ANALYSIS_OPTIONS.keys(),
        default=list(ANALYSIS_OPTIONS.keys())[0],
    )

    st.session_state.analysis_type = ANALYSIS_OPTIONS[selection].draw

    if st.session_state.analysis_type:
        comparison_mode = st.toggle("Turn on comparison mode")
    ""


if st.session_state.analysis_type:
    ""
    ""

    if comparison_mode:
        cols = st.columns(2)

        with cols[0]:
            st.session_state.analysis_type(data, comparison_mode, key=0)

        with cols[1]:
            st.session_state.analysis_type(data, comparison_mode, key=1)
    else:
        _, col, _ = st.columns([1, 2, 1])

        with col:
            st.session_state.analysis_type(data, comparison_mode, key=0)
