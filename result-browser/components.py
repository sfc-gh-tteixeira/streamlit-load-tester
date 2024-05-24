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

import contextlib

import streamlit as st
import streamlit.components.v1 as components


@contextlib.contextmanager
def button_container(key=0):
    container = st.container(border=True)
    clicked = st.button("", key=f"--button-container-{key}")

    script("""
        const buttonContainer = parentNode.previousSibling
        const container = buttonContainer.previousSibling
        const button = buttonContainer.querySelector(":scope button")

        const styles = getComputedStyle(container)
        const textColor = styles.getPropertyValue("color")
        const bgColor = styles.getPropertyValue("background-color")

        container.addEventListener(
            "click",
            () => {
                const ev = new MouseEvent("click", {
                  view: window,
                  bubbles: true,
                  cancelable: true,
                })

                button.dispatchEvent(ev)
            })

        container.style.cursor = "pointer"

        container.addEventListener("mouseover", () => {
            container.style.backgroundColor = `color-mix(in srgb, ${textColor} 5%, ${bgColor})`
        })

        container.addEventListener("mouseout", () => {
            container.style.backgroundColor = null
        })

        button.parentNode.parentNode.style.display = "none"
    """)

    with container:
        yield clicked


def toggle_containers(columns, gap="small", key=0):
    cols = st.columns(columns, gap=gap)
    containers = []

    for col in cols:
        with col:
            containers.append(st.container(border=True))

    selection = st.radio("", range(columns), key=f"--button-container-{key}")

    script("""
        const radioContainer = parentNode.previousSibling
        const columnContainer = radioContainer.previousSibling
        const radioButtons = Array.from(radioContainer.querySelectorAll(
            ":scope [data-baseweb=radio]"))
        const columns = Array.from(columnContainer.querySelectorAll(
            ":scope [data-testid=stVerticalBlock] > [data-testid=stVerticalBlockBorderWrapper]"))

        const styles = getComputedStyle(columnContainer)
        const textColor = styles.getPropertyValue("color")
        const bgColor = styles.getPropertyValue("background-color")

        function setSelectedStyle(i, selected) {
            columns[i].style.backgroundColor = selected
                ? `color-mix(in srgb, ${textColor} 5%, ${bgColor})`
                : null
        }

        let selectedIndex = 0
        setSelectedStyle(selectedIndex, true)

        function selectColumn(i) {
            const ev = new MouseEvent("click", {
              view: window,
              bubbles: true,
              cancelable: true,
            })

            radioButtons[i].dispatchEvent(ev)

            setSelectedStyle(selectedIndex, false)
            selectedIndex = i
            setSelectedStyle(selectedIndex, true)
        }

        columns.forEach((column, i) => {
            column.addEventListener("click", () => selectColumn(i))

            column.style.cursor = "pointer"

            column.addEventListener("mouseover", () => {
                setSelectedStyle(i, true)
            })

            column.addEventListener("mouseout", () => {
                setSelectedStyle(i, selectedIndex == i)
            })
        })

        radioContainer.style.display = "none"
    """)

    return containers, selection


def script(body):
    components.html(f"""
        <script>
            const scriptWindow = window
            const scriptDocument = document
            const outerWindow = window.parent
            const outerDocument = window.parent.document

            const iframe = Array.from(
                outerDocument.getElementsByTagName("iframe")
            ).find(frame => frame.contentDocument == document)

            const parentNode = iframe.parentNode
            parentNode.style.display = "none"

            window = outerWindow
            window.document = outerDocument

            {body}
        </script>
    """, height=0)
