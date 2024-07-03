import argparse
import requests
import urllib.parse
import os
import sys
import time


class YandexDiskDownloader:
    def __init__(self, link, download_location):
        self.link = link
        self.download_location = download_location
        self.cancelled = False

    def download(self):
        try:
            print("\033[94mStarting download process...\033[0m\n")

            # Get the download URL and expected file size
            url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
            print(f"\033[94mRequesting download URL from: {url}\033[0m\n")
            response = requests.get(url)
            response.raise_for_status()
            download_info = response.json()
            
            download_url = download_info["href"]
            file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
            save_path = os.path.join(self.download_location, file_name)
            total_size = int(download_info.get("size", 0))

            # Check if the file already exists and its size matches the expected total size
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                if file_size == 0:
                    print(f"\033[93mFile '{file_name}' exists but its size is 0 bytes. Deleting and restarting download...\033[0m")
                    os.remove(save_path)
                    self.restart_download(download_url, save_path)
                    return
                elif file_size >= total_size:
                    print(f"\033[93mFile '{file_name}' already fully downloaded.\033[0m")
                    return
                else:
                    print(f"\033[93mResuming download of '{file_name}'...\033[0m")
                    print(f"\033[94mAlready downloaded: {self.format_size(file_size)}\033[0m")
                    headers = {'Range': f'bytes={file_size}-'}
            else:
                headers = None

            print(f"\033[94mFile will be saved to: {save_path}\033[0m\n")

            # Start downloading the file
            with open(save_path, "ab" if os.path.exists(save_path) else "wb") as file:
                print(f"\033[94mDownloading from: {download_url}\033[0m\n")
                
                download_response = requests.get(download_url, headers=headers, stream=True)
                download_response.raise_for_status()

                progress = os.path.getsize(save_path)
                start_time = time.time()
                chunk_size = 10240
                for chunk in download_response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        progress += len(chunk)
                        elapsed_time = time.time() - start_time

                        # Display progress
                        if total_size > 0:
                            percentage = (progress / total_size) * 100
                            print_progress(progress, total_size, percentage, elapsed_time)
                        else:
                            print(f"\r\033[94mDownloaded {format_size(progress)} so far\033[0m", end="")
                            sys.stdout.flush()

                        # Check if user wants to cancel download
                        if self.cancelled:
                            confirm_cancel = input("\n\n\033[91mDo you really want to cancel the download? (y/n): \033[0m").strip().lower()
                            if confirm_cancel == 'y':
                                print("\n\033[91mDownload cancelled by user.\033[0m")
                                return
                            else:
                                self.cancelled = False  # Reset cancelled flag
                                print("\033[94mResuming download...\033[0m")

            print("\n\n\033[92mDownload complete.\033[0m")
        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mAn error occurred during the request: {e}\033[0m")
        except KeyboardInterrupt:
            self.cancelled = True
        except Exception as e:
            print(f"\n\033[91mAn unexpected error occurred: {e}\033[0m")

    def restart_download(self, download_url, save_path):
        try:
            with open(save_path, "wb") as file:
                download_response = requests.get(download_url, stream=True)
                download_response.raise_for_status()

                for chunk in download_response.iter_content(chunk_size=10240):
                    if chunk:
                        file.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mAn error occurred during the download restart: {e}\033[0m")

    def format_size(self, size):
        # Convert size to appropriate unit (KB, MB, GB)
        if size is None:
            return "Unknown"
        elif size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"


def print_progress(current, total, percentage, elapsed_time):
    # Display download progress with estimated time left
    downloaded = format_size(current)
    total_size = format_size(total)
    progress = f"\r\033[94mDownload Progress: {percentage:.2f}% ({downloaded} / {total_size}) - Elapsed Time: {elapsed_time:.1f}s"
    sys.stdout.write(progress)
    sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL', required=True)
    parser.add_argument('-d', '--download_location', type=str, help='Download location on PC', required=True)
    args = parser.parse_args()

    downloader = YandexDiskDownloader(args.link, args.download_location)
    downloader.download()
