import argparse
import requests
import urllib.parse
import os
import sys
import time

class YandexDiskDownloader:
    def __init__(self, link=None, download_location=None):
        self.link = link
        self.download_location = download_location
        self.cancelled = False

    def download(self):
        try:
            print("\033[94mStarting download process...\033[0m\n")

            # Get the download URL and expected file size from the server
            url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
            print(f"\033[94mRequesting download URL and file information from: {url}\033[0m\n")
            response = requests.get(url)
            response.raise_for_status()
            download_info = response.json()

            download_url = download_info["href"]
            file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
            save_path = os.path.join(self.download_location, file_name)
            
            # Fetch file size from server
            server_size = self.get_file_size(download_url)
            
            if server_size is None:
                print("\033[91mFailed to fetch file size from server. Cannot proceed with download.\033[0m")
                return

            # Display file size on the server
            print(f"\033[94mFile size on server: {self.format_size(server_size)}\033[0m\n")

            # Check if the file already exists locally and get its size
            local_size = 0
            if os.path.exists(save_path):
                local_size = os.path.getsize(save_path)
                print(f"\033[93mFile '{file_name}' already exists locally with size: {self.format_size(local_size)}\033[0m")

            # Compare sizes and decide whether to resume or start fresh
            if local_size == server_size:
                print(f"\033[93mFile '{file_name}' already fully downloaded.\033[0m")
                return
            elif local_size > server_size:
                print(f"\033[93mFile '{file_name}' is larger than expected. Deleting and restarting download...\033[0m")
                os.remove(save_path)
                self.download_file(download_url, save_path, server_size)
                return
            else:
                if local_size > 0:
                    print(f"\033[93mResuming download of '{file_name}'...\033[0m")
                else:
                    print(f"\033[93mStarting download of '{file_name}'...\033[0m")

                self.download_file(download_url, save_path, server_size, headers={'Range': f'bytes={local_size}-'})

            print("\n\n\033[92mDownload complete.\033[0m")
        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mAn error occurred during the request: {e}\033[0m")
        except KeyboardInterrupt:
            self.cancelled = True
        except Exception as e:
            print(f"\n\033[91mAn unexpected error occurred: {e}\033[0m")

    def get_file_size(self, download_url):
        try:
            response = requests.head(download_url)
            response.raise_for_status()
            return int(response.headers.get('content-length', 0))
        except requests.exceptions.RequestException as e:
            print(f"\033[91mAn error occurred while fetching file size: {e}\033[0m")
            return None

    def download_file(self, download_url, save_path, total_size, headers=None):
        try:
            with open(save_path, "ab" if os.path.exists(save_path) else "wb") as file:
                print(f"\033[94mDownloading from: {download_url}\033[0m\n")

                download_response = requests.get(download_url, headers=headers, stream=True)
                download_response.raise_for_status()

                progress = os.path.getsize(save_path) if headers else 0
                start_time = time.time()
                chunk_size = 10240
                refresh_interval = 0.5  # Refresh progress every 0.5 second
                last_refresh_time = start_time
                last_progress = progress
                for chunk in download_response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        progress += len(chunk)
                        current_time = time.time()

                        # Calculate download speed and estimated time left
                        elapsed_time = current_time - start_time
                        if elapsed_time > 0:
                            download_speed = (progress - last_progress) / elapsed_time
                            time_left = (total_size - progress) / download_speed if download_speed > 0 else float('inf')
                        else:
                            time_left = float('inf')

                        # Display progress
                        if total_size > 0:
                            percentage = (progress / total_size) * 100
                            if current_time - last_refresh_time >= refresh_interval:
                                print_progress(progress, total_size, percentage, time_left)
                                last_refresh_time = current_time
                                last_progress = progress
                        else:
                            print(f"\r\033[94mDownloaded {self.format_size(progress)} so far\033[0m", end="")
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

        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mAn error occurred during the download: {e}\033[0m")

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


def print_progress(current, total, percentage, time_left):
    # Display download progress with estimated time left
    downloaded = YandexDiskDownloader().format_size(current)
    total_size = YandexDiskDownloader().format_size(total)
    time_left_str = format_time(time_left)
    progress = f"\r\033[94mDownload Progress: {percentage:.2f}% ({downloaded} / {total_size}) - Time Left: {time_left_str}         "
    sys.stdout.write(progress)
    sys.stdout.flush()


def format_time(seconds):
    # Convert seconds into human-readable format (HH:MM:SS)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL', required=True)
    parser.add_argument('-d', '--download_location', type=str, help='Download location on PC', required=True)
    args = parser.parse_args()

    downloader = YandexDiskDownloader(args.link, args.download_location)
    downloader.download()
