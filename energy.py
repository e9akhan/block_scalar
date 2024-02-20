"""
    Module name :- energy
"""

import os
import csv
from datetime import datetime


def load_csv(filepath):
    """
    Load CSV.
    """
    filepath = os.path.abspath(filepath)

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    return reader


def calculate_block_price(data):
    """
    Calculate Block Price.
    """
    return sum(float(record["price"]) for record in data) / len(data) if data else 0


def calculate_scalar_price(data, block_price):
    """
    Calculate Scalar Price.
    """
    return [float(record["price"]) / block_price for record in data]


def calculate_daily_block_price(data):
    """
    Calculate Daily Block Price.
    """
    off_peak_list = []
    peak_list = []

    for record in data:
        date_obj = datetime.strptime(record["date"], "%Y-%m-%d %H:%M:%S")
        hour = date_obj.hour

        if 6 <= hour <= 21:
            peak_list.append(record)
        else:
            off_peak_list.append(record)

    peak_block_price = calculate_block_price(peak_list)
    off_peak_block_price = calculate_block_price(off_peak_list)

    return peak_block_price, off_peak_block_price


def monthly_block_data(data):
    """
    Monthly Block Data.
    """
    idx = 0
    peak_price, off_peak_price = 0, 0

    while idx < len(data):
        daily_list = []

        while idx % 24:
            daily_list.append(data[idx])
            idx += 1

        output = calculate_daily_block_price(daily_list)
        peak_price += output[0]
        off_peak_price += output[1]

        idx += 1

    length = len(data) // 24
    return peak_price / length, off_peak_price / length


def block_data(data):
    """
    Block Data.
    """
    idx = 0
    monthly_record = []

    for i in range(1, 13):
        month_list = []
        peak_price, off_peak_price = 0, 0
        while idx < len(data):
            date_obj = datetime.strptime(data[idx]["date"], "%Y-%m-%d %H:%M:%S")
            month = date_obj.month

            if month == i + 1:
                month -= 1
                break

            month_list.append(data[idx])
            idx += 1

        output = monthly_block_data(month_list)
        peak_price += output[0]
        off_peak_price += output[1]

        date = str(date_obj.year) + "-" + f"{month:0>2}"
        dictionary = {
            "date": date,
            "peak_price": f"{peak_price:.2f}",
            "off_peak_price": f"{off_peak_price:.2f}",
        }

        monthly_record.append(dictionary)

    filepath = os.getcwd() + "/block.csv"
    with open(filepath, "w", encoding="utf-8") as f:
        headers = monthly_record[0].keys()
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(monthly_record)

    return filepath


def calculate_daily_scalar_price(data, peak_price, off_peak_price):
    """
    Daily Scalar Price.
    """
    off_peak_list = []
    peak_list = []

    for record in data:
        date_obj = datetime.strptime(record["date"], "%Y-%m-%d %H:%M:%S")
        hour = date_obj.hour

        if 6 <= hour <= 21:
            peak_list.append(record)
        else:
            off_peak_list.append(record)

    peak_block_price = calculate_scalar_price(peak_list, peak_price)
    off_peak_block_price = calculate_scalar_price(off_peak_list, off_peak_price)

    return off_peak_block_price[:6] + peak_block_price + off_peak_block_price[6:]


def monthly_scalar_data(data):
    """
    Monthly Scalar Data.
    """
    idx = 0
    scalar_list = []
    length = len(data) // 24

    while idx < len(data):
        daily_list = []

        while True:
            daily_list.append(data[idx])
            idx += 1

            if (idx % 24) == 0:
                break

        peak_price, off_peak_price = calculate_daily_block_price(daily_list)
        output = calculate_daily_scalar_price(daily_list, peak_price, off_peak_price)
        scalar_list.append(output)

    monthly_scalar_list = []
    for i in range(24):
        price = sum(scalar[i] for scalar in scalar_list)
        monthly_scalar_list.append(price / length)

    return monthly_scalar_list


def scalar_data(data):
    """
    Scalar Data.
    """
    idx = 0
    monthly_record = []

    for i in range(1, 13):
        month_list = []
        while idx < len(data):
            date_obj = datetime.strptime(data[idx]["date"], "%Y-%m-%d %H:%M:%S")
            month = date_obj.month

            if month == i + 1:
                month -= 1
                break

            month_list.append(data[idx])
            idx += 1

        output = monthly_scalar_data(month_list)

        i = 0
        for price in output:
            dictionary = {
                "date": str(date_obj.year)
                + "-"
                + f"{month:0>2}"
                + "-01 "
                + f"{i:0>2}:00:00",
                "scalar": f"{price:.2f}",
            }

            monthly_record.append(dictionary)
            i += 1

    filepath = os.getcwd() + "/scalar.csv"
    with open(filepath, "w", encoding="utf-8") as f:
        headers = monthly_record[0].keys()
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(monthly_record)

    return filepath


def main():
    """
    Main
    """
    data = load_csv("hourly_prices.csv")
    print(block_data(data))
    print(scalar_data(data))


if __name__ == "__main__":
    main()
