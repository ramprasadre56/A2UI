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

"""A2UI Message Processor - handles A2UI messages and manages surfaces."""

from typing import Any, Optional
from .types import A2UIMessage, Component, Surface
from .data_model import DataModel


class MessageProcessor:
    """Processes A2UI messages and manages surfaces."""

    def __init__(self):
        self._surfaces: dict[str, Surface] = {}

    def process_messages(self, messages: list[A2UIMessage]) -> None:
        """Process a list of A2UI messages.

        Args:
            messages: List of A2UI messages to process.
        """
        for message in messages:
            self.process_message(message)

    def process_message(self, message: A2UIMessage) -> None:
        """Process a single A2UI message.

        Args:
            message: A2UI message containing one action.
        """
        if "beginRendering" in message:
            self._handle_begin_rendering(message["beginRendering"])
        elif "surfaceUpdate" in message:
            self._handle_surface_update(message["surfaceUpdate"])
        elif "dataModelUpdate" in message:
            self._handle_data_model_update(message["dataModelUpdate"])
        elif "deleteSurface" in message:
            self._handle_delete_surface(message["deleteSurface"])

    def _handle_begin_rendering(self, data: dict) -> None:
        """Handle beginRendering message."""
        surface_id = data.get("surfaceId", "default")
        root_id = data.get("root")
        styles = data.get("styles", {})

        self._surfaces[surface_id] = Surface(
            surface_id=surface_id,
            root_id=root_id,
            components={},
            data_model={},
            styles=styles,
        )

    def _handle_surface_update(self, data: dict) -> None:
        """Handle surfaceUpdate message."""
        surface_id = data.get("surfaceId", "default")
        components = data.get("components", [])

        # Create surface if it doesn't exist
        if surface_id not in self._surfaces:
            self._surfaces[surface_id] = Surface(
                surface_id=surface_id,
                components={},
                data_model={},
            )

        surface = self._surfaces[surface_id]

        # Update components
        for comp in components:
            comp_id = comp.get("id")
            if comp_id:
                surface.components[comp_id] = comp

    def _handle_data_model_update(self, data: dict) -> None:
        """Handle dataModelUpdate message."""
        surface_id = data.get("surfaceId", "default")
        path = data.get("path")
        contents = data.get("contents", [])

        # Create surface if it doesn't exist
        if surface_id not in self._surfaces:
            self._surfaces[surface_id] = Surface(
                surface_id=surface_id,
                components={},
                data_model={},
            )

        surface = self._surfaces[surface_id]

        # Create DataModel and update it
        data_model = DataModel()
        data_model._data = surface.data_model
        data_model.update(path, contents)
        surface.data_model = data_model.data

    def _handle_delete_surface(self, data: dict) -> None:
        """Handle deleteSurface message."""
        surface_id = data.get("surfaceId")
        if surface_id and surface_id in self._surfaces:
            del self._surfaces[surface_id]

    def get_surface(self, surface_id: str) -> Optional[Surface]:
        """Get a surface by ID.

        Args:
            surface_id: The surface ID.

        Returns:
            The Surface object, or None if not found.
        """
        return self._surfaces.get(surface_id)

    def get_surfaces(self) -> dict[str, Surface]:
        """Get all surfaces.

        Returns:
            Dictionary of surface_id to Surface.
        """
        return self._surfaces.copy()

    def clear_surfaces(self) -> None:
        """Clear all surfaces."""
        self._surfaces.clear()

    def get_data_model(self, surface_id: str) -> DataModel:
        """Get a DataModel instance for a surface.

        Args:
            surface_id: The surface ID.

        Returns:
            DataModel instance initialized with surface data.
        """
        surface = self._surfaces.get(surface_id)
        data_model = DataModel()
        if surface:
            data_model._data = surface.data_model.copy()
        return data_model
