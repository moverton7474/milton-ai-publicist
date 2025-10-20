import zipfile
import os

# Create ZIP file containing TECH_STACK.md
zip_path = 'TECH_STACK.zip'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('TECH_STACK.md', 'TECH_STACK.md')

print(f'Created: {os.path.abspath(zip_path)}')
print(f'Size: {os.path.getsize(zip_path):,} bytes')
print(f'\nYou can now download this file from:')
print(f'   {os.path.abspath(zip_path)}')
