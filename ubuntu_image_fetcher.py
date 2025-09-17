import requests
import os
from urllib.parse import urlparse
import hashlib  # For duplicate detection (Challenge Q3)

def generate_filename_from_url(url):
    """Extract filename from URL or generate a default one."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or '.' not in filename:
        # Generate generic name if none found
        ext = get_extension_from_content_type(None)  # Fallback in main logic
        filename = f"downloaded_image{ext}"
    return filename

def get_extension_from_content_type(content_type):
    """Map common content types to file extensions."""
    if not content_type:
        return ".jpg"  # Default fallback
    mapping = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/bmp': '.bmp',
        'image/tiff': '.tiff',
        'image/svg+xml': '.svg'
    }
    return mapping.get(content_type, '.bin')

def is_duplicate_image(content, directory="Fetched_Images"):
    """Check if image content already exists in directory (Challenge Q3)."""
    content_hash = hashlib.md5(content).hexdigest()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                existing_hash = hashlib.md5(f.read()).hexdigest()
                if existing_hash == content_hash:
                    return True, filename
    return False, None

def download_image(url):
    """Download a single image with Ubuntu spirit: respect, community, sharing."""
    print(f"\nAttempting to fetch: {url}")

    try:
        # Respect: Set headers to identify ourselves and respect robots.txt norms
        headers = {
            'User-Agent': 'UbuntuImageFetcher/1.0 (+https://github.com/yourusername/Ubuntu_Requests)',
            'Accept': 'image/*'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Check important headers (Challenge Q4)
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"⚠️  Warning: URL does not appear to serve an image (Content-Type: {content_type})")
            # Still proceed if user insists? For now, we warn but continue.

        # Generate filename
        filename = generate_filename_from_url(url)
        # If no extension, infer from Content-Type
        if '.' not in filename:
            ext = get_extension_from_content_type(content_type)
            filename += ext

        # Check for duplicates (Challenge Q3)
        is_dup, existing_file = is_duplicate_image(response.content)
        if is_dup:
            print(f"♻️  Duplicate detected! Already saved as: {existing_file}")
            return

        # Create directory if needed
        os.makedirs("Fetched_Images", exist_ok=True)
        filepath = os.path.join("Fetched_Images", filename)

        # Prevent overwrites by appending numbers if file exists
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1

        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.Timeout:
        print("✗ Connection timed out. The community is vast — try again later.")
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect. Check the URL or your network.")
    except requests.exceptions.HTTPError as e:
        print(f"✗ Server responded with error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Network-related error: {e}")
    except PermissionError:
        print("✗ Permission denied: Cannot write to directory.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    urls_input = input("Please enter image URL(s) separated by commas: ").strip()
    urls = [url.strip() for url in urls_input.split(',') if url.strip()]

    if not urls:
        print("No URLs provided. Exiting gracefully.")
        return

    for url in urls:
        download_image(url)

    print("\n🌍 Connection strengthened. Community enriched. Thank you for sharing mindfully.")

if __name__ == "__main__":
    main()