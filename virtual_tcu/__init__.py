"""Virtual TCU — external adaptive transmission controller for Forza Horizon 6."""

__version__ = "12.0"

__all__ = ["__version__", "main"]


def main():
    from virtual_tcu.app import main as _main

    return _main()
