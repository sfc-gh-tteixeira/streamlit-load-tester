import collections
import glob
import io
import json
import pathlib

import streamlit as st
import pandas as pd
import altair as alt


@st.cache_data(ttl="1d")
def read_data(experiment_filenames):
    all_lines = []

    for experiment_filename in experiment_filenames:
        with open(experiment_filename) as f:
            all_lines.extend(f.readlines())

        # In my janky "rowjson" format, every line is a json dict. So in order to read it as json I
        # need to add commas between lines and wrap the whole thing in an array.
        data_json_str = ",".join(all_lines)
        data_json_str = f"[{data_json_str}]"

    data = pd.read_json(io.StringIO(data_json_str))
    return data


@st.cache_data(ttl="1d")
def read_annotations(experiment_filenames):
    all_annotations = collections.defaultdict(list)

    for experiment_filename in experiment_filenames:
        # Annotation files have the same name as the corresponding experiment file,
        # but the extension is .annotation.json instead of .rowjson .
        annotation_filename = (
            pathlib.Path(experiment_filename).with_suffix(".annotations.json"))

        if not annotation_filename.exists():
            continue

        with open(annotation_filename) as f:
            experiment_annotations = json.load(f)

        for annot in experiment_annotations:
            key_tuple = AnnotationKey(
                computation=annot["computation"],
                num_multiplications=annot["num_multiplications"],
                num_stuff_to_draw=annot["num_stuff_to_draw"],
                sleep_time_between_multiplications=annot["sleep_time_between_multiplications"],
                user_arrival_style=annot["user_arrival_style"],
            )

            all_annotations[key_tuple].append(annot["annotation"])

    return all_annotations


AnnotationKey = collections.namedtuple(
    "AnnotationKey",
    [
        "computation",
        "num_multiplications",
        "num_stuff_to_draw",
        "sleep_time_between_multiplications",
        "user_arrival_style",
    ],
)


"""
# :heart_on_fire: Load test results browser
"""

files = sorted(glob.glob("data/*.rowjson"))
filenames = st.multiselect("Pick files", files, default=files[-1])
data = None

if filenames:
    data = read_data(filenames)
    annotations = read_annotations(filenames)

if data is not None:
    data


""

"""
## Filter
"""

all_experiment_names = data.experiment_name.unique().tolist()
all_num_multiplications = data.num_multiplications.unique().tolist()
all_sleep_times = data.sleep_time_between_multiplications.unique().tolist()
all_arrival_styles = data.user_arrival_style.unique().tolist()

filtered_experiment_names = st.multiselect(
    "Experiment types to include", all_experiment_names, default=all_experiment_names)

selected_arrival_style = st.radio(
    "How do users arrive", all_arrival_styles,
    horizontal=True)

selected_sleep_time = st.radio(
    "Sleep time between every million multiplications (seconds)", sorted(all_sleep_times),
    horizontal=True)

if data is not None:
    ""
    ""

    """
    ## Results
    """

    filtered_data_0 = data[
        (data.experiment_name.isin(filtered_experiment_names)) &
        (data.user_arrival_style == selected_arrival_style) &
        (data.sleep_time_between_multiplications == selected_sleep_time)
    ]

    normalize_run_times = st.toggle("Normalize to fastest number")
    run_time_units = "s"

    if normalize_run_times:
        filtered_data_0.session_run_time /= filtered_data_0.session_run_time.min()
        run_time_units = "normalized"

    all_computations = filtered_data_0.computation.unique().tolist()
    all_num_stuff_to_draw = filtered_data_0.num_stuff_to_draw.unique().tolist()

    for curr_num_multiplications in all_num_multiplications:
        filtered_data_1 = filtered_data_0[
            data.num_multiplications == curr_num_multiplications]

        ""

        f"""
        #### {curr_num_multiplications}M multiplications
        """

        c = alt.Chart(
            filtered_data_1,
            height=300,
        ).encode(
            x=alt.X("num_users:Q", title="Number of users"),
            y=alt.Y("median(session_run_time):Q", title=f"Session run time ({run_time_units})"),
            color=alt.Color(
                "experiment_name:N",
                title=None,
                legend=alt.Legend(
                    orient="top-left",
                    symbolType="stroke",
                    symbolOpacity=1,
                    symbolStrokeWidth=2,
                ),
            ),
        )

        st.altair_chart(
            # Little ticks for each individual experiment.
            c.mark_point(size=50, shape="stroke", opacity=0.33, strokeWidth=1).encode(
                y="session_run_time:Q",
            ) +

            # Lines going through the median points.
            c.mark_line(strokeWidth=2) +

            # Points on top of the lines, showing the median.
            c.mark_point(size=50, filled=True).encode(
                shape=alt.Shape("experiment_name:N", legend=None),
            ),
        use_container_width=True)

        for curr_computation in all_computations:
            for curr_num_stuff_to_draw in all_num_stuff_to_draw:
                comparison_key = AnnotationKey(
                    computation=curr_computation,
                    num_multiplications=curr_num_multiplications,
                    num_stuff_to_draw=curr_num_stuff_to_draw,
                    sleep_time_between_multiplications=selected_sleep_time,
                    user_arrival_style=selected_arrival_style,
                )

        for annot in annotations[comparison_key]:
            st.caption(annot)

        ""
