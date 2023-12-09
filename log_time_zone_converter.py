#!/usr/bin/python3

from datetime import datetime
import pytz
import os
import logging
from logging.handlers import RotatingFileHandler
import click

# Constants
VERSION = "1.4"
MENU_OPTIONS = {'MANUAL': 1, 'LOG_FILE': 2, 'EXIT': 3}

# Logger configuration
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('timestamp_converter.log', maxBytes=1024000, backupCount=5)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Banner
print("""
*******************************************************************
*                   Security tools by KaliHacks                   *
*            Version: 1.4 | By Wajahat Ali A.K.A KaliHacks        *
*  For support or inquiries, email us at hacker@wajahatali.ca     *
*******************************************************************
""")


def get_valid_input(prompt, max_value, input_type=int):
    """Get a valid input within a specified range."""
    while True:
        try:
            value = input_type(input(prompt).strip())
            if value == 'exit':
                return 'exit'
            if 1 <= value <= max_value:
                return value
            print("Invalid input. Please enter a valid option.")
        except ValueError:
            print("Invalid input. Please enter a valid option.")


def get_region_options():
    """Get a sorted list of unique region options."""
    return sorted(set(tz.split('/')[0] for tz in pytz.all_timezones))


def get_timezones_by_region(region):
    """Get a sorted list of timezones for a given region."""
    return sorted(tz for tz in pytz.all_timezones if tz.startswith(region + '/'))


def sanitize_file_name(file_name):
    """Sanitize file name to prevent path traversal attacks."""
    return os.path.basename(file_name)


def convert_timestamp_to_local(timestamp_str, selected_timezone):
    """Convert a timestamp to a local time in the specified timezone."""
    try:
        timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
        local_timestamp = timestamp.astimezone(pytz.timezone(selected_timezone))
        return local_timestamp.strftime("%d/%b/%Y:%H:%M:%S %Z")
    except ValueError as e:
        logger.error(f"Error converting timestamp: {e}")
        return f"Error: {e}"


def display_options(options, prompt):
    """Display a numbered list of options and return the user's choice."""
    print(f"\n{prompt}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    return options[get_valid_input(f"Enter the number for the desired {prompt.lower()}: ", len(options)) - 1]


def get_menu_option():
    """Get a valid option from the main menu."""
    return get_valid_input("Enter the option number or 'exit' to quit: ", len(MENU_OPTIONS))


@click.command()
def handle_manual_conversion():
    """Handle manual timestamp conversion."""
    timestamp_input = click.prompt("Enter the timestamp (e.g., 25/Oct/2023:09:11:14 +0000)")
    selected_region = display_options(get_region_options(), "Select a Region")
    selected_timezone = display_options(get_timezones_by_region(selected_region), "Select a Time Zone")
    local_timestamp = convert_timestamp_to_local(timestamp_input, selected_timezone)
    click.echo(f"\nTimestamp in {selected_timezone}: {local_timestamp}")


@click.command()
def handle_log_file_conversion():
    """Handle log file timestamp conversion."""
    log_file = sanitize_file_name(click.prompt("Enter the log file name: "))

    if not os.path.exists(log_file):
        logger.error(f"Error: The file '{log_file}' does not exist.")
        click.echo(f"Error: The file '{log_file}' does not exist.")
        return

    selected_region = display_options(get_region_options(), "Select a Region")
    selected_timezone = display_options(get_timezones_by_region(selected_region), "Select a Time Zone")

    with open(log_file, 'r') as file:
        lines = file.readlines()

    converted_lines = []
    for line in lines:
        # Assuming timestamps are enclosed in square brackets []
        timestamp_start = line.find('[')
        timestamp_end = line.find(']')
        if timestamp_start != -1 and timestamp_end != -1:
            timestamp_str = line[timestamp_start + 1:timestamp_end]
            converted_timestamp = convert_timestamp_to_local(timestamp_str, selected_timezone)
            line = line.replace(timestamp_str, converted_timestamp)

        converted_lines.append(line)

    output_file_prompt = "Enter the output file name (press Enter to use the default, type 'exit' to cancel): "
    output_file = sanitize_file_name(click.prompt(output_file_prompt, default=''))

    if output_file.lower() == 'exit':
        click.echo("Conversion canceled.")
        return

    if not output_file:
        output_file = f"{log_file}_converted_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

    with open(output_file, 'w') as file:
        file.writelines(converted_lines)

    click.echo(f"\nLog file converted and saved as: {output_file}")
    logger.info(f"Log file '{log_file}' converted and saved as: {output_file}")


def main():
    """Main function to run the program."""
    print(f"Timestamp Converter v{VERSION}")
    while True:
        print("\nMain Menu:")
        print(f"{MENU_OPTIONS['MANUAL']}. Manually Convert Timestamp")
        print(f"{MENU_OPTIONS['LOG_FILE']}. Convert Timestamps from Log File")
        print(f"{MENU_OPTIONS['EXIT']}. Exit")
        option = get_menu_option()

        if option == MENU_OPTIONS['EXIT']:
            print("Exiting the program.")
            logger.info("Program exited.")
            break

        if option == MENU_OPTIONS['MANUAL']:
            handle_manual_conversion()

        elif option == MENU_OPTIONS['LOG_FILE']:
            handle_log_file_conversion()


if __name__ == "__main__":
    main()
