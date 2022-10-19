from pathlib import Path

if __name__ == "__main__":
    source = Path(__file__).parent / "plugin.py"
    target = Path("~") / "domoticz" / "plugins" / "AirtonAC" / "plugin.py"
    if not target.parent.exists():
        target.parent.mkdir()
    target.write_text(source.read_text())
