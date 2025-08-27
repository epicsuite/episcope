from __future__ import annotations

from episcope.app.core import App


def main():
    app = App()
    app.server.start()


if __name__ == "__main__":
    main()
