import json
import cloudinary
import cloudinary.api

# 1. CONFIGURE YOUR READY CLOUDINARY CREDENTIALS
cloudinary.config(
    cloud_name = "dk9yhsklq",
    api_key = "864777795557874",          # Your real Root API Key
    api_secret = "gW4JmVP1aL8sG94MHdfXtnxzd-o", # Your real Root API Secret token
    secure = True
)

OUTPUT_FILE = "gallery_data.js"
TARGET_REMOTE_FOLDER = "gallery"

def scan_cloudinary_gallery():
    print("🌐 Connecting to Cloudinary Media Library...")
    memory_database = {}

    try:
        raw_resources = []
        
        # Fetch Images from Cloudinary
        print("📸 Scanning for images...")
        img_response = cloudinary.api.resources(
            type = "upload",
            prefix = f"{TARGET_REMOTE_FOLDER}/",
            max_results = 500
        )
        raw_resources.extend(img_response.get('resources', []))

        # Fetch Videos from Cloudinary
        print("🎥 Scanning for videos...")
        vid_response = cloudinary.api.resources(
            resource_type = "video",
            type = "upload",
            prefix = f"{TARGET_REMOTE_FOLDER}/",
            max_results = 500
        )
        raw_resources.extend(vid_response.get('resources', []))

        if not raw_resources:
            print("⚠️ No files found! Verify files are placed inside the 'gallery' folder on Cloudinary.")
            return

        # 3. Process and group assets dynamically
        for resource in raw_resources:
            public_id = resource.get('public_id', '')
            path_parts = public_id.split('/')
            
            if len(path_parts) >= 3:
                # Keeps 'BA', 'BCA', 'BCOM' matching your folder layout casing
                # Safely turns 'Cultural Fests' into 'Cultural_Fests' key token
                section = path_parts[1].replace(' ', '_')
                file_name = path_parts[2]
                
                if section not in memory_database:
                    memory_database[section] = []

                # Group classification tag
                media_type = 'video' if resource.get('resource_type') == 'video' else 'image'
                
                # Transform raw filenames into pretty captions
                clean_title = file_name.replace('_', ' ').replace('-', ' ').title()
                
                memory_database[section].append({
                    'type': media_type,
                    'src': resource.get('secure_url'), # Secure https link
                    'title': clean_title
                })

        # 4. Generate the uniform JSON array file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"// Automatically compiled via Cloudinary Engine API\n")
            f.write(f"const MemoryDatabase = {json.dumps(memory_database, indent=4)};")

        print("\n--- CLOUD SYNC SUMMARY ---")
        for sec, items in memory_database.items():
            print(f"📦 Section [{sec}]: Packaged {len(items)} items successfully.")
            
        print(f"\n✅ Build complete! '{OUTPUT_FILE}' has been populated with high-speed CDN URLs.")

    except Exception as e:
        print(f"❌ Error accessing Cloudinary API: {e}")
        print("Please double-check your API Key and Secret configurations.")

if __name__ == "__main__":
    scan_cloudinary_gallery()
