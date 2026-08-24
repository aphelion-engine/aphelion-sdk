# Plugin widgets

Widgets are **not** plugins. They are UI surfaces owned by a `Plugin` subclass:

```python
widgets = (NotesDialog, StatusPanel)
```

The editor discovers them when it registers the parent plugin. Never use `@register_plugin` on a widget class.

## Kinds

| Class | Kind | Host chrome |
|---|---|---|
| `PanelWidget` | Dockable panel | Dock title / window menu |
| `DialogWidget` | Popup | Title bar, OK/Cancel (modal by default) |

Identity:

| Attribute | Role |
|---|---|
| `widget_id` | Used by `custom_property(widget_id=...)` and `host.open_dialog(...)`. Defaults to the class name. |
| `widget_title` | Dock or window title |
| `widget_description` | Tooltip |
| `widget_modal` | Dialogs: block the editor when True |
| `widget_width` / `widget_height` | Dialog initial size |
| `widget_show_in_menu` | Dialogs: list under Plugin Windows |

## Simple UI (host primitives)

Implement `build_view(host)` and use `host.create_view()`:

- `add_label`, `add_button`, `add_text`, `add_separator`
- `set_text` / `get_text` for later updates
- `host.open_dialog("notes")` to open a sibling dialog
- `host.get_property_value` / `host.set_property_value` (writes go through undo)

`host.context()` returns `WidgetContext` (`plugin_key`, `node_id`, `property_key`, `project_name`).

## Inspector extras

On `VideoEffectPlugin`:

- `build_property_panel(host)` — extra section below generated property rows
- `custom_property(..., widget_id="notes")` — inspector row that opens that dialog

## Advanced PyQt6

The host keeps dock/dialog chrome. You own only the body widget. Still do not import editor packages.

1. Return a `QWidget` from `build_qt_widget(parent, host)` (or `build_property_qt_widget` on a video effect).
2. Or mix primitives with `view.embed_native(my_widget)` inside `build_view`.

Parent custom widgets with `aphelion_sdk.coerce_qt_parent(parent)` or `host.qt_parent()`. Check types with `is_qt_widget`.

On a modal `DialogWidget`, persist edits in `on_accept(view, host)`. `on_reject` runs on cancel/close.

See [`examples/effect_with_widget.py`](../examples/effect_with_widget.py).
