#!/usr/bin/env python3

import argparse
from datetime import date

from connector import TransaviaConnector, Travel


class main:
    def __init__(
        self, origin: str, destination: str, departure_time: date, return_date: date
    ):
        t = Travel(origin, destination, departure_time, return_date)
        connector = TransaviaConnector(False)
        flights = connector.search_travel(t)
        [print(f) for f in flights]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Transavia Scrapper")
    parser.add_argument("-o", "--origin", help="Travel origin", required=True)
    parser.add_argument("-t", "--to", help="Travel destination", required=True)
    parser.add_argument(
        "-d", "--departure-date", help="Travel departure date", required=True
    )
    parser.add_argument(
        "-r", "--return-date", help="Travel arrival date", required=True
    )
    args = parser.parse_args()
    main(
        origin=args.origin,
        destination=args.to,
        departure_time=date.fromisoformat(args.departure_date),
        return_date=date.fromisoformat(args.return_date),
    )
