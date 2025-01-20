import tkinter as tk
from tkinter import filedialog
import qrcode
from PIL import Image, ImageTk
import time
import subprocess
import os
import threading
import traceback
import ngrok
import shutil
import platform
import sys
root = tk.Tk()
root.title("Sharing window")
import os,shutil
filename = 'http_server.py'

from tkinter.filedialog import SaveFileDialog,askdirectory
def cleanup_ports_background():
    def cleanup():
        print("Starting quick cleanup...")
        try:
            # Quick kill for ngrok - no waiting
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'], 
                             shell=True, 
                             stderr=subprocess.DEVNULL)
            else:  # Unix/Mac
                subprocess.run(['pkill', '-9', 'ngrok'], 
                             shell=True, 
                             stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Cleanup note: {e}")

    # Run cleanup without waiting
    thread = threading.Thread(target=cleanup)
    thread.daemon = True
    thread.start()

def get_python_command():
    """Dynamically determine the correct Python command"""
    try:
        # First check if we're running in Docker
        if os.path.exists('/.dockerenv'):
            return 'python'
        
        # Check if we're on Windows
        if platform.system() == 'Windows':
            # Try using sys.executable first (most reliable on Windows)
            if sys.executable:
                return sys.executable
            
            # Fallbacks for Windows
            try:
                subprocess.run(['py', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return 'py'
            except FileNotFoundError:
                try:
                    subprocess.run(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return 'python'
                except FileNotFoundError:
                    raise Exception("Python interpreter not found on Windows")
        else:
            # Unix-like systems
            try:
                subprocess.run(['python3', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return 'python3'
            except FileNotFoundError:
                try:
                    subprocess.run(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return 'python'
                except FileNotFoundError:
                    if sys.executable:
                        return sys.executable
                    raise Exception("No Python interpreter found")
    except Exception as e:
        print(f"Warning: Error detecting Python command: {e}")
        # Last resort: return sys.executable or 'python'
        return sys.executable if sys.executable else 'python'

# Replace the existing python_cmd line with:
python_cmd = get_python_command()
print(f"Using Python command: {python_cmd}")  # Debug line

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_ngrok_token():
    """Check if ngrok token exists and is valid"""
    token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ngrok_token.txt')
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return True
    except:
        pass
    return False

def open_token_dialog(callback=None):
    """Open dialog to get ngrok token"""
    dialog = tk.Toplevel()
    dialog.title("Ngrok Authentication Required")
    dialog.geometry("400x250")
    dialog.configure(bg='#2C2C2C')
    
    # Center the dialog
    dialog.transient(root)
    dialog.grab_set()
    
    # Instructions
    tk.Label(dialog, 
        text="Ngrok authentication required!",
        font=('Helvetica', 14, 'bold'),
        fg='#E8D5C4',
        bg='#2C2C2C',
        pady=10
    ).pack()
    
    tk.Label(dialog,
        text="1. Sign up at dashboard.ngrok.com/signup\n2. Get your authtoken from\ndashboard.ngrok.com/get-started/your-authtoken",
        font=('Helvetica', 10),
        fg='#E8D5C4',
        bg='#2C2C2C',
        justify='left',
        pady=10
    ).pack()
    
    # Get existing token if any
    token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ngrok_token.txt')
    current_token = ""
    try:
        with open(token_file, 'r') as f:
            current_token = f.read().strip()
    except:
        pass
    
    # Token entry with existing token if any
    token_var = tk.StringVar(value=current_token)
    entry = tk.Entry(dialog, textvariable=token_var, width=40)
    entry.pack(pady=10)
    
    def save_token():
        token = token_var.get().strip()
        if token:
            try:
                # Validate token before saving
                ngrok.set_auth_token(token)
                with open(token_file, 'w') as f:
                    f.write(token)
                dialog.destroy()
                if callback:
                    callback()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid token: {str(e)}")
        else:
            messagebox.showerror("Error", "Please enter a valid token")
    
    # Save button
    tk.Button(dialog,
        text="Save Token",
        command=save_token,
        bg='#3E6D9C',
        fg='black',
        font=('Helvetica', 12),
        pady=5,
        padx=20
    ).pack(pady=20)

def import_folder():
    if not check_ngrok_token():
        open_token_dialog(import_folder)
        return
        
    try:
        options = {
            "initialdir": os.path.expanduser("~"),
            "title": "Select a Folder"
        }

        global file_path
        file_path = askdirectory(**options)
        if not file_path:  # If user cancels selection
            return
            
        print(f"Selected path: {file_path}")
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = resource_path('http_server.py')
            url_file = os.path.join(script_dir, 'share_url.txt')
            
            # Clear any existing URL file
            if os.path.exists(url_file):
                os.remove(url_file)
            
            # Create new app instance with clean state
            change_page = app(root)
            change_page.url_file = url_file
            
            # Use the full path to Python interpreter when starting server
            cmd = [python_cmd, server_path, file_path, 'folder', url_file]
            print(f"Executing command: {' '.join(cmd)}")  # Debug print
            change_page.server_process = subprocess.Popen(cmd)
            
            change_page.page2()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            print(f"Command attempted: {python_cmd}")
            print(f"Full traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"Error in import_folder: {e}")

def import_file():
    if not check_ngrok_token():
        open_token_dialog(import_file)
        return
        
    try:
        global file_path
        files = filedialog.askopenfilenames(title="Select files to share", filetypes=[("All files", "*.*")])
        if not files:  # If user cancels selection
            return
            
        print(f"\nDebug: Selected files:")
        for file in files:
            print(f"- {file}")
        
        try:
            import subprocess
            script_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = resource_path('http_server.py')
            url_file = os.path.join(script_dir, 'share_url.txt')
            temp_dir = os.path.join(script_dir, 'temp_serve')
            
            print(f"\nDebug: Absolute paths:")
            print(f"Script dir: {os.path.abspath(script_dir)}")
            print(f"Server path: {os.path.abspath(server_path)}")
            print(f"Temp dir: {os.path.abspath(temp_dir)}")
            
            # Clear any existing URL file
            if os.path.exists(url_file):
                os.remove(url_file)
            
            # Clean and recreate temp directory
            if os.path.exists(temp_dir):
                print(f"Debug: Removing existing temp directory")
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            print(f"Debug: Created fresh temp directory at {os.path.abspath(temp_dir)}")
            
            # Copy all selected files to temp directory
            print("\nDebug: Copying files to temp directory:")
            for file_path in files:
                dest_path = os.path.join(temp_dir, os.path.basename(file_path))
                print(f"Copying {file_path} -> {dest_path}")
                shutil.copy2(file_path, dest_path)
                # Verify file was copied
                if os.path.exists(dest_path):
                    print(f"Successfully copied: {os.path.basename(dest_path)} ({os.path.getsize(dest_path)} bytes)")
                else:
                    print(f"Warning: Failed to copy {os.path.basename(file_path)}")
            
            # Verify files in temp directory
            print("\nDebug: Files in temp directory before server start:")
            temp_files = os.listdir(temp_dir)
            for file in temp_files:
                file_path = os.path.join(temp_dir, file)
                print(f"- {file} ({os.path.getsize(file_path)} bytes)")
            
            if not temp_files:
                raise Exception("No files were copied to temp directory")
            
            # Create new app instance with clean state
            change_page = app(root)
            change_page.url_file = url_file
            # Important: Change - we're serving from temp_dir but telling server it's a folder
            change_page.server_process = subprocess.Popen([python_cmd, server_path, temp_dir, 'folder', url_file])
            
            # Wait briefly to ensure server starts
            time.sleep(1)
            
            # Verify temp directory still exists and has files
            print("\nDebug: Verifying temp directory after server start:")
            if os.path.exists(temp_dir):
                files_after = os.listdir(temp_dir)
                print(f"Temp directory exists at {os.path.abspath(temp_dir)}")
                print(f"Files in temp_serve: {files_after}")
                for file in files_after:
                    file_path = os.path.join(temp_dir, file)
                    print(f"- {file} ({os.path.getsize(file_path)} bytes)")
            else:
                print(f"Warning: Temp directory no longer exists at {os.path.abspath(temp_dir)}!")
            
            change_page.page2()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"Error in import_file: {e}")
        print(f"Stack trace: {traceback.format_exc()}")

def open_settings():
    open_token_dialog()  # Reuse the same dialog for settings

class app:
    def __init__(self, master):
        self.master = master
        self.master.geometry("400x600")  
        self.master.configure(bg='#2C2C2C')  
        self.server_process = None
        self.qr_label = None
        self.url_file = None
        self.cleanup_done = False  # Add this flag
        self.page1()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        if self.cleanup_done:  # Prevent double cleanup
            self.master.destroy()
            return
            
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            cleanup_ports_background()
            self.cleanup_done = True
            
            # Don't wait - destroy immediately
            self.master.destroy()
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.master.destroy()
    
    def page1(self):
        for i in self.master.winfo_children():
            i.destroy()

        # Main frame with padding and dark cream background
        self.frame1 = tk.Frame(self.master, bg='#2A2829')
        self.frame1.pack(expand=True, fill='both', padx=20, pady=20)

        # Title with enhanced styling
        title = tk.Label(
            self.frame1, 
            text='Share Files Securely',
            font=('Helvetica', 24, 'bold'),
            fg='#E8D5C4',
            bg='#2A2829',
            pady=30
        )
        title.pack()

        # Container for buttons
        button_frame = tk.Frame(self.frame1, bg='#2A2829')
        button_frame.pack(expand=True)

        # Enhanced button styling
        button_style = {
            'font': ('Helvetica', 14),
            'width': 18,
            'height': 2,
            'bd': 0,
            'relief': 'flat',
            'cursor': 'hand2',
            'borderwidth': 0,
            'fg': 'black',
            'activeforeground': 'black'
        }

        button1 = tk.Button(
            button_frame,
            text="Share a File",
            command=import_file,
            bg='#3E6D9C',
            **button_style
        )
        button1.pack(pady=15)

        button2 = tk.Button(
            button_frame,
            text="Share a Folder",
            command=import_folder,
            bg='#3E6D9C',
            **button_style
        )
        button2.pack(pady=15)

        # Add Settings button
        settings_btn = tk.Button(
            button_frame,
            text="⚙️ Settings",
            command=open_settings,
            bg='#3E6D9C',
            font=('Helvetica', 12),
            width=12,
            height=1,
            bd=0,
            relief='flat',
            cursor='hand2',
            fg='black',
            activeforeground='black'
        )
        settings_btn.pack(pady=15)

        # Add authentication steps
        steps_text = """
How to get Authentication Token:
1. Sign up at dashboard.ngrok.com/signup
2. Get your token from dashboard.ngrok.com/get-started/your-authtoken
3. Click Settings and paste your token
        """
        
        steps_label = tk.Label(
            button_frame,
            text=steps_text,
            font=('Helvetica', 10),
            fg='#B0B0B0',
            bg='#2A2829',
            justify='left',
            pady=10
        )
        steps_label.pack(pady=5)

        # Modified hover effects
        def on_enter(e):
            e.widget['background'] = '#2B4865'

        def on_leave(e):
            if e.widget != settings_btn:  # Don't change settings button color
                e.widget['background'] = '#3E6D9C'

        # Add rounded corners and hover effects
        for button in (button1, button2):
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            button.configure(highlightthickness=0)
            radius = 15
            button.configure(relief='flat', borderwidth=0)

    def page2(self):
        for i in self.master.winfo_children():
            i.destroy()

        self.frame2 = tk.Frame(self.master, bg='#2A2829')
        self.frame2.pack(expand=True, fill='both', padx=20, pady=20)

        # Update title styling
        title_label = tk.Label(
            self.frame2,
            text="File Sharing Active",
            font=('Helvetica', 24, 'bold'),
            fg='#E8D5C4',
            bg='#2A2829',
            pady=20
        )
        title_label.pack()

        try:
            # Read URL with timeout
            url = None
            start_time = time.time()
            while time.time() - start_time < 10:
                if os.path.exists(self.url_file):
                    with open(self.url_file, 'r') as f:
                        url = f.read().strip()
                    if url:
                        break
                time.sleep(0.5)

            if not url:
                raise Exception("Could not get sharing URL")

            # Create a frame to hold URL and copy button horizontally
            url_frame = tk.Frame(self.frame2, bg='#2C2C2C')
            url_frame.pack(pady=(0, 20))

            url_text = tk.Label(
                url_frame,  # Changed parent to url_frame
                text=url,
                font=('Helvetica', 10),
                fg='#B0B0B0',
                bg='#2C2C2C',
                wraplength=300  # Slightly reduced to make space for button
            )
            url_text.pack(side='left', padx=(0, 10))

            def copy_url():
                self.master.clipboard_clear()
                self.master.clipboard_append(url)
                copy_btn.config(text="Copied!")
                # Reset button text after 2 seconds
                self.master.after(2000, lambda: copy_btn.config(text="Copy"))

            copy_btn = tk.Button(
                url_frame,
                text="Copy",
                command=copy_url,
                font=('Helvetica', 10),
                bg='#3E6D9C',
                fg='black',
                activeforeground='black',
                padx=10,
                relief='flat',
                cursor='hand2'
            )
            copy_btn.pack(side='left')

            # QR Code section
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="white", back_color="#2C2C2C")
            qr_image = qr_image.resize((250, 250))
            qr_photo = ImageTk.PhotoImage(qr_image)

            qr_title = tk.Label(
                self.frame2,
                text="Scan QR Code:",
                font=('Helvetica', 12, 'bold'),
                fg='#E0E0E0',
                bg='#2C2C2C'
            )
            qr_title.pack(pady=(0, 10))

            self.qr_label = tk.Label(self.frame2, image=qr_photo, bg='#2C2C2C')
            self.qr_label.image = qr_photo
            self.qr_label.pack(pady=10)

            # Share Another File button with improved styling
            def share_another():
                if self.server_process:
                    self.server_process.terminate()
                    self.server_process = None
                cleanup_ports_background()
                # Don't wait - switch pages immediately
                self.page1()

            share_btn = tk.Button(
                self.frame2,
                text="Share Another File",
                command=share_another,
                font=('Helvetica', 14, 'bold'),
                bg='#3E6D9C',
                fg='black',             # Force black text
                activeforeground='black',  # Keep black even when clicked
                padx=30,
                pady=12,
                relief='flat',
                cursor='hand2'
            )
            share_btn.pack(pady=30)

            # Modified hover effects (only changes background)
            def on_enter(e):
                e.widget['background'] = '#2B4865'

            def on_leave(e):
                e.widget['background'] = '#3E6D9C'

            share_btn.bind("<Enter>", on_enter)
            share_btn.bind("<Leave>", on_leave)

            # Update retry button if present
            if 'retry_btn' in locals():
                retry_btn.configure(
                    bg='#3E6D9C',
                    fg='black',
                    activeforeground='black',
                    font=('Helvetica', 12, 'bold')
                )

        except Exception as e:
            error_label = tk.Label(
                self.frame2,
                text=f"Error: {e}",
                font=('Helvetica', 12),
                fg='#FF6B6B',
                bg='#2C2C2C'
            )
            error_label.pack(pady=10)

            retry_btn = tk.Button(
                self.frame2,
                text="Try Again",
                command=self.page1,
                font=('Helvetica', 12),
                bg='#3D5A80',
                fg='white',
                padx=20,
                pady=10,
                relief='flat',
                cursor='hand2'
            )
            retry_btn.pack(pady=10)

    # def update_shared_content(self, path, is_file=False):
    #     print(f"\nAttempting to update shared content:")
    #     print(f"Path: {path}")
    #     print(f"Is file: {is_file}")
        
    #     if self.server_process and self.server_process.poll() is None:
    #         print("Server is running")
    #         try:
    #             # Update the server's directory
    #             script_dir = os.path.dirname(os.path.abspath(__file__))
    #             server_path = resource_path('http_server.py')
    #             print(f"Server path: {server_path}")
                
    #             # Use same URL file
    #             if not hasattr(self, 'url_file'):
    #                 self.url_file = os.path.join(script_dir, 'share_url.txt')
    #             print(f"URL file: {self.url_file}")
                
    #             # Update the server's directory
    #             print("Loading server module...")
    #             spec = importlib.util.spec_from_file_location("http_server", server_path)
    #             server_module = importlib.util.module_from_spec(spec)
    #             spec.loader.exec_module(server_module)
                
    #             print("Calling update_directory...")
    #             if server_module.MyHttpRequestHandler.update_directory(path, is_file):
    #                 print("Update successful, refreshing page...")
    #                 # Refresh the page to show current content
    #                 self.page2()
    #             else:
    #                 print("Update failed")
    #                 tk.messagebox.showerror("Error", "Failed to update shared content")
    #         except Exception as e:
    #             print(f"Error during update: {e}")
    #             print(f"Exception type: {type(e)}")
    #             print(f"Traceback: {traceback.format_exc()}")
    #             tk.messagebox.showerror("Error", f"Error updating shared content: {e}")
    #     else:
    #         print("Server not running")
    #         tk.messagebox.showerror("Error", "Server not running")

def get_port_command(port):
    """Get the appropriate command to check port based on OS"""
    if os.name == 'nt':  # Windows
        return f"netstat -ano | findstr :{port}"
    else:  # Unix/Linux/Mac
        return f"lsof -ti :{port}"

app(root)

root.mainloop()




import http.server
import socketserver
import os
import sys
import shutil
from pyngrok import ngrok
import signal
import json
import time
import subprocess
import io
import zipfile

PORT = 8000

# Add debug prints
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())

try:
    from pyngrok import ngrok
except ImportError as e:
    print("Failed to import pyngrok:", e)
    print("Installed packages:", os.listdir(os.path.dirname(os.__file__) + "/site-packages"))
    sys.exit(1)

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def list_directory(self, path):
        try:
            # List files and directories in current directory only
            items = os.listdir(path)
            files = []
            folders = []
            
            for item in items:
                if item != "index.html":
                    full_path = os.path.join(path, item)
                    if os.path.isfile(full_path):
                        files.append(item)
                    elif os.path.isdir(full_path):
                        folders.append(item)
            
            files.sort()
            folders.sort()

            # Create HTML content
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Shared Files from directory {os.path.basename(os.getcwd())}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: #f5f5f5;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .file-list {{
                        list-style: none;
                        padding: 0;
                    }}
                    .file-item {{
                        display: flex;
                        align-items: center;
                        padding: 10px;
                        border-bottom: 1px solid #eee;
                    }}
                    .file-name {{
                        flex-grow: 1;
                        margin-right: 10px;
                    }}
                    .download-btn {{
                        background: #4CAF50;
                        color: white;
                        padding: 8px 15px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        text-decoration: none;
                    }}
                    .download-btn:hover {{
                        background: #45a049;
                    }}
                    .download-all {{
                        display: block;
                        width: 200px;
                        margin: 20px auto;
                        text-align: center;
                        background: #2196F3;
                    }}
                    .download-all:hover {{
                        background: #1976D2;
                    }}
                    .download-all-files {{
                        display: block;
                        width: 200px;
                        margin: 10px auto;
                        text-align: center;
                        background: #FF5722;
                    }}
                    .download-all-files:hover {{
                        background: #F4511E;
                    }}
                    @media (max-width: 600px) {{
                        body {{
                            padding: 10px;
                        }}
                        .container {{
                            padding: 10px;
                        }}
                        .file-item {{
                            flex-direction: column;
                            align-items: flex-start;
                        }}
                        .download-btn {{
                            margin-top: 10px;
                        }}
                    }}
                </style>
                <script>
                    function downloadAllFiles() {{
                        const files = {str(files)};  // Only files, not folders
                        let delay = 0;
                        files.forEach(file => {{
                            setTimeout(() => {{
                                const link = document.createElement('a');
                                link.href = file;
                                link.download = file;
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }}, delay);
                            delay += 500;
                        }});
                    }}
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>Shared Files from directory {os.path.basename(os.getcwd())}</h1>
                    <ul class="file-list">
            '''

            # Add folders first
            for folder in folders:
                html += f'''
                <li class="file-item">
                    <span class="file-name">📁 {folder}/</span>
                </li>
                '''

            # Add files
            for file in files:
                html += f'''
                <li class="file-item">
                    <span class="file-name">📄 {file}</span>
                    <a href="{file}" class="download-btn" download>Download</a>
                </li>
                '''

            # Modified section: Show download options based on content
            html += '</ul>'
            
            # Show "Download All as ZIP" if there are any files OR folders
            if files or folders:
                html += f'''
                    <a href="download-all" class="download-btn download-all">Download All as ZIP</a>
                '''
            
            # Show "Download All Files" only if there are files
            if files:
                html += f'''
                    <a href="#" onclick="downloadAllFiles()" class="download-btn download-all-files">Download All Files</a>
                '''
            
            html += '</div>'

            html += '''
            </body>
            </html>
            '''

            # Send response
            encoded = html.encode('utf-8', 'replace')
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return None

        except Exception as e:
            print(f"Error in list_directory: {e}")
            return super().list_directory(path)

    def do_GET(self):
        # Block any path traversal attempts
        if '..' in self.path or '//' in self.path:
            self.send_error(403, "Access denied")
            return  #these three lines are for security
        
        if self.path == '/download-all':
            try:
                # Get the current directory name
                current_dir = os.path.basename(os.getcwd())
                zip_filename = f"{current_dir}.zip"
                
                # Create ZIP file in memory
                memory_file = io.BytesIO()
                with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                    # Add all files in current directory to ZIP
                    for root, dirs, files in os.walk(os.getcwd()):
                        for file in files:
                            if file != "index.html":  # Skip index.html
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.getcwd())
                                zf.write(file_path, arcname)

                # Get ZIP file content
                memory_file.seek(0)
                content = memory_file.getvalue()

                # Send ZIP file with directory name
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename="{zip_filename}"')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                return

            except Exception as e:
                print(f"Error creating ZIP: {e}")
                self.send_error(500, "Internal server error")
                return

        return super().do_GET()

def start_ngrok(port):
    try:
        # First try to get token from environment variable
        auth_token = os.getenv('NGROK_AUTH_TOKEN')
        
        # If no environment variable, try to read from a local file
        if not auth_token:
            token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ngrok_token.txt')
            try:
                with open(token_file, 'r') as f:
                    auth_token = f.read().strip()
            except FileNotFoundError:
                # Create a dialog window for token input
                dialog = tk.Toplevel()
                dialog.title("Ngrok Authentication Required")
                dialog.geometry("400x250")
                dialog.configure(bg='#2C2C2C')
                
                # Center the dialog
                dialog.transient(root)
                dialog.grab_set()
                
                # Instructions
                tk.Label(dialog, 
                    text="Ngrok authentication required!",
                    font=('Helvetica', 14, 'bold'),
                    fg='#E8D5C4',
                    bg='#2C2C2C',
                    pady=10
                ).pack()
                
                tk.Label(dialog,
                    text="1. Sign up at dashboard.ngrok.com/signup\n2. Get your authtoken from\ndashboard.ngrok.com/get-started/your-authtoken",
                    font=('Helvetica', 10),
                    fg='#E8D5C4',
                    bg='#2C2C2C',
                    justify='left',
                    pady=10
                ).pack()
                
                # Token entry
                token_var = tk.StringVar()
                entry = tk.Entry(dialog, textvariable=token_var, width=40)
                entry.pack(pady=10)
                
                def save_token():
                    token = token_var.get().strip()
                    if token:
                        try:
                            # Validate token before saving
                            ngrok.set_auth_token(token)
                            with open(token_file, 'w') as f:
                                f.write(token)
                            dialog.token = token
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"Invalid token: {str(e)}")
                    else:
                        messagebox.showerror("Error", "Please enter a valid token")
                
                # Save button
                tk.Button(dialog,
                    text="Save Token",
                    command=save_token,
                    bg='#3E6D9C',
                    fg='black',
                    font=('Helvetica', 12),
                    pady=5,
                    padx=20
                ).pack(pady=20)
                
                # Wait for dialog
                dialog.wait_window()
                
                # Get token from dialog
                auth_token = getattr(dialog, 'token', None)
        
        if not auth_token:
            raise Exception("No ngrok authentication token provided")
            
        # Kill any existing ngrok processes first
        cleanup_ports_background()
            
        # Set the auth token
        ngrok.set_auth_token(auth_token)
        
        # Configure ngrok to use a single session
        ngrok.get_ngrok_process().stop_monitor_thread()
        
        # Open an Ngrok tunnel on the specified port
        https_url = ngrok.connect(port, "http").public_url
        print(f"\nNgrok Tunnel URL: {https_url}")
        print("Visit the Ngrok dashboard at http://127.0.0.1:4040 to inspect requests.")
        return https_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None

def start_server(path, type_of_share, url_file, callback=None):
    """Modified version of start_server that works with the UI"""
    print("\nStarting server setup...")
    
    if not path:
        print("No path selected!")
        return False
    
    # Kill any existing ngrok processes first
    cleanup_ports_background()
    
    print(f"Preparing to serve from directory: {path}")
    os.chdir(path)
    
    # Start ngrok with retries
    print("Starting ngrok tunnel...")
    public_url = start_ngrok(PORT)
    
    if not public_url:
        print("Failed to start ngrok tunnel")
        return False
    
    # Write the URL to the specified file
    print(f"Writing URL to file: {url_file}")
    with open(url_file, 'w') as f:
        f.write(public_url)

    print("Starting HTTP server...")
    try:
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", PORT), MyHttpRequestHandler)
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"\nLocal server running at: http://localhost:{PORT}")
        print(f"Public URL: {public_url}")
        
        if callback:
            callback(httpd)
        return httpd
        
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 3:
        start_server(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python http_server.py <path> <type> <url_file>")
        print("type can be 'file' or 'folder'")
        sys.exit(1)