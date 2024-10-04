# extendEwayBill Automation

This Python script automates the process of extending E-way bills on the Indian GST E-way bill system. It uses Selenium WebDriver to interact with the website's interface programmatically.

## Features

- **Automated Login**: The script automatically logs into the E-way bill system using provided credentials.
- **E-way Bill Extension**: The script reads E-way bill numbers and vehicle numbers from a text file, and then extends each E-way bill on the website.
- **Form Filling**: The script automatically fills in necessary details on the extension form, such as vehicle number, transhipment details, and adjusted distance.
- **Submission**: After filling in the details, the script submits the form to complete the extension process.

## Usage

To use this script, you need to have Python and Selenium WebDriver installed on your machine. You also need to have a text file named "eway.txt" in the same directory as the script. This file should contain the E-way bill numbers and vehicle numbers, with each pair separated by a comma and each pair on a new line.

Please note that this script is configured to use Firefox as the web browser. If you want to use a different browser, you will need to modify the WebDriver initialization in the script.

## Disclaimer

This script is intended for educational purposes and automating personal tasks. Please ensure you have the necessary permissions to automate interactions with the E-way bill system. The author is not responsible for any misuse or any issues arising from the use of this script.
