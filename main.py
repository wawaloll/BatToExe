import os
import sys
import tempfile
import subprocess
import shutil
import time

def check_pyinstaller_installed():
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def install_pyinstaller():
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def create_python_script(batch_file):
    with open(batch_file, 'r') as file:
        batch_content = file.read()

    python_script = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
    with open(python_script.name, 'w') as file:
        file.write(f"""import os
import tempfile

temp_batch_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bat')
with open(temp_batch_file.name, 'w') as f:
    f.write('''{batch_content}''')

os.system(temp_batch_file.name)
os.remove(temp_batch_file.name)
os.system('pause')
""")

    return python_script.name

def remove_folder_with_retry(folder_path, max_retries=5, delay=1):
    for retry in range(max_retries):
        try:
            shutil.rmtree(folder_path)
            break
        except PermissionError as e:
            if retry < max_retries - 1:
                print(f"Failed to remove {folder_path}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

def convert_to_exe(batch_file):
    python_script = create_python_script(batch_file)
    exe_name = os.path.splitext(os.path.basename(batch_file))[0] + '.exe'
    exe_name = exe_name.replace('\\', '/')
    os.system(f'pyinstaller --onefile --console -n "{exe_name}" "{python_script}"')
    os.unlink(python_script)
    
 
    base_dir = os.path.dirname(os.path.abspath(batch_file))
    exe_path = os.path.join(base_dir, 'dist', exe_name)
    destination_path = os.path.join(base_dir, exe_name)

    if os.path.isfile(exe_path):
        
        if os.path.isfile(destination_path):
            os.remove(destination_path)

        shutil.move(exe_path, base_dir)
        
       
        for file_path in os.listdir(os.path.join(base_dir, 'dist')):
            file_path = os.path.join(base_dir, 'dist', file_path)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

 
        dist_folder = os.path.join(base_dir, 'dist')
        remove_folder_with_retry(dist_folder)
 
        build_folder = os.path.join(base_dir, 'build')
        remove_folder_with_retry(build_folder)


        spec_file = os.path.join(base_dir, f"{os.path.splitext(os.path.basename(batch_file))[0]}.spec")
        if os.path.isfile(spec_file):
            os.remove(spec_file)
    else:
        print(f"Failed to generate executable for {batch_file}")

if __name__ == '__main__':
    if not check_pyinstaller_installed():
        install_pyinstaller()
        print("Installed pyinstaller. Please run the script again.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python main.py <batch_file>")
        sys.exit(1)

    batch_file = sys.argv[1]
    convert_to_exe(batch_file)
