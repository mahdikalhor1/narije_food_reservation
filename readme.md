# Narije Food Reservation

## Command-line Arguments

- `--username`: Required. Specifies the username (mobile number) for authentication with the API.
- `--password`: Required. Specifies the password (mobile number) for authentication with the API.
- `--include-thursdays`: Optional. Flag to include Thursdays in the reservation process. If not provided, Thursdays are skipped.
- `--lazy-mode`: Optional. Flag to enable lazy mode. When enabled, the script automatically reserves the first available food item for each day without user intervention.

## Example Command

To run the script with all options enabled:
```sh
python reserve_food.py --username alice@example.com --password mypassword --include-thursdays --lazy-mode

