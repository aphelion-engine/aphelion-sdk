# Packaging plugins

Three ways to get a plugin into the editor: drop-in files, a generated wheel, or your own PEP 517 project with an entry point.

## Drop-in files

Copy a `.py` module into the editor's `plugins/` or `userdata/plugins/`, then **Preferences → Plugins → Reload**.

Programmatic copy into the user folder:

```python
from pathlib import Path
from aphelion_sdk.host import install_plugins_into_editor

install_plugins_into_editor(Path("examples/grayscale_effect.py"))
```

`locate_editor()` / `discover_editors()` find an installed editor when you need a specific target.

## `aphelion-sdk build`

Wraps plugin sources, writes a src-layout project, and emits a wheel whose `aphelion.editor.plugins` entry points are already set.

```bash
aphelion-sdk build examples/grayscale_effect.py -o dist
pip install dist/aphelion_plugin_grayscale-*.whl
```

Point it at a directory of `.py` files to pack several plugins into one distribution.

```bash
aphelion-sdk build path/to/plugins -o dist --name my-aphelion-plugins --package-version 1.2.0
```

Optional flags (generated packages only): `--name`, `--package-version` (default `0.1.0`), `--author`, `--description`.

`python -m aphelion_sdk build` is equivalent. Default `source` is the current directory; default `-o` is `./dist`.

## Your own project

```toml
[project.entry-points."aphelion.editor.plugins"]
grayscale = "my_plugin_package.grayscale:GrayscaleEffect"
```

Then:

```bash
aphelion-sdk build path/to/project
```

That path must contain `pyproject.toml`. The CLI runs a standard PEP 517 build (does not wrap sources).

You can also `python -m build` in that project.

## After install

Restart the editor, or enable the entry-point source and reload under **Preferences → Plugins**. Disabled keys in preferences skip registration.

## Building this SDK

From `aphelion-sdk/`:

```bash
pip install -e ".[dev]"
python -m build
```

The PyPI / wheel name is `aphelion-plugin-sdk`. Import remains `aphelion_sdk`. Installing the editor from `aphelion-editor/` already depends on `aphelion-plugin-sdk @ file:../aphelion-sdk`.
