Certainly! Here's the combined README file that integrates information from both the original repository ([SecFathy/YandexDown](https://github.com/SecFathy/YandexDown)) and your modified script:

---

# Yandex Disk Downloader

This Python script downloads files from Yandex Disk using the public link provided. It handles downloading large files and displays download progress when possible.

## Based on

This script is based on the original implementation by [SecFathy](https://github.com/SecFathy/YandexDown). It has been modified and enhanced for improved functionality and ease of use.

## Requirements

- Python 3.x
- Required Python packages (`requests`)

Install required packages using pip:
```bash
pip install requests
```

## Installation

Clone the repository:
```bash
git clone https://github.com/your/repository.git
cd repository
```

## Usage

To use the script, follow these steps:

1. Run the following command in your terminal:

```bash
python yandex_disk_downloader.py -l <Yandex Disk public link> -d <download location>
```

Replace `<Yandex Disk public link>` with the public link of the file you want to download from Yandex Disk.
Replace `<download location>` with the directory path where you want to save the downloaded file.

Example:
```bash
python yandex_disk_downloader.py -l https://disk.yandex.com/d/public_key123 -d /path/to/save/location
```

2. Press Enter and wait for the download to complete.

## Features

- Handles large file downloads efficiently.
- Displays download progress dynamically when possible.
- Checks if the file already exists before attempting to download it again.
- Error handling for network issues and other exceptions.

## Notes

- If the `content-length` header is missing in the server response, the script will download the file without displaying progress.
- Ensure you have sufficient disk space and a stable internet connection for downloading large files.
