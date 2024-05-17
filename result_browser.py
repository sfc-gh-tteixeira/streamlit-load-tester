import glob
import io

import streamlit as st
import pandas as pd
import altair as alt


@st.cache_data(ttl="1d")
def read_data(filenames):
    all_lines = []

    for filename in filenames:
        with open(filename) as f:
            all_lines.extend(f.readlines())

        # In my janky "rowjson" format, every line is a json dict. So in order to read it as json I
        # need to add commas between lines and wrap the whole thing in an array.
        data_json_str = ",".join(all_lines)
        data_json_str = f"[{data_json_str}]"

    data = pd.read_json(io.StringIO(data_json_str))
    return data


"""
# :heart_on_fire: Load test results browser
"""

files = sorted(glob.glob("data/*.rowjson"))
filenames = st.multiselect("Pick files", files, default=files[-1])
data = None

if filenames:
    data = read_data(filenames)

if data is not None:
    data

"""
## Filter
"""

all_experiment_names = data.experiment_name.unique().tolist()
all_num_multiplications = data.num_multiplications.unique().tolist()
all_sleep_times = data.sleep_time_between_multiplications.unique().tolist()
all_arrival_styles = data.user_arrival_style.unique().tolist()

filtered_experiment_names = st.multiselect(
    "Experiment names", all_experiment_names, default=all_experiment_names)

arrival_style = st.radio(
    "User arrival style", all_arrival_styles,
    horizontal=True)

sleep_time = st.radio(
    "Sleep time between multiplications (seconds)", sorted(all_sleep_times),
    horizontal=True)

if data is not None:
    ""

    """
    ## Results
    """

    filtered_data_0 = data[
        (data.experiment_name.isin(filtered_experiment_names)) &
        (data.user_arrival_style == arrival_style) &
        (data.sleep_time_between_multiplications == sleep_time)
    ]

    for num_multiplications in all_num_multiplications:
        filtered_data_1 = filtered_data_0[
            data.num_multiplications == num_multiplications]

        ""

        f"""
        ##### {num_multiplications}M mults, {sleep_time}s sleep
        """

        c = alt.Chart(
            filtered_data_1,
            height=300,
        ).encode(
            x="num_users:Q",
            color=alt.Color("experiment_name:N", legend=None),
        )

        st.altair_chart(
            # Little ticks for each individual experiment.
            c.mark_point(size=50, shape="stroke", opacity=0.33, strokeWidth=1).encode(y="session_run_time:Q") +

            # Lines going through the median points.
            c.mark_line().encode(y="median(session_run_time):Q") +

            # Points on top of the lines, showing the median.
            c.mark_point(size=50, filled=True).encode(y="median(session_run_time):Q", shape=alt.Shape("experiment_name:N", legend=None)),
        use_container_width=True)
