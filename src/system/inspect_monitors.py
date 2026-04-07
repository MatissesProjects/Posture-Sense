from screeninfo import get_monitors
import json

def inspect_monitors():
    print("--- Monitor Layout Inspection ---")
    monitors = get_monitors()
    
    layout = []
    for i, m in enumerate(monitors):
        monitor_data = {
            "id": i,
            "name": m.name,
            "x": m.x,
            "y": m.y,
            "width": m.width,
            "height": m.height,
            "is_primary": m.is_primary
        }
        layout.append(monitor_data)
        print(f"Monitor {i}: {m.width}x{m.height} at ({m.x}, {m.y}) {'[Primary]' if m.is_primary else ''}")

    # Check for stacked layout
    if len(monitors) >= 2:
        # Sort by Y coordinate
        sorted_monitors = sorted(monitors, key=lambda m: m.y)
        top = sorted_monitors[0]
        bottom = sorted_monitors[1]
        
        if bottom.y >= top.y + top.height:
            print(f"\nDetected STACKED layout:")
            print(f"  TOP: {top.width}x{top.height}")
            print(f"  BOTTOM: {bottom.width}x{bottom.height}")
        else:
            print("\nLayout does not appear to be perfectly stacked vertically.")
    else:
        print("\nOnly one monitor detected.")

    return layout

if __name__ == "__main__":
    inspect_monitors()
