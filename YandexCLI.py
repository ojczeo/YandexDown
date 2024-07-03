import argparse
import requests
import urllib.parse
import os
import sys


class YandexDiskDownloader:
    def __init__(self, link, download_location):
        self.link = link
        self.download_location = download_location

    def download(self):
        try:
            print("\033[94mStarting download process...\033[0m\n")
            
            # Get the download URL
            url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
            print(f"\033[94mRequesting download URL from: {url}\033[0m\n")
            response = requests.get(url)
            response.raise_for_status()

            print("\033[92mSuccessfully obtained download URL.\033[0m\n")
            download_url = response.json()["href"]
            file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
            save_path = os.path.join(self.download_location, file_name)

            print(f"\033[94mFile will be saved to: {save_path}\033[0m\n")

            # Start downloading the file
            with open(save_path, "wb") as file:
                print(f"\033[94mDownloading from: {download_url}\033[0m\n")
                download_response = requests.get(download_url, stream=True)
                download_response.raise_for_status()

                # Get the total file size if available
                total_size = download_response.headers.get('content-length')
                if total_size:
                    total_size = int(total_size)
                    print(f"\033[94mTotal file size: {self.format_size(total_size)}\033[0m\n")

                    progress = 0
                    for chunk in download_response.iter_content(chunk_size=10240):
                        if chunk:
                            file.write(chunk)
                            progress += len(chunk)
                            percentage = (progress / total_size) * 100
                            print(f"\r\033[94mDownload Progress: {percentage:.2f}% ({self.format_size(progress)}/{self.format_size(total_size)})\033[0m", end="")
                            sys.stdout.flush()

                else:
                    print("\033[93mContent-Length header is missing. Downloading without progress indication.\033[0m\n")
                    total_downloaded = 0
                    for chunk in download_response.iter_content(chunk_size=10240):
                        if chunk:
                            file.write(chunk)
                            total_downloaded += len(chunk)
                            print(f"\r\033[94mDownloaded {self.format_size(total_downloaded)} so far\033[0m", end="")
                            sys.stdout.flush()

            print("\n\n\033[92mDownload complete.\033[0m")
        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mAn error occurred during the request: {e}\033[0m")
        except Exception as e:
            print(f"\n\033[91mAn unexpected error occurred: {e}\033[0m")

    def format_size(self, size):
        # Convert size to appropriate unit (KB, MB, GB)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL', required=True)
    parser.add_argument('-d', '--download_location', type=str, help='Download location on PC', required=True)
    args = parser.parse_args()

    downloader = YandexDiskDownloader(args.link, args.download_location)
    downloader.download()
