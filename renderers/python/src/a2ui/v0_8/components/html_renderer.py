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

"""HTML Renderer for A2UI components."""

from html import escape
from typing import Any, Callable, Optional
from ..processor import MessageProcessor
from ..data_model import DataModel


class HTMLRenderer:
    """Renders A2UI components to HTML strings."""

    # Default styles for A2UI components
    DEFAULT_CSS = """
    .a2ui-surface {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    .a2ui-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15);
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .a2ui-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(46, 125, 50, 0.2);
    }
    .a2ui-row {
        display: flex;
        flex-direction: row;
        gap: 16px;
        align-items: center;
        padding: 12px;
    }
    .a2ui-column {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .a2ui-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .a2ui-image {
        width: 150px;
        height: 120px;
        border-radius: 12px;
        object-fit: cover;
    }
    .a2ui-title {
        font-weight: 600;
        color: #1b5e20;
        font-size: 16px;
        margin: 0;
    }
    .a2ui-text {
        color: #757575;
        font-size: 14px;
        margin: 0;
    }
    .a2ui-heading {
        color: #388e3c;
        font-weight: 600;
        margin: 0;
    }
    .a2ui-button {
        background: #388e3c;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }
    .a2ui-button:hover {
        background: #1b5e20;
    }
    .a2ui-divider {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 8px 0;
    }
    """

    def __init__(
        self,
        processor: MessageProcessor,
        base_url: str = "http://localhost:10004",
    ):
        """Initialize the renderer.

        Args:
            processor: The MessageProcessor containing surfaces.
            base_url: Base URL for resolving relative URLs (e.g., for images).
        """
        self._processor = processor
        self._base_url = base_url

    def render_surface(self, surface_id: str) -> str:
        """Render a surface to HTML.

        Args:
            surface_id: The surface ID to render.

        Returns:
            HTML string representation of the surface.
        """
        surface = self._processor.get_surface(surface_id)
        if not surface:
            return ""

        # Get data model for resolving paths
        data_model = DataModel()
        data_model._data = surface.data_model

        # Build component map
        component_map = surface.components

        # Render all components
        html_parts = []
        for comp_id, comp in component_map.items():
            html = self._render_component(comp, component_map, data_model)
            if html:
                html_parts.append(html)

        return f'<div class="a2ui-surface">{"".join(html_parts)}</div>'

    def render_all_surfaces(self) -> str:
        """Render all surfaces to HTML.

        Returns:
            HTML string with all surfaces.
        """
        surfaces = self._processor.get_surfaces()
        html_parts = []
        for surface_id in surfaces:
            html = self.render_surface(surface_id)
            if html:
                html_parts.append(html)
        return "".join(html_parts)

    def get_css(self) -> str:
        """Get the default CSS for A2UI components.

        Returns:
            CSS string.
        """
        return self.DEFAULT_CSS

    def _resolve(self, value: Any, data_model: DataModel, default: str = "") -> str:
        """Resolve an A2UI value to a string."""
        return data_model.resolve_value(value, default)

    def _render_component(
        self,
        component: dict,
        component_map: dict,
        data_model: DataModel,
    ) -> str:
        """Render a single component to HTML."""
        comp_wrapper = component.get("component", {})
        if not comp_wrapper:
            return ""

        comp_type = list(comp_wrapper.keys())[0]
        props = comp_wrapper[comp_type]

        renderers = {
            "Text": self._render_text,
            "Heading": self._render_heading,
            "Image": self._render_image,
            "Card": self._render_card,
            "Row": self._render_row,
            "Column": self._render_column,
            "List": self._render_list,
            "Button": self._render_button,
            "Divider": self._render_divider,
        }

        renderer = renderers.get(comp_type)
        if renderer:
            return renderer(props, component_map, data_model)

        return ""

    def _render_text(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Text component."""
        text = escape(self._resolve(props.get("text"), data_model))
        hint = props.get("usageHint", "")
        css_class = "a2ui-title" if hint == "h3" else "a2ui-text"
        return f'<p class="{css_class}">{text}</p>'

    def _render_heading(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Heading component."""
        text = escape(self._resolve(props.get("text"), data_model))
        level = props.get("level", 2)
        level = max(1, min(6, level))  # Clamp to valid heading level
        return f'<h{level} class="a2ui-heading">{text}</h{level}>'

    def _render_image(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Image component."""
        url = self._resolve(props.get("url"), data_model)
        alt = escape(self._resolve(props.get("alt"), data_model))

        # Handle relative URLs
        if url.startswith("/"):
            url = f"{self._base_url}{url}"

        return f'<img src="{escape(url)}" alt="{alt}" class="a2ui-image" />'

    def _render_card(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Card component."""
        child_id = props.get("child")
        child_html = ""
        if child_id and child_id in component_map:
            child_html = self._render_component(
                component_map[child_id], component_map, data_model
            )
        return f'<div class="a2ui-card">{child_html}</div>'

    def _render_row(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Row component."""
        children_html = self._render_children(props, component_map, data_model)
        return f'<div class="a2ui-row">{children_html}</div>'

    def _render_column(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Column component."""
        children_html = self._render_children(props, component_map, data_model)
        return f'<div class="a2ui-column">{children_html}</div>'

    def _render_list(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render List component."""
        children_html = self._render_children(props, component_map, data_model)
        return f'<div class="a2ui-list">{children_html}</div>'

    def _render_button(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Button component."""
        label = escape(self._resolve(props.get("label"), data_model, "Button"))
        return f'<button class="a2ui-button">{label}</button>'

    def _render_divider(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render Divider component."""
        return '<hr class="a2ui-divider" />'

    def _render_children(
        self, props: dict, component_map: dict, data_model: DataModel
    ) -> str:
        """Render children of a container component."""
        children_prop = props.get("children", {})
        explicit_list = children_prop.get("explicitList", [])

        html_parts = []
        for child_id in explicit_list:
            if child_id in component_map:
                html = self._render_component(
                    component_map[child_id], component_map, data_model
                )
                if html:
                    html_parts.append(html)

        return "".join(html_parts)
