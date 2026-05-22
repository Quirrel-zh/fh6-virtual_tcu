#!/usr/bin/env python3
"""Backward-compatible entry point. Prefer: python -m virtual_tcu"""

import sys


def _run() -> None:
    from virtual_tcu.app import main

    main()


if __name__ == "__main__":
    try:
        _run()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (1 if e.code else 0)
        if code:
            from virtual_tcu.bootstrap import pause_before_exit

            pause_before_exit(code)
        sys.exit(code if code is not None else 0)
    except Exception as e:
        from virtual_tcu.bootstrap import report_fatal

        report_fatal("Virtual TCU failed to start.", exc=e)
