# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A2UI message processor and renderer for Reflex."""

from typing import Any
import reflex as rx
from . import style


def render_a2ui_messages(messages: list[dict]) -> rx.Component:
    """Render A2UI messages as Reflex components."""
    components = []

    for message in messages:
        if "surfaceUpdate" in message:
            surface_update = message["surfaceUpdate"]
            rendered = render_surface_update(surface_update)
            if rendered:
                components.append(rendered)
        elif "beginRendering" in message:
            # beginRendering just indicates we should start fresh
            pass

    if not components:
        return rx.box()

    return rx.box(
        *components,
        style=style.surfaces_style,
    )


def render_surface_update(surface_update: dict) -> rx.Component | None:
    """Render a surface update message."""
    components_list = surface_update.get("components", [])
    root_id = surface_update.get("root")

    if not components_list:
        return None

    # Build a map of component ID to component definition
    component_map = {}
    for comp in components_list:
        comp_id = comp.get("id")
        if comp_id:
            component_map[comp_id] = comp

    # Render starting from root
    if root_id and root_id in component_map:
        return render_component(component_map[root_id], component_map)

    # If no root, render all components
    rendered = []
    for comp in components_list:
        rendered_comp = render_component(comp, component_map)
        if rendered_comp:
            rendered.append(rendered_comp)

    return rx.box(*rendered) if rendered else None


def render_component(component: dict, component_map: dict) -> rx.Component | None:
    """Render a single A2UI component."""
    component_props = component.get("componentProperties", {})

    if not component_props:
        return None

    # Get the component type (the key in componentProperties)
    comp_type = list(component_props.keys())[0]
    props = component_props[comp_type]

    renderers = {
        "Text": render_text,
        "Heading": render_heading,
        "Image": render_image,
        "Card": render_card,
        "Row": render_row,
        "Column": render_column,
        "List": render_list,
        "Button": render_button,
        "Divider": render_divider,
    }

    renderer = renderers.get(comp_type)
    if renderer:
        return renderer(props, component_map)

    return None


def render_text(props: dict, component_map: dict) -> rx.Component:
    """Render a Text component."""
    text = props.get("text", "")
    usage_hint = props.get("usageHint", "")

    text_style = dict(style.text_style)

    if usage_hint == "h3":
        text_style.update(style.card_title_style)
    elif usage_hint == "subtitle":
        text_style.update(style.card_subtitle_style)

    return rx.text(text, style=text_style)


def render_heading(props: dict, component_map: dict) -> rx.Component:
    """Render a Heading component."""
    text = props.get("text", "")
    level = props.get("level", 2)

    heading_components = {
        1: rx.heading,
        2: rx.heading,
        3: rx.heading,
    }

    heading_func = heading_components.get(level, rx.heading)
    return heading_func(text, style=style.heading_style, size=str(9 - level))


def render_image(props: dict, component_map: dict) -> rx.Component:
    """Render an Image component."""
    url = props.get("url", "")
    alt = props.get("alt", "")

    # Handle relative URLs from the agent
    if url.startswith("/static/"):
        url = f"http://localhost:10004{url}"

    return rx.image(src=url, alt=alt, style=style.card_image_style)


def render_card(props: dict, component_map: dict) -> rx.Component:
    """Render a Card component."""
    child_id = props.get("child")

    child_component = None
    if child_id and child_id in component_map:
        child_component = render_component(component_map[child_id], component_map)

    return rx.box(
        child_component if child_component else rx.box(),
        style=style.card_style,
    )


def render_row(props: dict, component_map: dict) -> rx.Component:
    """Render a Row component."""
    children = render_children(props, component_map)
    return rx.hstack(*children, style=style.card_row_style)


def render_column(props: dict, component_map: dict) -> rx.Component:
    """Render a Column component."""
    children = render_children(props, component_map)
    return rx.vstack(*children, style=style.card_column_style, align="start")


def render_list(props: dict, component_map: dict) -> rx.Component:
    """Render a List component."""
    children = render_children(props, component_map)
    return rx.vstack(*children, style=style.list_style, align="stretch")


def render_button(props: dict, component_map: dict) -> rx.Component:
    """Render a Button component."""
    label = props.get("label", "Button")

    return rx.button(
        label,
        style=style.card_button_style,
    )


def render_divider(props: dict, component_map: dict) -> rx.Component:
    """Render a Divider component."""
    return rx.divider()


def render_children(props: dict, component_map: dict) -> list[rx.Component]:
    """Render children of a container component."""
    children_prop = props.get("children", {})
    explicit_list = children_prop.get("explicitList", [])

    rendered_children = []
    for child_id in explicit_list:
        if child_id in component_map:
            child = render_component(component_map[child_id], component_map)
            if child:
                rendered_children.append(child)

    return rendered_children
