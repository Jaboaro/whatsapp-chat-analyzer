from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .generator import generate_chat
from .profiles import EN_PROFILE, ES_PROFILE, ExportProfile


PROFILES: dict[str, ExportProfile] = {
    "en": EN_PROFILE,
    "es": ES_PROFILE,
}


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the chat generator CLI.
    """
    parser = argparse.ArgumentParser(
        description="Generate a synthetic WhatsApp chat export"
    )

    parser.add_argument(
        "--profile",
        choices=PROFILES.keys(),
        default="en",
        help="WhatsApp export profile / locale",
    )

    parser.add_argument(
        "--users",
        nargs="+",
        required=True,
        help="List of chat participants (minimum 2)",
    )

    parser.add_argument(
        "--start-date",
        default="2023-01-01",
        help="Chat start date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to generate",
    )

    parser.add_argument(
        "--avg-messages-per-day",
        type=int,
        default=120,
        help="Average messages per day",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file path",
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point for the chat generator CLI.
    """
    args = parse_args()

    # Validate number of users
    if len(args.users) < 2:
        raise SystemExit("You must provide at least two users.")

    # Validate and parse start date
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("Invalid --start-date format. Use YYYY-MM-DD.")

    profile: ExportProfile = PROFILES[args.profile]

    chat_text = generate_chat(
        users=args.users,
        start_date=start_date,
        days=args.days,
        avg_messages_per_day=args.avg_messages_per_day,
        export_profile=profile,
        seed=args.seed,
    )

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(chat_text, encoding="utf-8")

    # CLI summary output
    print("\nChat successfully generated")
    print("-" * 40)
    print(f"Users: {', '.join(args.users)}")
    print(f"Days: {args.days}")
    print(f"Average messages/day: {args.avg_messages_per_day}")
    print(f"Profile: {args.profile}")
    print(f"Seed: {args.seed}")
    print(f"Output: {args.output}")
    print("-" * 40)


if __name__ == "__main__":
    main()
