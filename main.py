"""Launch from any working directory with Python 3.12+."""

import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="Abandoned Mall Restorer")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Render a frame and exit using a headless display",
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Start in a resizable window instead of fullscreen",
    )
    parser.add_argument(
        "--dev", action="store_true", help="Enable F3 developer playtest shortcuts"
    )
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        from game.smoke import run

        run(developer=args.dev)
        return
    from game.game import Game

    game = Game(
        fullscreen=not args.windowed,
        start_screen=True,
        developer=args.dev,
        persistence=True,
    )
    if args.windowed and game.fullscreen:
        game.toggle_fullscreen()
    game.run()


if __name__ == "__main__":
    main()
