import glob
import io

import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

@st.cache_data(ttl="1d")
def read_data(filenames):
    all_lines = []

    for filename in filenames:
        with open(filename) as f:
            all_lines.extend(f.readlines())

        data_json_str = ",".join(all_lines)
        data_json_str = f"[{data_json_str}]"

    data = pd.read_json(io.StringIO(data_json_str))
    return data

_, col, _ = st.columns([1, 4, 1])

with col:
    """
    # :heart_on_fire: Load test results browser
    """

    files = sorted(glob.glob("*.txt"))
    filenames = st.multiselect("Pick files", files, default=files)
    data = None

    if filenames:
        data = read_data(filenames)

    if data is not None:
        data

    all_experiment_names = data.experiment_name.unique().tolist()
    all_num_multiplications = data.num_multiplications.unique().tolist()
    all_sleep_time = data.sleep_time_between_multiplications.unique().tolist()

    filtered_experiment_names = st.multiselect(
        "Experiment names", all_experiment_names, default=all_experiment_names)

if data is not None:
    filtered_data_0 = data[data.experiment_name.isin(filtered_experiment_names)]

    cols = st.columns(len(all_sleep_time))

    for i, sleep_time in enumerate(all_sleep_time):
        filtered_data_1 = filtered_data_0[
            data.sleep_time_between_multiplications == sleep_time]

        with cols[i]:
            for num_multiplications in all_num_multiplications:
                filtered_data_2 = filtered_data_1[
                    data.num_multiplications == num_multiplications]

                ""

                f"""
                ##### {num_multiplications}M mults, {sleep_time}s sleep
                """

                c = alt.Chart(
                    filtered_data_2,
                    height=300,
                ).encode(
                    x="num_users:Q",
                    color=alt.Color("experiment_name:N", legend=None),
                )

                st.altair_chart(
                    c.mark_point(size=50, shape="stroke", opacity=0.33, strokeWidth=1).encode(y="session_run_time:Q") +
                    c.mark_line().encode(y="median(session_run_time):Q") +
                    c.mark_point(size=50, filled=True).encode(y="median(session_run_time):Q", shape=alt.Shape("experiment_name:N", legend=None)),
                use_container_width=True)

