import pygetwindow as gw

def close_legacy_guard_windows():
    # Find windows with the title "Legacy Guard"
    legacy_guard_windows = gw.getWindowsWithTitle('Legacy Guard')

    # Close each window
    for window in legacy_guard_windows:
        window.close()

close_legacy_guard_windows()
