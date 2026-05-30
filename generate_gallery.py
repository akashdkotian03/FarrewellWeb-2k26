import json
import cloudinary
import cloudinary.api

# 1. CONFIGURE YOUR CLOUDINARY CREDENTIALS (Get these from your Dashboard)
cloudinary.config(
    cloud_name = "YOUR_CLOUD_NAME",
    api_key = "YOUR_API_KEY",
    api_secret = "YOUR_API_SECRET",
    secure = True
)

OUTPUT_FILE = "gallery_data.js"
TARGET_REMOTE_FOLDER = "gallery" # The main folder we created in Cloudinary

def scan_cloudinary_gallery():
    print("🌐 Connecting to Cloudinary Media Library...")
    memory_database = {}

    try:
        # 2. Fetch all resources (images and videos) from Cloudinary
        # We set max_results to 500 to catch large memory collections in one go
        raw_resources = []
        
        # Fetch Images
        img_response = cloudinary.api.resources(
            type = "upload",
            prefix = f"{TARGET_REMOTE_FOLDER}/",
            max_results = 500
        )
        raw_resources.extend(img_response.get('resources', []))

        # Fetch Videos
        vid_response = cloudinary.api.resources(
            resource_type = "video",
            type = "upload",
            prefix = f"{TARGET_REMOTE_FOLDER}/",
            max_results = 500
        )
        raw_resources.extend(vid_response.get('resources', []))

        if not raw_resources:
            print("⚠️ No files found in your Cloudinary 'gallery/' folder. Check your upload paths!")
            return

        # 3. Sort and group files into their subfolder sections
        for resource in raw_resources:
            public_id = resource.get('public_id', '')
            
            # Split path (e.g., "gallery/bca/class_pic") to isolate the subfolder name
            path_parts = public_id.split('/')
            if len(path_parts) >= 3:
                section = path_parts[1].lower() # This grabs 'bca', 'nss', etc.
                file_name = path_parts[2]
                
                if section not in memory_database:
                    memory_database[section] = []

                # Determine dynamic media category type
                media_type = 'video' if resource.get('resource_type') == 'video' else 'image'
                
                # Format clean visual captions out of raw filenames
                clean_title = file_name.replace('_', ' ').replace('-', ' ').title()
                
                memory_database[section].append({
                    'type': media_type,
                    'src': resource.get('secure_url'), # High-speed CDN streaming link
                    'title': clean_title
                })

        # 4. Write data structure smoothly to local js file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"// Automatically compiled via Cloudinary Engine API\n")
            f.write(f"const MemoryDatabase = {json.dumps(memory_database, indent=4)};")

        print("\n--- SCAN SUMMARY ---")
        for sec, items in memory_database.items():
            print(f"📦 Section [{sec.upper()}]: Synced {len(items)} files from Cloudinary.")
            
        print(f"\n✅ Build complete! '{OUTPUT_FILE}' is ready for deployment.")

    except Exception as e:
        print(f"❌ Error accessing Cloudinary API: {e}")
        print("Please double-check your Cloud Name, API Key, and Secret.")

if __name__ == "__main__":
    scan_cloudinary_gallery()