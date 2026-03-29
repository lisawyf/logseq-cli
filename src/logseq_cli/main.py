"""Package entrypoint for logseq-cli."""

from logseq_cli.cli.app import app


def main() -> None:
    """Run the Typer application."""
    app()


if __name__ == "__main__":
    main()
