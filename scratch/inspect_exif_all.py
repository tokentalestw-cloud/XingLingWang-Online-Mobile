import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

base_dir = 'C:/Users/a2132/Downloads/星靈王圖片/藝術品'
if not os.path.exists(base_dir):
    print("Directory not found:", base_dir)
    sys.exit(0)

files = [f for f in os.listdir(base_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"Total files: {len(files)}")

for f_name in files[:10]:
    path = os.path.join(base_dir, f_name)
    print(f"\n--- {f_name} ---")
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                print("No EXIF")
                continue
            for tag_id in exif:
                tag = TAGS.get(tag_id, tag_id)
                data = exif.get(tag_id)
                if isinstance(data, bytes):
                    for enc in ['utf-8', 'gbk', 'utf-16', 'big5']:
                        try:
                            data = data.decode(enc)
                            break
                        except Exception:
                            pass
                print(f"  {tag}: {repr(data)}")
    except Exception as e:
        print("Error:", e)
