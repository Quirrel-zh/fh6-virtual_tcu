# Electron build resources

Place a **valid Windows `.ico`** here (multi-resolution, e.g. 16–256 px).
Do **not** rename a `.png` to `.ico` — `electron-builder` / `rcedit` will fail with:

`Reserved header is not 0 or image type is not icon`

## Generate `icon.ico` from a PNG

```powershell
pip install pillow
python build/make-icon.py path/to/source.png
```

Or use an online converter / GIMP / Photoshop and export as Windows ICO.

Optional: `installerIcon.ico` (NSIS wizard), `background.png` (NSIS sidebar).
`installer.nsh` — custom uninstall hooks (force-kill processes, retry directory removal).
Then set `icon:` in `../electron-builder.yml` (already enabled).
