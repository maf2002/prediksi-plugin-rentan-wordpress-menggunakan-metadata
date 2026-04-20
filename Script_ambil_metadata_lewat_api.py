import requests
from datetime import datetime
import zipfile
import os
import csv
import math
import time

DATASET_FILE = "wordpress_plugin_dataset.csv"

def get_existing_slugs(filename="wordpress_plugin_dataset.csv"):
    if not os.path.isfile(filename):
        return set()

    existing_slugs = set()

    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_slugs.add(row["slug"])

    return existing_slugs

def read_slugs_from_file(filename="2378-4000_V_data.csv"):
    with open(filename, "r", encoding="utf-8") as f:
        slugs = [line.strip() for line in f if line.strip()]
    return slugs

def get_plugin_metadata(slug):
    url = "https://api.wordpress.org/plugins/info/1.2/"

    params = {
        "action": "plugin_information",
        "request[slug]": slug,
        "request[fields][downloaded]": True,
        "request[fields][rating]": True,
        "request[fields][ratings]": True,
        "request[fields][active_installs]": True,
        "request[fields][last_updated]": True,
        "request[fields][tested]": True,
        "request[fields][requires]": True,
        "request[fields][support_threads]": True,
        "request[fields][support_threads_resolved]": True,
        "request[fields][added]": True,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("[ERROR] Gagal mengambil metadata")
        return None

    plugin = response.json()

    total_downloads = plugin.get("downloaded", 0)
    rating_user = plugin.get("rating", 0)
    num_reviewers = plugin.get("num_ratings", 0)

    last_updated_raw = plugin.get("last_updated")

    if last_updated_raw:
        date_only = last_updated_raw.split(" ")[0]
        last_updated = datetime.strptime(date_only, "%Y-%m-%d")

        last_update_year = max(
            math.floor((datetime.now() - last_updated).days / 365),
            1
        )

        freq_update_per_year = round(1 / last_update_year, 3)
    else:
        last_update_year = None
        freq_update_per_year = None

    added_raw = plugin.get("added")

    if added_raw:
        age_year = added_raw.split(" ")[0]
        added = datetime.strptime(age_year, "%Y-%m-%d")

        plugin_age_since_release = max(
            math.floor((datetime.now() - added).days / 365),
            1
        )
    else:
        plugin_age_since_release = None

    threads = plugin.get("support_threads", 0)
    resolved = plugin.get("support_threads_resolved", 0)

    if threads > 0:
        support_response_rate = round(resolved / threads, 2)
    else:
        support_response_rate = 0

    open_issues = threads - resolved

    return {
        "slug": slug,
        "total_downloads": total_downloads,
        "rating_user": rating_user,
        "num_reviewers": num_reviewers,
        "plugin_age_since_release": plugin_age_since_release,
        "last_update_year": last_update_year,
        "freq_update_per_year": freq_update_per_year,
        "wp_requires": plugin.get("requires"),
        "wp_tested": plugin.get("tested"),
        "support_response_rate": support_response_rate,
        "open_issues": open_issues
    }


def download_and_analyze_plugin(slug, base_dir="plugins"):
    os.makedirs(base_dir, exist_ok=True)

    zip_url = f"https://downloads.wordpress.org/plugin/{slug}.latest-stable.zip"
    zip_path = os.path.join(base_dir, f"{slug}.zip")
    extract_path = os.path.join(base_dir, slug)

    response = requests.get(zip_url, stream=True)
    if response.status_code != 200:
        print(f"[ERROR] Gagal download plugin: {slug}")
        return None

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    total_files = 0
    php_files = 0
    loc = 0
    total_size = 0

    for root, _, files in os.walk(extract_path):
        for file in files:
            file_path = os.path.join(root, file)
            total_files += 1
            total_size += os.path.getsize(file_path)

            if file.endswith(".php"):
                php_files += 1
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        loc += sum(1 for line in f if line.strip())
                except:
                    pass

    os.remove(zip_path)

    return {
        "num_files": total_files,
        "num_php_files": php_files,
        "loc": loc,
        "plugin_size_kb": round(total_size / 1024, 2)
    }


def save_to_csv(data, filename=DATASET_FILE):
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


# ==========================
# MAIN PROGRAM
# ==========================
if __name__ == "__main__":

    import time

    slugs = read_slugs_from_file("2378-4000_V_data.csv")
    existing_slugs = get_existing_slugs()

    print(f"Found {len(existing_slugs)} existing plugins in dataset.")

    for slug in slugs:

        if slug in existing_slugs:
            print(f"Skipping (already exists): {slug}")
            continue

        print(f"\nProcessing: {slug}")

        metadata = get_plugin_metadata(slug)
        code_metrics = download_and_analyze_plugin(slug)

        if metadata and code_metrics:
            combined_data = {**metadata, **code_metrics}
            save_to_csv(combined_data)

            print("\n=== WORDPRESS PLUGIN DATASET ===")
            print(f"Slug                    : {slug}")
            print(f"Total Unduhan           : {metadata['total_downloads']}")
            print(f"Rating Pengguna         : {metadata['rating_user']}")
            print(f"Jumlah Reviewer         : {metadata['num_reviewers']}")
            print(f"Umur Plugin (tahun)     : {metadata['plugin_age_since_release']}")
            print(f"Last Update (tahun)     : {metadata['last_update_year']}")
            print(f"Frekuensi Update/Tahun  : {metadata['freq_update_per_year']}")
            print(f"Versi WP Minimal        : {metadata['wp_requires']}")
            print(f"Versi WP Terakhir Uji   : {metadata['wp_tested']}")
            print(f"Support Response Rate   : {metadata['support_response_rate']}")
            print(f"Issue Belum Selesai     : {metadata['open_issues']}")
            print(f"Jumlah File             : {code_metrics['num_files']}")
            print(f"Jumlah File PHP         : {code_metrics['num_php_files']}")
            print(f"Lines of Code (LOC)     : {code_metrics['loc']}")
            print(f"Ukuran Plugin (KB)      : {code_metrics['plugin_size_kb']}")

            print(f"{slug} successfully added to dataset.")
        else:
            print(f"Failed to process {slug}")

        time.sleep(2)  # prevent API rate limit

    print(f"Pengumpulan data selesai.")