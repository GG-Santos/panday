# Panday

Panday is a standalone, composable skill ecosystem with 12 canonical skills,
a Python standard-library CLI, and versioned lifecycle records.

## Install

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/GG-Santos/panday/main/install.bat -OutFile install.bat
./install.bat
```

macOS/Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/GG-Santos/panday/main/install.sh | sh
```

The installers require [`uv`](https://docs.astral.sh/uv/) and download the
fingerprintable package archive from this repository. Set `PANDAY_REPO`,
`PANDAY_VERSION`, or `PANDAY_HOME` to override the defaults.

After installation:

```sh
panday --version
panday --json doctor
```

Add the installed `skills` directory to `~/.panday/config.toml` under
`[registries]` to make the bundled skills discoverable.

## Included capabilities

`panday-discover`, `panday-create`, `panday-inspect`, `panday-evaluate`,
`panday-fix`, `panday-install`, `panday-card`, `panday-augment`,
`panday-synthesize`, `panday-optimize`, `panday-connect`, and `panday-migrate`.

See `cli/README.md` in the package archive for the full command reference.
