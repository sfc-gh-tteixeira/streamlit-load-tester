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

import streamlit as st
import pandas as pd


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
                analysis_type=annot["analysis_type"],
                computation=annot["computation"],
                num_multiplications=annot["num_multiplications"],
                num_stuff_to_draw=annot["num_stuff_to_draw"],
                num_users=annot["num_users"],
                sleep_time_between_multiplications=annot["sleep_time_between_multiplications"],
                user_arrival_style=annot["user_arrival_style"],
            )

            all_annotations[key_tuple].append(annot["annotation"])

    return all_annotations


AnnotationKey = collections.namedtuple(
    "AnnotationKey",
    [
        "analysis_type",
        "computation",
        "num_multiplications",
        "num_stuff_to_draw",
        "num_users",
        "sleep_time_between_multiplications",
        "user_arrival_style",
    ],
)
