"""Inline property-page sections bound to the selected plugin node."""
from aphelion_sdk.widgets.base import PluginWidget


class InspectorWidget(PluginWidget):
    """An inline section in the properties page; supports primitives or Qt."""
    widget_kind = "inspector"
