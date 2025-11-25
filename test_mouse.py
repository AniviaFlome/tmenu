#!/usr/bin/env python3
import curses
import sys


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Mouse test - Click anywhere or press 'q' to quit")
    stdscr.addstr(1, 0, "Requested mask: ")

    # Enable mouse
    mask = curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION
    available = curses.mousemask(mask)

    stdscr.addstr(1, 16, f"{bin(mask)}")
    stdscr.addstr(2, 0, f"Available mask: {bin(available[0])}")
    stdscr.addstr(3, 0, f"Has clicks: {bool(available[0] & curses.BUTTON1_CLICKED)}")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                stdscr.addstr(
                    5, 0, f"MOUSE EVENT! x={mx}, y={my}, state={bin(bstate)}    "
                )
                stdscr.refresh()
            except:
                stdscr.addstr(5, 0, "Mouse event but getmouse failed    ")
                stdscr.refresh()
        else:
            stdscr.addstr(6, 0, f"Key pressed: {key}    ")
            stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
