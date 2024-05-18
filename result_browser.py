import collections
import glob
import io
import json
import pathlib

import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(
    page_title="Load test results browser",
    page_icon=":heart_on_fire:",
    layout="wide",
)

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


def runtime_x_users(id, comparison_mode=False):
    all_experiment_names = data.experiment_name.unique().tolist()
    all_num_multiplications = data.num_multiplications.unique().tolist()
    all_sleep_times = data.sleep_time_between_multiplications.unique().tolist()
    all_arrival_styles = data.user_arrival_style.unique().tolist()

    """
    ## Session run time vs. number of users
    """

    filtered_experiment_names = st.multiselect(
        "Experiment types to include",
        sorted(all_experiment_names),
        default=all_experiment_names,
        key=f"names-{id}",
    )

    selected_arrival_style = st.radio(
        "How do users arrive",
        sorted(all_arrival_styles, reverse=True),
        horizontal=True,
        key=f"style-{id}",
    )

    selected_sleep_time = st.radio(
        "Sleep time between every million multiplications (seconds)",
        sorted(all_sleep_times),
        horizontal=True,
        key=f"sleep-{id}",
    )

    ""
    ""

    normalize_run_times = st.toggle(
        "Normalize run times to fastest",
        key=f"normalize-{id}",
    )

    if data is not None:
        filtered_data_0 = data[
            (data.experiment_name.isin(filtered_experiment_names)) &
            (data.user_arrival_style == selected_arrival_style) &
            (data.sleep_time_between_multiplications == selected_sleep_time)
        ]

        run_time_units = "s"

        if normalize_run_times:
            filtered_data_0.session_run_time /= filtered_data_0.session_run_time.min()
            run_time_units = "normalized"

        all_computations = filtered_data_0.computation.unique().tolist()
        all_num_stuff_to_draw = filtered_data_0.num_stuff_to_draw.unique().tolist()

        ""
        ""

        for curr_num_multiplications in all_num_multiplications:
            filtered_data_1 = filtered_data_0[
                data.num_multiplications == curr_num_multiplications]

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

            if not comparison_mode:
                comparison_keys = []
                for curr_computation in all_computations:
                    for curr_num_stuff_to_draw in all_num_stuff_to_draw:
                        comparison_keys.append(AnnotationKey(
                            computation=curr_computation,
                            num_multiplications=curr_num_multiplications,
                            num_stuff_to_draw=curr_num_stuff_to_draw,
                            sleep_time_between_multiplications=selected_sleep_time,
                            user_arrival_style=selected_arrival_style,
                        ))

                annots = []
                for comparison_key in comparison_keys:
                    for annot in annotations[comparison_key]:
                        annots.append(annot)

                if annots:
                    st.caption("\n\n".join(annots))

                    ""
                    ""

def runtime_shootout(id, comparison_mode):
    all_num_users = data.num_users.unique().tolist()
    all_experiment_names = data.experiment_name.unique().tolist()
    all_num_multiplications = data.num_multiplications.unique().tolist()
    all_sleep_times = data.sleep_time_between_multiplications.unique().tolist()
    all_arrival_styles = data.user_arrival_style.unique().tolist()

    selected_num_multiplications = st.radio(
        "Number of multiplications, in millions (i.e. how complex are your app's calculations?)",
        ["include all", *sorted(all_num_multiplications)],
        horizontal=True,
        key=f"mult-{id}",
    )

    selected_arrival_style = st.radio(
        "How do users arrive",
        ["include all", *sorted(all_arrival_styles, reverse=True)],
        horizontal=True,
        key=f"style-{id}",
    )

    selected_sleep_time = st.radio(
        "Sleep time between every million multiplications (seconds)",
        ["include all", *sorted(all_sleep_times)],
        horizontal=True,
        key=f"sleep-{id}",
    )

    ""
    ""

    filtered_data_0 = data

    if selected_num_multiplications != "include all":
        filtered_data_0 = filtered_data_0[
            filtered_data_0.num_multiplications == selected_num_multiplications]

    if selected_arrival_style != "include all":
        filtered_data_0 = filtered_data_0[
            filtered_data_0.user_arrival_style == selected_arrival_style]

    if selected_sleep_time != "include all":
        filtered_data_0 = filtered_data_0[
            filtered_data_0.sleep_time_between_multiplications == selected_sleep_time]

    for curr_num_users in all_num_users:
        f"### {curr_num_users} concurrent users"

        filtered_data_1 = filtered_data_0[filtered_data_0.num_users == curr_num_users]
        #filtered_data_1.session_run_time /= filtered_data_1.session_run_time.min()

        st.altair_chart(
            alt.Chart(filtered_data_1).mark_bar().encode(
                x=alt.X("median(session_run_time):Q", title="Median run time (s)"),
                y=alt.Y("experiment_name:N", title=None),
                color=alt.Y("experiment_name:N", legend=None),
            ),
            use_container_width=True,
        )

        ""


_, col, _ = st.columns([1, 2, 1])

with col:
    """
    # :heart_on_fire: Load test results browser
    """

    ""

    files = sorted(glob.glob("data/*.rowjson"))
    filenames = st.multiselect("Result files", files, default=files[-1])
    data = None

    if filenames:
        data = read_data(filenames)
        annotations = read_annotations(filenames)

    analysis_types = {
        "Session run time vs. number of users": runtime_x_users,
        "Runtime shootout": runtime_shootout,
    }

    analysis_type = analysis_types[st.selectbox("Analysis type", analysis_types.keys())]

    comparison_mode = st.toggle("Turn on comparison mode")

    ""
    ""

if comparison_mode:
    cols = st.columns(2)

    with cols[0]:
        analysis_type(0, comparison_mode)

    with cols[1]:
        analysis_type(1, comparison_mode)
else:
    _, col, _ = st.columns([1, 2, 1])

    with col:
        analysis_type(0, comparison_mode)
