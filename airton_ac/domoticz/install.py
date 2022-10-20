import sys
from pathlib import Path

if __name__ == "__main__":
    domoticz_path = sys.argv[1] if len(sys.argv) > 1 else "/home/domoticz/domoticz"
    source = Path(__file__).parent / "plugin.py"
    target = Path(domoticz_path) / "plugins" / "AirtonAC" / "plugin.py"
    if not target.parent.exists():
        target.parent.mkdir()
    target.write_text(source.read_text())
