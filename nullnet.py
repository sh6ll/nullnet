# -*- coding: utf-8 -*-

import io
import json
import os
import requests
import re
import html
import time
import random
from datetime import datetime
import platform
import subprocess
import sys
import threading  # Still needed for both modes

# Global variables to hold GUI modules when imported
tk = None
ttk = None
scrolledtext = None

########################
# CROSS-PLATFORM BEEPING
########################
SYSTEM = platform.system()

ERROR_BEEP_FREQ   = 600  # Hz
ERROR_BEEP_LENGTH = 150  # ms

def beep_linux(freq_hz, duration_ms):
    try:
        subprocess.run(["beep", "-f", str(freq_hz), "-l", str(duration_ms)], check=False)
    except FileNotFoundError:
        pass
    except Exception:
        pass

def beep_windows(freq_hz, duration_ms):
    # Only import winsound when needed on Windows
    if SYSTEM == "Windows":
        try:
            import winsound
            winsound.Beep(freq_hz, duration_ms)
        except ImportError:
            pass

def beep_error():
    """Plays a short beep on error if the platform supports it."""
    if SYSTEM == "Windows":
        try:
            beep_windows(ERROR_BEEP_FREQ, ERROR_BEEP_LENGTH)
        except:
            pass
    elif SYSTEM == "Linux":
        beep_linux(ERROR_BEEP_FREQ, ERROR_BEEP_LENGTH)

# Add this function near the top of the file, after imports
def is_display_available():
    """Check if a display server is available (for GUI)"""
    # Check if running on Linux or Unix-like system
    if SYSTEM == "Windows":
        return True  # Windows always has a display
    
    # For Linux/Unix, check if DISPLAY is set
    if 'DISPLAY' in os.environ and os.environ['DISPLAY']:
        try:
            # Try importing Tkinter as a test
            import tkinter
            test_root = tkinter.Tk()
            test_root.destroy()
            return True
        except:
            return False
    return False

# Function to import GUI modules only when needed
def import_gui_modules():
    global tk, ttk, scrolledtext
    if tk is None:  # Only import if not already imported
        try:
            import tkinter as tk
            from tkinter import ttk, scrolledtext
            return True
        except ImportError:
            return False
    return True

# Add this terminal-only version of the app
class TerminalOnlyApp:
    """Terminal-only version of the HIBP scanner that visually resembles the GUI version"""
    def __init__(self):
        # Terminal colors using ANSI escape codes
        self.COLORS = {
            "reset": "\033[0m",
            "text": "\033[92m",      # Green text
            "accent": "\033[96m",    # Cyan for accent
            "warning": "\033[91m",   # Red for warnings
            "header": "\033[97m",    # Bright white for headers
            "dim": "\033[2m",        # Dimmed text
            "bold": "\033[1m",       # Bold text
            "underline": "\033[4m",  # Underlined text
            "bg": "\033[40m",        # Black background
        }
        
        # Check if terminal supports colors
        self.use_colors = True
        try:
            # Check if we're in a terminal that supports colors
            if not sys.stdout.isatty():
                self.use_colors = False
        except:
            self.use_colors = False
            
        # Clear screen and display header
        self.clear_screen()
        self.display_welcome_message()
        
        # State variables
        self.email = ""
        self.breach = ""
        self.api_key = os.environ.get('HIBP_API_KEY', '')
        
        # Main loop
        self.run()
        
    def color_text(self, text, color_code):
        """Apply color to text if colors are enabled"""
        if self.use_colors:
            return f"{color_code}{text}{self.COLORS['reset']}"
        return text
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if SYSTEM == 'Windows' else 'clear')
        
    def display_welcome_message(self):
        """Display the welcome message with ASCII art header"""
        header = self.color_text("""
╔══════════════════════════════════════════════════════╗
║   NULLNET SCANNER                                    ║
║   SECURITY BREACH DETECTION SYSTEM v1.0.3            ║
║   POWERED BY: HAVE I BEEN PWNED API                  ║
║   CLASSIFICATION: CONFIDENTIAL                       ║
╚══════════════════════════════════════════════════════╝
""", self.COLORS["header"])
        
        status = self.color_text("""
SYSTEM INITIALIZED...
NETWORK CONNECTION: ESTABLISHED
DATABASE ACCESS: GRANTED
SECURITY PROTOCOLS: ACTIVE
""", self.COLORS["text"])
        
        mode_info = self.color_text("""
TERMINAL MODE ACTIVE - GUI UNAVAILABLE
VISUAL COMPATIBILITY MODE ENABLED
""", self.COLORS["accent"])
        
        instructions = self.color_text("""
READY TO SCAN FOR SECURITY BREACHES.
""", self.COLORS["text"])
        
        print(header)
        print(status)
        print(mode_info)
        print(instructions)
        
    def draw_interface(self):
        """Draw the main interface layout"""
        self.clear_screen()
        
        # Header section
        print(self.color_text("╔══════════════════════════════════════════════════════════════════════════╗", self.COLORS["header"]))
        header_text = "NULLNET"
        subtitle = "SECURITY BREACH DETECTION SYSTEM"
        status = "[ ONLINE ]"
        
        # Calculate spacing to position the status indicator on the right
        total_width = 70
        left_part = f"{header_text}    {subtitle}"
        padding = total_width - len(left_part) - len(status)
        
        print(self.color_text(f"║ {self.color_text(header_text, self.COLORS['bold'])}    {subtitle}{' ' * padding}{status} ║", self.COLORS["header"]))
        print(self.color_text("╠══════════════════════════════════════════════════════════════════════════╣", self.COLORS["header"]))
        
        # Input section (left panel)
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        print(self.color_text("║  " + self.color_text("SCAN PARAMETERS:", self.COLORS["bold"]) + "                                                     ║", self.COLORS["header"]))
        print(self.color_text("║  ───────────────────────────────────────────                            ║", self.COLORS["header"]))
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        print(self.color_text(f"║  EMAIL ADDRESS:                                                          ║", self.COLORS["header"]))
        print(self.color_text(f"║  {self.color_text(self.email if self.email else '<Enter email to scan>', self.COLORS['text'])}                       ║", self.COLORS["header"]))
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        print(self.color_text(f"║  BREACH NAME (OPTIONAL):                                                 ║", self.COLORS["header"]))
        print(self.color_text(f"║  {self.color_text(self.breach if self.breach else '<Enter breach to lookup>', self.COLORS['text'])}                  ║", self.COLORS["header"]))
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        print(self.color_text(f"║  HIBP API KEY:                                                           ║", self.COLORS["header"]))
        
        # Show API key status
        if self.api_key:
            api_display = "********" + self.api_key[-4:] if len(self.api_key) > 4 else "********"
            print(self.color_text(f"║  {self.color_text(api_display, self.COLORS['text'])}                                                  ║", self.COLORS["header"]))
        else:
            print(self.color_text(f"║  {self.color_text('<API key required>', self.COLORS['warning'])}                                           ║", self.COLORS["header"]))
        
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        print(self.color_text("║  " + self.color_text("[1] INITIATE SCAN", self.COLORS["accent"]) + "    " + self.color_text("[2] CLEAR", self.COLORS["accent"]) + "    " + self.color_text("[0] EXIT", self.COLORS["accent"]) + "                    ║", self.COLORS["header"]))
        print(self.color_text("║                                                                          ║", self.COLORS["header"]))
        
        # Status bar at bottom
        date_str = datetime.now().strftime("%Y.%m.%d")
        time_str = datetime.now().strftime("%H:%M:%S")
        datetime_display = f"DATE: {date_str} | TIME: {time_str}"
        
        status_text = "SYSTEM READY"
        padding = total_width - len(status_text) - len(datetime_display)
        
        print(self.color_text("╠══════════════════════════════════════════════════════════════════════════╣", self.COLORS["header"]))
        print(self.color_text(f"║ {status_text}{' ' * padding}{datetime_display} ║", self.COLORS["header"]))
        print(self.color_text("╚══════════════════════════════════════════════════════════════════════════╝", self.COLORS["header"]))
        
    def run(self):
        """Main application loop"""
        while True:
            self.draw_interface()
            
            print("\nEnter option (1-Scan, 2-Clear, 0-Exit):", end=" ")
            choice = input().strip()
            
            if choice == "0":
                print(self.color_text("\nShutting down NULLNET Scanner...", self.COLORS["accent"]))
                break
            elif choice == "1":
                self.prepare_scan()
            elif choice == "2":
                # Just redraw the interface
                continue
            else:
                print(self.color_text("\nInvalid option. Press Enter to continue...", self.COLORS["warning"]))
                input()
                
    def prepare_scan(self):
        """Prepare for scanning by collecting necessary information"""
        self.clear_screen()
        self.draw_interface()
        
        # First collect API key if not already set
        if not self.api_key:
            print("\nHIBP API Key required.")
            import getpass
            self.api_key = getpass.getpass("Enter HIBP API key: ")
            if not self.api_key:
                print(self.color_text("\nError: API key is required. Press Enter to continue...", self.COLORS["warning"]))
                input()
                return
        
        # Now collect email or breach name
        print("\nEnter scan parameters (leave blank to skip):")
        self.email = input("Email address to scan: ").strip()
        if not self.email:
            self.breach = input("Breach name to lookup: ").strip()
            
        if not self.email and not self.breach:
            print(self.color_text("\nError: Email or breach name is required. Press Enter to continue...", self.COLORS["warning"]))
            input()
            return
        
        # Update the interface to show entered values
        self.clear_screen()
        self.draw_interface()
        
        # Now perform the scan
        self.perform_scan()
        
    def perform_scan(self):
        """Perform the actual scan and display results"""
        self.clear_screen()
        
        # Display a terminal-like header
        print(self.color_text("╔══════════════════════════════════════════════════════╗", self.COLORS["header"]))
        print(self.color_text("║   TERMINAL OUTPUT                                    ║", self.COLORS["header"]))
        print(self.color_text("╚══════════════════════════════════════════════════════╝", self.COLORS["header"]))
        print()
        
        headers = {
            "hibp-api-key": self.api_key,
            "User-Agent": "NULLNETSecurityScanner/1.0"
        }
        
        print(self.color_text(">>> INITIATING SCAN...", self.COLORS["accent"]))
        time.sleep(0.5)
        
        # If email is provided
        if self.email:
            print(self.color_text(f"\n>>> SCANNING EMAIL: {self.email}", self.COLORS["header"]))
            time.sleep(0.5)
            
            folder_name = self.email.replace("@", "_at_").replace(".", "_dot_")
            os.makedirs(folder_name, exist_ok=True)
            
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.email}"
            try:
                print(self.color_text(">>> CONNECTING TO HIBP DATABASE...", self.COLORS["text"]))
                time.sleep(0.5)
                
                resp = requests.get(url, headers=headers)
                
                if resp.status_code == 404:
                    # 404 on this endpoint means "no breaches found"
                    beep_error()
                    print(self.color_text("\n>>> SCAN COMPLETE: NO BREACHES FOUND", self.COLORS["accent"]))
                    print("\nPress Enter to continue...")
                    input()
                    return
                    
                resp.raise_for_status()
                
                breach_list = resp.json()
                if not breach_list:
                    print(self.color_text("\n>>> SCAN COMPLETE: NO BREACHES FOUND", self.COLORS["accent"]))
                    print("\nPress Enter to continue...")
                    input()
                    return
                
                print(self.color_text(f"\n>>> ALERT: FOUND {len(breach_list)} BREACH(ES)", self.COLORS["warning"]))
                time.sleep(0.5)
                
                for breach_info in breach_list:
                    breach_name = breach_info["Name"]
                    print(self.color_text(f"\n>>> RETRIEVING DETAILS FOR: {breach_name}", self.COLORS["accent"]))
                    time.sleep(0.3)
                    
                    breach_url = f"https://haveibeenpwned.com/api/v3/breach/{breach_name}"
                    br_resp = requests.get(breach_url, headers=headers)
                    br_resp.raise_for_status()
                    
                    breach_data = br_resp.json()
                    
                    json_filename = os.path.join(folder_name, f"{breach_name}.json")
                    with open(json_filename, "w", encoding="utf-8") as outfile:
                        json.dump(breach_data, outfile, indent=2)
                    print(self.color_text(f">>> SAVED: {json_filename}", self.COLORS["text"]))
                    
                    self.display_breach_summary(breach_data)
                
                print(self.color_text("\n>>> SCAN COMPLETE", self.COLORS["accent"]))
                print(self.color_text(f">>> ALL DATA SAVED TO FOLDER: {folder_name}", self.COLORS["text"]))
                
            except requests.exceptions.RequestException as e:
                beep_error()
                print(self.color_text(f"\n>>> ERROR: {str(e)}", self.COLORS["warning"]))
        
        # If breach is provided
        if self.breach:
            print(self.color_text(f"\n>>> RETRIEVING BREACH: {self.breach}", self.COLORS["header"]))
            time.sleep(0.5)
            
            single_breach_url = f"https://haveibeenpwned.com/api/v3/breach/{self.breach}"
            try:
                print(self.color_text(">>> CONNECTING TO HIBP DATABASE...", self.COLORS["text"]))
                time.sleep(0.5)
                
                resp = requests.get(single_breach_url, headers=headers)
                
                if resp.status_code == 404:
                    beep_error()
                    print(self.color_text(f"\n>>> BREACH '{self.breach}' NOT FOUND", self.COLORS["warning"]))
                    print("\nPress Enter to continue...")
                    input()
                    return
                    
                resp.raise_for_status()
                
                breach_data = resp.json()
                
                json_filename = f"{self.breach}.json"
                with open(json_filename, "w", encoding="utf-8") as outfile:
                    json.dump(breach_data, outfile, indent=2)
                print(self.color_text(f">>> SAVED: {json_filename}", self.COLORS["text"]))
                
                self.display_breach_summary(breach_data)
                
                print(self.color_text("\n>>> SCAN COMPLETE", self.COLORS["accent"]))
                
            except requests.exceptions.RequestException as e:
                beep_error()
                print(self.color_text(f"\n>>> ERROR: {str(e)}", self.COLORS["warning"]))
        
        print("\nPress Enter to continue...")
        input()
    
    def display_breach_summary(self, breach_data):
        """Display breach summary in a box format similar to the GUI"""
        box_width = 60
        top_border = "╔" + "═" * (box_width - 2) + "╗"
        mid_border = "╠" + "═" * (box_width - 2) + "╣"
        bot_border = "╚" + "═" * (box_width - 2) + "╝"

        # Top border
        print(self.color_text("\n" + top_border, self.COLORS["header"]))

        # Centered title
        title_str = "BREACH DETAILS"
        centered_title = title_str.center(box_width - 4)
        print(self.color_text(f"║ {centered_title} ║", self.COLORS["header"]))

        # Mid border
        print(self.color_text(mid_border, self.COLORS["header"]))

        # Key lines (Name, Title, etc.)
        lines = [
            ("Name", breach_data.get("Name", "N/A")),
            ("Title", breach_data.get("Title", "N/A")),
            ("Domain", breach_data.get("Domain", "N/A")),
            ("Breach Date", breach_data.get("BreachDate", "N/A")),
            ("Added Date", breach_data.get("AddedDate", "N/A")),
            ("Modified", breach_data.get("ModifiedDate", "N/A")),
            ("Pwn Count", breach_data.get("PwnCount", "N/A")),
        ]
        
        for label, value in lines:
            label_text = f"{label}:"
            line_str = f"{label_text:<12} {value}"
            padded = line_str.ljust(box_width - 4)
            print(self.color_text(f"║ {padded} ║", self.COLORS["text"]))

        # Data classes
        data_classes = breach_data.get('DataClasses', [])
        print(self.color_text(f"║ {'Data Classes:'.ljust(box_width - 4)} ║", self.COLORS["text"]))
        for cls in data_classes:
            padded = f"  - {cls}".ljust(box_width - 4)
            print(self.color_text(f"║ {padded} ║", self.COLORS["text"]))

        verified = breach_data.get('IsVerified', 'N/A')
        fabricated = breach_data.get('IsFabricated', 'N/A')
        print(self.color_text(f"║ {f'Verified:    {verified}'.ljust(box_width - 4)} ║", self.COLORS["text"]))
        print(self.color_text(f"║ {f'Fabricated:  {fabricated}'.ljust(box_width - 4)} ║", self.COLORS["text"]))

        # Blank line
        print(self.color_text(f"║ {' '.ljust(box_width - 4)} ║", self.COLORS["text"]))
        # DESCRIPTION header
        print(self.color_text(f"║ {'DESCRIPTION:'.ljust(box_width - 4)} ║", self.COLORS["text"]))

        # Description (may be long)
        description = breach_data.get('Description', '')
        description_cleaned = re.sub(r'<[^>]*>', '', description)
        description_cleaned = html.unescape(description_cleaned)
        
        # Wrap description text to fit inside the box
        import textwrap
        wrapper = textwrap.TextWrapper(width=box_width - 4)
        wrapped_text = wrapper.wrap(text=description_cleaned)
        
        for line in wrapped_text:
            padded = line.ljust(box_width - 4)
            print(self.color_text(f"║ {padded} ║", self.COLORS["text"]))

        # Bottom border
        print(self.color_text(bot_border, self.COLORS["header"]))

############################
# COLOR SCHEME & CONSTANTS
############################
COLORS = {
    "bg": "#0a0a0a",           
    "text": "#33ff33",         
    "accent": "#66ff66",       
    "warning": "#ff3333",      
    "header": "#aaffaa",       
    "panel": "#111111",        
    "border": "#225522",       
    "button": "#113311",       
    "button_active": "#225522",
    "scrollbar": "#33ff33",    # Green scrollbar color
    "scrollbar_bg": "#0a0a0a", # Scrollbar background
    "titlebar": "#111111",     # Title bar background
    "titlebar_text": "#33ff33" # Title bar text
}


############################
# Custom Scrollbar Class - Only loaded when GUI is used
############################
def define_gui_classes():
    global GreenScrollbar, CustomTitleBar, TerminalText, HIBPScannerApp
    
    class GreenScrollbar(tk.Canvas):
        """Custom scrollbar with green styling"""
        def __init__(self, parent, **kwargs):
            tk.Canvas.__init__(self, parent, **kwargs)
            self.config(bg=COLORS["scrollbar_bg"], highlightthickness=0, bd=0)
            
            # Create the slider
            self.slider = self.create_rectangle(0, 0, 0, 0, fill=COLORS["scrollbar"], outline="")
            
            # Bind events
            self.bind("<ButtonPress-1>", self.on_press)
            self.bind("<ButtonRelease-1>", self.on_release)
            self.bind("<B1-Motion>", self.on_motion)
            
            # Scrolling target and parameters
            self.target = None
            self.pressed = False
            self.start_y = 0
            self.start_value = 0
            
            # Bind mouse wheel for scrolling
            self.bind("<MouseWheel>", self.on_mousewheel)  # Windows
            self.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
            self.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
            
        def set_target(self, widget):
            """Set the widget to be scrolled"""
            self.target = widget
            self.update_view()
            
        def update_view(self):
            """Update the slider position and size based on the target's scroll position"""
            if not self.target:
                return
                
            try:
                # Get scroll position
                first, last = self.target.yview()
                
                # Calculate slider position and size
                height = self.winfo_height()
                slider_height = max(20, height * (last - first))
                slider_y = height * first
                
                # Update slider
                self.coords(self.slider, 2, slider_y, self.winfo_width() - 2, slider_y + slider_height)
            except:
                pass
        
        # This is the method that will be called by the text widget's yscrollcommand
        def update_slider(self, first, last):
            """Update the slider position based on the scroll values"""
            if not self.winfo_exists():
                return
                
            try:
                # Calculate slider position and size
                height = self.winfo_height()
                slider_height = max(20, height * (last - first))
                slider_y = height * first
                
                # Update slider
                self.coords(self.slider, 2, slider_y, self.winfo_width() - 2, slider_y + slider_height)
            except:
                pass
                
        def on_press(self, event):
            """Handle mouse press on the scrollbar"""
            self.pressed = True
            self.start_y = event.y
            if self.target:
                self.start_value = self.target.yview()[0]
                
        def on_release(self, event):
            """Handle mouse release"""
            self.pressed = False
            
        def on_motion(self, event):
            """Handle mouse drag on the scrollbar"""
            if not self.pressed or not self.target:
                return
                
            # Calculate new position
            delta_y = event.y - self.start_y
            height = self.winfo_height()
            delta_fraction = delta_y / height
            
            # Move the target's view
            new_pos = max(0, min(1, self.start_value + delta_fraction))
            self.target.yview_moveto(new_pos)
            
            # Update slider
            self.update_view()
            
        def on_mousewheel(self, event):
            """Handle mouse wheel scrolling"""
            if not self.target:
                return
                
            # Determine scroll direction and amount
            if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
                # Scroll up
                self.target.yview_scroll(-1, "units")
            elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
                # Scroll down
                self.target.yview_scroll(1, "units")
                
            # Update slider
            self.update_view()


    ############################
    # Custom Title Bar
    ############################
    class CustomTitleBar(tk.Frame):
        """Custom title bar with maximize and close buttons"""
        def __init__(self, parent, title="", **kwargs):
            tk.Frame.__init__(self, parent, **kwargs)
            self.parent = parent
            self.title = title
            
            # Configure appearance
            self.config(bg=COLORS["titlebar"], height=30)
            
            # Create title label
            self.title_label = tk.Label(
                self, 
                text=title,
                bg=COLORS["titlebar"],
                fg=COLORS["titlebar_text"],
                font=('Consolas', 10, 'bold')
            )
            self.title_label.pack(side=tk.LEFT, padx=10)
            
            # Create control buttons frame
            self.controls_frame = tk.Frame(self, bg=COLORS["titlebar"])
            self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Close button (X)
            self.close_button = tk.Label(
                self.controls_frame,
                text="✕",
                bg=COLORS["titlebar"],
                fg=COLORS["text"],
                font=('Consolas', 12),
                padx=10,
                pady=2
            )
            self.close_button.pack(side=tk.RIGHT)
            self.close_button.bind("<Button-1>", self.close_window)
            self.close_button.bind("<Enter>", lambda e: self.close_button.config(fg=COLORS["warning"]))
            self.close_button.bind("<Leave>", lambda e: self.close_button.config(fg=COLORS["text"]))
            
            # Maximize button (□)
            self.maximize_button = tk.Label(
                self.controls_frame,
                text="□",
                bg=COLORS["titlebar"],
                fg=COLORS["text"],
                font=('Consolas', 12),
                padx=10,
                pady=2
            )
            self.maximize_button.pack(side=tk.RIGHT)
            self.maximize_button.bind("<Button-1>", self.toggle_maximize)
            self.maximize_button.bind("<Enter>", lambda e: self.maximize_button.config(fg=COLORS["accent"]))
            self.maximize_button.bind("<Leave>", lambda e: self.maximize_button.config(fg=COLORS["text"]))
            
            # Bind events for window dragging
            self.bind("<ButtonPress-1>", self.start_move)
            self.title_label.bind("<ButtonPress-1>", self.start_move)
            self.bind("<ButtonRelease-1>", self.stop_move)
            self.title_label.bind("<ButtonRelease-1>", self.stop_move)
            self.bind("<B1-Motion>", self.do_move)
            self.title_label.bind("<B1-Motion>", self.do_move)
            
            # Window state tracking
            self.maximized = False
            self.normal_geometry = None
            
        def start_move(self, event):
            """Start window dragging"""
            self.x = event.x
            self.y = event.y
            
        def stop_move(self, event):
            """Stop window dragging"""
            self.x = None
            self.y = None
            
        def do_move(self, event):
            """Move the window during drag"""
            if self.maximized:
                # Don't allow dragging when maximized
                return
                
            deltax = event.x - self.x
            deltay = event.y - self.y
            
            x = self.parent.winfo_x() + deltax
            y = self.parent.winfo_y() + deltay
            self.parent.geometry(f"+{x}+{y}")
            
        def close_window(self, event):
            """Close the window"""
            self.parent.destroy()
            
        def toggle_maximize(self, event):
            """Toggle between maximized and normal window state"""
            if self.maximized:
                # Restore to normal size
                if self.normal_geometry:
                    self.parent.geometry(self.normal_geometry)
                self.maximized = False
            else:
                # Save current geometry and maximize
                self.normal_geometry = self.parent.geometry()
                
                # Temporarily disable override-redirect before setting fullscreen
                self.parent.overrideredirect(False)
                self.parent.update()
                
                # Now set fullscreen
                self.parent.attributes('-fullscreen', True)
                self.maximized = True
                
                # Re-enable override-redirect
                self.parent.overrideredirect(True)


    ############################
    # Terminal-like text output
    ############################
    class TerminalText:
        """
        Handles 'typing' text into a Tkinter ScrolledText widget
        to mimic an old-school terminal output.
        """
        def __init__(self, text_widget):
            self.text_widget = text_widget
            # Adjust these if you dislike the "typewriter" animation speed.
            # Increased typing speed by 25% (multiplied by 0.75)
            self.typing_speed = 0.00089 * 0.75
            self.typing_variation = 0.003 * 0.75
            
            # Flag to track if auto-scrolling is enabled
            self.auto_scroll = True
            
            # Store the last visible position
            self.last_visible_position = 1.0
            
            # Bind scroll events to detect manual scrolling
            self.text_widget.bind("<Button-4>", self._on_manual_scroll)  # Linux scroll up
            self.text_widget.bind("<Button-5>", self._on_manual_scroll)  # Linux scroll down
            self.text_widget.bind("<MouseWheel>", self._on_manual_scroll)  # Windows
            self.text_widget.bind("<B1-Motion>", self._on_manual_scroll)  # Drag scrollbar
            
            # Bind key events that might cause scrolling
            self.text_widget.bind("<Up>", self._on_manual_scroll)
            self.text_widget.bind("<Down>", self._on_manual_scroll)
            self.text_widget.bind("<Prior>", self._on_manual_scroll)  # Page Up
            self.text_widget.bind("<Next>", self._on_manual_scroll)   # Page Down
            self.text_widget.bind("<Home>", self._on_manual_scroll)
            self.text_widget.bind("<End>", self._on_manual_scroll)

        def _on_manual_scroll(self, event=None):
            """Detect manual scrolling and disable auto-scroll"""
            # Get current view position
            try:
                first, last = self.text_widget.yview()
                # If we're not at the bottom, disable auto-scrolling
                if last < 1.0:
                    self.auto_scroll = False
                    # Store the current position
                    self.last_visible_position = first
                else:
                    # If we're at the bottom, re-enable auto-scrolling
                    self.auto_scroll = True
            except:
                pass
            
            # Allow the event to propagate
            return None

        def _check_if_at_bottom(self):
            """Check if the view is at the bottom of the text widget"""
            try:
                first, last = self.text_widget.yview()
                return last >= 0.99  # Consider "almost at bottom" as "at bottom"
            except:
                return True

        def _update_scroll_state(self):
            """Update the auto-scroll state based on current view position"""
            if self._check_if_at_bottom():
                self.auto_scroll = True
            else:
                self.auto_scroll = False
                first, _ = self.text_widget.yview()
                self.last_visible_position = first

        def type_text(self, text, tag=None):
            """Type text character by character with a typewriter effect"""
            self.text_widget.config(state=tk.NORMAL)
            
            # Check if we're at the bottom before starting to type
            self._update_scroll_state()
            
            # Remember the initial position
            initial_auto_scroll = self.auto_scroll
            
            for char in text:
                # Insert the character
                self.text_widget.insert(tk.END, char, tag)
                
                # Only auto-scroll if it was enabled at the start of typing
                # and hasn't been manually changed during typing
                if initial_auto_scroll and self.auto_scroll:
                    self.text_widget.see(tk.END)
                elif not self.auto_scroll:
                    # Maintain the scroll position where the user left it
                    self.text_widget.yview_moveto(self.last_visible_position)
                    
                # Update the UI
                self.text_widget.update()
                
                # Add delay for typewriter effect
                delay = self.typing_speed + random.uniform(0, self.typing_variation)
                time.sleep(delay)
            
            # Make sure the text widget is read-only again
            self.text_widget.config(state=tk.DISABLED)
            
        def clear(self):
            """Clear the text widget and reset auto-scroll"""
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.config(state=tk.DISABLED)
            self.auto_scroll = True
            
        def append(self, text, tag=None):
            """Append text without typewriter effect"""
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, text, tag)
            
            # Only auto-scroll if enabled
            if self.auto_scroll:
                self.text_widget.see(tk.END)
                
            self.text_widget.config(state=tk.DISABLED)


    ############################
    # Main HIBPScannerApp Class
    ############################
    class HIBPScannerApp:
        def __init__(self, root):
            self.root = root
            self.root.title("NULLNET - SECURITY BREACH SCANNER")
            self.root.geometry("1000x700")
            self.root.configure(bg=COLORS["bg"])
            
            # Center the window on the screen
            self.center_window()
            
            # Remove window decorations
            self.root.overrideredirect(True)
            
            # Configure widget styles
            self.configure_styles()
            
            # Create custom title bar
            self.title_bar = CustomTitleBar(
                root, 
                title="NULLNET - SECURITY BREACH SCANNER",
                bg=COLORS["titlebar"]
            )
            self.title_bar.pack(fill=tk.X)
            
            # Main frame
            self.main_frame = tk.Frame(root, bg=COLORS["bg"])
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create the UI
            self.create_header()
            self.create_content()
            self.create_status_bar()
            
            # Terminal object
            self.terminal = TerminalText(self.output_text)
            
            # Initial welcome message
            self.display_welcome_message()
            
            # Status indicator blink
            self.online_visible = True
            self.update_status()
        
        def center_window(self):
            """Center the window on the screen"""
            # Get screen width and height
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Get window width and height
            window_width = 1000
            window_height = 700
            
            # Calculate position coordinates
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Set the window position
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        def configure_styles(self):
            style = ttk.Style()
            style.theme_use('alt')
            
            style.configure(
                'Terminal.TButton',
                background=COLORS["button"],
                foreground=COLORS["text"],
                borderwidth=1,
                relief="raised",
                font=('Consolas', 10, 'bold')
            )
            style.map(
                'Terminal.TButton',
                background=[('active', COLORS["button_active"])],
                relief=[('pressed', 'sunken')]
            )
            
            style.configure(
                'Terminal.TEntry',
                fieldbackground=COLORS["panel"],
                foreground=COLORS["text"],
                insertcolor=COLORS["text"],
                borderwidth=1,
                relief="sunken",
                font=('Consolas', 10)
            )
            
            style.configure(
                'Terminal.TLabel',
                background=COLORS["bg"],
                foreground=COLORS["text"],
                font=('Consolas', 10)
            )
            
            style.configure(
                'Header.TLabel',
                background=COLORS["bg"],
                foreground=COLORS["header"],
                font=('Consolas', 16, 'bold')
            )

        def create_header(self):
            header_frame = tk.Frame(self.main_frame, bg=COLORS["bg"], height=60)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            header_frame.pack_propagate(False)
            
            # Title
            self.header_label = ttk.Label(
                header_frame, 
                text="NULLNET",
                style='Header.TLabel'
            )
            self.header_label.pack(side=tk.LEFT, padx=10)
            
            # Subtitle
            subtitle = ttk.Label(
                header_frame,
                text="SECURITY BREACH DETECTION SYSTEM",
                style='Terminal.TLabel'
            )
            subtitle.pack(side=tk.LEFT, padx=10)
            
            # "[ ONLINE ]"
            self.status_indicator = ttk.Label(
                header_frame,
                text="[ ONLINE ]",
                style='Terminal.TLabel'
            )
            self.status_indicator.pack(side=tk.RIGHT, padx=10)
            
            # Separator
            sep = ttk.Separator(self.main_frame, orient='horizontal')
            sep.pack(fill=tk.X, pady=(0, 10))

        def create_content(self):
            content_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Left panel (input fields)
            input_frame = tk.LabelFrame(
                content_frame,
                text="SCAN PARAMETERS",
                bg=COLORS["bg"],
                fg=COLORS["text"],
                font=('Consolas', 10, 'bold'),
                bd=1,
                relief=tk.GROOVE,
                highlightbackground=COLORS["border"],
                highlightcolor=COLORS["border"],
                highlightthickness=1,
                padx=10,
                pady=10
            )
            input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
            
            # Email
            email_frame = tk.Frame(input_frame, bg=COLORS["bg"])
            email_frame.pack(fill=tk.X, pady=5)
            email_label = ttk.Label(email_frame, text="EMAIL ADDRESS:", style='Terminal.TLabel')
            email_label.pack(anchor=tk.W)
            
            self.email_var = tk.StringVar()
            self.email_entry = ttk.Entry(
                email_frame,
                textvariable=self.email_var,
                style='Terminal.TEntry',
                width=30
            )
            self.email_entry.pack(fill=tk.X, pady=5)
            
            # Breach
            breach_frame = tk.Frame(input_frame, bg=COLORS["bg"])
            breach_frame.pack(fill=tk.X, pady=5)
            breach_label = ttk.Label(breach_frame, text="BREACH NAME (OPTIONAL):", style='Terminal.TLabel')
            breach_label.pack(anchor=tk.W)
            
            self.breach_var = tk.StringVar()
            self.breach_entry = ttk.Entry(
                breach_frame,
                textvariable=self.breach_var,
                style='Terminal.TEntry',
                width=30
            )
            self.breach_entry.pack(fill=tk.X, pady=5)
            
            # API key
            api_frame = tk.Frame(input_frame, bg=COLORS["bg"])
            api_frame.pack(fill=tk.X, pady=5)
            api_label = ttk.Label(api_frame, text="HIBP API KEY:", style='Terminal.TLabel')
            api_label.pack(anchor=tk.W)
            
            self.api_var = tk.StringVar()
            self.last_api_value = ""
            
            self.api_entry = tk.Entry(
                api_frame,
                textvariable=self.api_var,
                width=30,
                show="*",
                bg=COLORS["panel"],
                fg=COLORS["text"],
                insertbackground=COLORS["text"],
                highlightthickness=1,
                highlightcolor=COLORS["border"],
                relief="sunken",
                font=('Consolas', 10)
            )
            self.api_entry.pack(fill=tk.X, pady=5)
            
            self.api_entry.bind("<Key>", self.record_api_value_before_change)
            self.api_entry.bind("<FocusIn>", self.record_api_value_before_change)
            self.api_entry.bind("<Control-z>", self.undo_api)
            
            self.show_api = tk.BooleanVar(value=False)
            show_api_check = tk.Checkbutton(
                api_frame,
                text="SHOW KEY",
                variable=self.show_api,
                bg=COLORS["bg"],
                fg=COLORS["text"],
                selectcolor=COLORS["panel"],
                activebackground=COLORS["bg"],
                activeforeground=COLORS["accent"],
                font=('Consolas', 8),
                command=self.toggle_api_visibility
            )
            show_api_check.pack(anchor=tk.W)
            
            # Buttons
            button_frame = tk.Frame(input_frame, bg=COLORS["bg"])
            button_frame.pack(fill=tk.X, pady=10)
            
            scan_button = ttk.Button(
                button_frame,
                text="INITIATE SCAN",
                style='Terminal.TButton',
                command=self.start_scan
            )
            scan_button.pack(side=tk.LEFT, padx=5)
            
            clear_button = ttk.Button(
                button_frame,
                text="CLEAR TERMINAL",
                style='Terminal.TButton',
                command=self.clear_terminal
            )
            clear_button.pack(side=tk.LEFT, padx=5)
            
            # Right panel (terminal output) with custom scrollbar
            output_frame = tk.LabelFrame(
                content_frame,
                text="TERMINAL OUTPUT",
                bg=COLORS["bg"],
                fg=COLORS["text"],
                font=('Consolas', 10, 'bold'),
                bd=1,
                relief=tk.GROOVE,
                highlightbackground=COLORS["border"],
                highlightcolor=COLORS["border"],
                highlightthickness=1,
                padx=10,
                pady=10
            )
            output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
            
            # Create a frame to hold the text and scrollbar
            text_container = tk.Frame(output_frame, bg=COLORS["bg"])
            text_container.pack(fill=tk.BOTH, expand=True)
            
            # Create the text widget without scrollbar
            self.output_text = tk.Text(
                text_container,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                insertbackground=COLORS["text"],
                font=('Consolas', 10),
                wrap="none",
                width=60,
                height=20,
                bd=0,
                highlightthickness=0
            )
            self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create custom scrollbar
            self.custom_scrollbar = GreenScrollbar(text_container, width=12)
            self.custom_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Connect the text widget to the scrollbar
            self.output_text.config(yscrollcommand=lambda first, last: self.custom_scrollbar.update_slider(first, last))
            
            # Set up the scrollbar to control the text widget
            self.custom_scrollbar.set_target(self.output_text)
            
            # Bind mouse wheel events to the text widget
            self.output_text.bind("<MouseWheel>", self._on_mousewheel)  # Windows
            self.output_text.bind("<Button-4>", self._on_mousewheel)    # Linux scroll up
            self.output_text.bind("<Button-5>", self._on_mousewheel)    # Linux scroll down
            
            # Configure the text widget to be read-only initially
            self.output_text.config(state=tk.DISABLED)
            
            # Color tags
            self.output_text.tag_configure("normal", foreground=COLORS["text"])
            self.output_text.tag_configure("header", foreground=COLORS["header"])
            self.output_text.tag_configure("warning", foreground=COLORS["warning"])
            self.output_text.tag_configure("accent", foreground=COLORS["accent"])
        
        def _on_mousewheel(self, event):
            """Forward mousewheel events from text widget to scrollbar"""
            self.custom_scrollbar.on_mousewheel(event)

        def create_status_bar(self):
            status_frame = tk.Frame(self.main_frame, bg=COLORS["bg"], height=25)
            status_frame.pack(fill=tk.X, pady=(10, 0))
            
            self.status_message = ttk.Label(status_frame, text="SYSTEM READY", style='Terminal.TLabel')
            self.status_message.pack(side=tk.LEFT, padx=5)
            
            self.datetime_label = ttk.Label(status_frame, text="", style='Terminal.TLabel')
            self.datetime_label.pack(side=tk.RIGHT, padx=5)

        ########################################
        # SINGLE-STEP UNDO FOR THE API KEY FIELD
        ########################################
        def record_api_value_before_change(self, event):
            self.last_api_value = self.api_var.get()

        def undo_api(self, event):
            self.api_var.set(self.last_api_value)
            return "break"

        def toggle_api_visibility(self):
            if self.show_api.get():
                self.api_entry.config(show="")
            else:
                self.api_entry.config(show="*")

        def update_status(self):
            now = datetime.now()
            date_str = now.strftime("%Y.%m.%d")
            time_str = now.strftime("%H:%M:%S")
            self.datetime_label.config(text=f"DATE: {date_str} | TIME: {time_str}")
            
            # Toggle "[ ONLINE ]" text for effect
            if self.online_visible:
                self.status_indicator.config(text="[ ONLINE ]")
                self.online_visible = False
            else:
                self.status_indicator.config(text="[ ONLINE ]")
                self.online_visible = True
                
            self.root.after(1000, self.update_status)

        def display_welcome_message(self):
            welcome_text = (
                "╔══════════════════════════════════════════════════════╗\n"
                "║   NULLNET SCANNER                                    ║\n"
                "║   SECURITY BREACH DETECTION SYSTEM v1.0.3            ║\n"
                "║   POWERED BY: HAVE I BEEN PWNED API                  ║\n"
                "║   CLASSIFICATION: CONFIDENTIAL                       ║\n"
                "╚══════════════════════════════════════════════════════╝\n\n"
                "SYSTEM INITIALIZED...\n"
                "NETWORK CONNECTION: ESTABLISHED\n"
                "DATABASE ACCESS: GRANTED\n"
                "SECURITY PROTOCOLS: ACTIVE\n\n"
                "READY TO SCAN FOR SECURITY BREACHES.\n"
                "ENTER EMAIL ADDRESS OR BREACH NAME AND INITIATE SCAN.\n\n"
            )
            self.terminal.type_text(welcome_text, "header")

        def clear_terminal(self):
            self.terminal.clear()
            self.display_welcome_message()
            self.status_message.config(text="TERMINAL CLEARED")

        def start_scan(self):
            """
            Launch the breach scan in a separate thread.
            Only beep on errors (missing API key, etc.).
            Also sanitize or strip multiline text from email/breach fields
            so we don't pass invalid data to the API.
            """
            email = self.email_var.get().strip()
            breach = self.breach_var.get().strip()
            api_key = self.api_var.get().strip()

            # 1) Remove any newlines/tabs
            email = re.sub(r"[\r\n\t]+", "", email)
            breach = re.sub(r"[\r\n\t]+", "", breach)

            # 2) Keep only normal ASCII letters, digits, underscores, hyphens, @, plus, etc.
            email = re.sub(r"[^a-zA-Z0-9@._\-+]", "", email)
            breach = re.sub(r"[^a-zA-Z0-9._\-]+", "", breach)

            # Put them back in the text fields (sanitized)
            self.email_var.set(email)
            self.breach_var.set(breach)

            # Check input
            if not api_key:
                beep_error()
                self.terminal.type_text("\n>>> ERROR: API KEY REQUIRED\n", "warning")
                return
            if not email and not breach:
                beep_error()
                self.terminal.type_text("\n>>> ERROR: EMAIL OR BREACH NAME REQUIRED\n", "warning")
                return

            self.status_message.config(text="SCAN IN PROGRESS...")
            threading.Thread(target=self.perform_scan, args=(email, breach, api_key), daemon=True).start()

        def perform_scan(self, email, breach, api_key):
            headers = {
                "hibp-api-key": api_key,
                "User-Agent": "NULLNETSecurityScanner/1.0"
            }
            
            self.terminal.type_text("\n>>> INITIATING SCAN...\n", "accent")
            time.sleep(0.5)
            
            # If email is provided
            if email:
                self.terminal.type_text(f"\n>>> SCANNING EMAIL: {email}\n", "header")
                time.sleep(0.5)
                
                folder_name = self.sanitize_email_for_folder(email)
                os.makedirs(folder_name, exist_ok=True)
                
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                try:
                    self.terminal.type_text(">>> CONNECTING TO HIBP DATABASE...\n", "normal")
                    time.sleep(0.5)
                    
                    resp = requests.get(url, headers=headers)
                    
                    if resp.status_code == 404:
                        # 404 on this endpoint means "no breaches found"
                        beep_error()
                        self.terminal.type_text("\n>>> SCAN COMPLETE: NO BREACHES FOUND\n", "accent")
                        self.root.after(0, lambda: self.status_message.config(text="SCAN COMPLETE - NO BREACHES"))
                        return
                        
                    resp.raise_for_status()
                    
                    breach_list = resp.json()
                    if not breach_list:
                        self.terminal.type_text("\n>>> SCAN COMPLETE: NO BREACHES FOUND\n", "accent")
                        self.root.after(0, lambda: self.status_message.config(text="SCAN COMPLETE - NO BREACHES"))
                        return
                    
                    self.terminal.type_text(f"\n>>> ALERT: FOUND {len(breach_list)} BREACH(ES)\n", "warning")
                    time.sleep(0.5)
                    
                    for breach_info in breach_list:
                        breach_name = breach_info["Name"]
                        self.terminal.type_text(f"\n>>> RETRIEVING DETAILS FOR: {breach_name}\n", "accent")
                        time.sleep(0.3)
                        
                        breach_url = f"https://haveibeenpwned.com/api/v3/breach/{breach_name}"
                        br_resp = requests.get(breach_url, headers=headers)
                        br_resp.raise_for_status()
                        
                        breach_data = br_resp.json()
                        
                        json_filename = os.path.join(folder_name, f"{breach_name}.json")
                        self.save_breach_data_to_json(breach_data, json_filename)
                        self.terminal.type_text(f">>> SAVED: {json_filename}\n", "normal")
                        
                        self.display_breach_summary(breach_data)
                    
                    self.terminal.type_text("\n>>> SCAN COMPLETE\n", "accent")
                    self.terminal.type_text(f">>> ALL DATA SAVED TO FOLDER: {folder_name}\n", "normal")
                    self.root.after(0, lambda: self.status_message.config(text=f"SCAN COMPLETE - {len(breach_list)} BREACHES"))
                    
                except requests.exceptions.RequestException as e:
                    beep_error()
                    self.terminal.type_text(f"\n>>> ERROR: {str(e)}\n", "warning")
                    self.root.after(0, lambda: self.status_message.config(text="SCAN FAILED - ERROR"))
            
            # If breach is provided
            if breach:
                self.terminal.type_text(f"\n>>> RETRIEVING BREACH: {breach}\n", "header")
                time.sleep(0.5)
                
                single_breach_url = f"https://haveibeenpwned.com/api/v3/breach/{breach}"
                try:
                    self.terminal.type_text(">>> CONNECTING TO HIBP DATABASE...\n", "normal")
                    time.sleep(0.5)
                    
                    resp = requests.get(single_breach_url, headers=headers)
                    
                    if resp.status_code == 404:
                        beep_error()
                        self.terminal.type_text(f"\n>>> BREACH '{breach}' NOT FOUND\n", "warning")
                        self.root.after(0, lambda: self.status_message.config(text="BREACH NOT FOUND"))
                        return
                        
                    resp.raise_for_status()
                    
                    breach_data = resp.json()
                    
                    json_filename = f"{breach}.json"
                    self.save_breach_data_to_json(breach_data, json_filename)
                    self.terminal.type_text(f">>> SAVED: {json_filename}\n", "normal")
                    
                    self.display_breach_summary(breach_data)
                    
                    self.terminal.type_text("\n>>> SCAN COMPLETE\n", "accent")
                    self.root.after(0, lambda: self.status_message.config(text="BREACH DETAILS RETRIEVED"))
                    
                except requests.exceptions.RequestException as e:
                    beep_error()
                    self.terminal.type_text(f"\n>>> ERROR: {str(e)}\n", "warning")
                    self.root.after(0, lambda: self.status_message.config(text="SCAN FAILED - ERROR"))

        ###############################################
        # HELPER: Print multi-line box with right edge
        ###############################################
        def print_box_line(self, text, box_width=60, tag="normal"):
            """
            Print a single line inside the box, with left/right borders.
            - box_width: total width including the borders.
            - We have '║ ' (2 chars) on the left and ' ║' (2 chars) on the right,
              so we can place up to (box_width - 4) visible chars of text inside.
            """
            content_width = box_width - 4
            # If text is longer, just truncate here. 
            # (We do a more robust wrap in wrap_and_box_print if we want multi-line.)
            truncated = text[:content_width]
            # Left-justify within content_width
            padded = truncated.ljust(content_width)
            line = f"║ {padded} ║\n"
            self.terminal.type_text(line, tag)

        def wrap_and_box_print(self, text, box_width=60, tag="normal"):
            """
            Break 'text' into multiple lines so each fits inside the box,
            then print them with the left/right border.
            """
            content_width = box_width - 4
            words = text.split()
            current_line = ""

            for w in words:
                # If adding this word would exceed content_width, print current_line first
                if len(current_line) + len(w) + (1 if current_line else 0) > content_width:
                    self.print_box_line(current_line, box_width, tag)
                    current_line = w
                else:
                    # Add word to current line
                    if current_line:
                        current_line += " " + w
                    else:
                        current_line = w

            # Print any leftover
            if current_line:
                self.print_box_line(current_line, box_width, tag)

        def display_breach_summary(self, breach_data):
            box_width = 60
            top_border =  "╔" + "═" * (box_width - 2) + "╗\n"
            mid_border =  "╠" + "═" * (box_width - 2) + "╣\n"
            bot_border =  "╚" + "═" * (box_width - 2) + "╝\n"

            # Top border
            self.terminal.type_text("\n" + top_border, "header")

            # Centered title
            title_str = "BREACH DETAILS"
            # We have "║ " + text + " ║", so effectively box_width - 4 chars for text
            centered_title = title_str.center(box_width - 4)
            self.print_box_line(centered_title, box_width, tag="header")

            # Mid border
            self.terminal.type_text(mid_border, "header")

            # Key lines (Name, Title, etc.)
            lines = [
                ("Name",         breach_data.get("Name", "N/A")),
                ("Title",        breach_data.get("Title", "N/A")),
                ("Domain",       breach_data.get("Domain", "N/A")),
                ("Breach Date",  breach_data.get("BreachDate", "N/A")),
                ("Added Date",   breach_data.get("AddedDate", "N/A")),
                ("Modified",     breach_data.get("ModifiedDate", "N/A")),
                ("Pwn Count",    breach_data.get("PwnCount", "N/A")),
            ]
            for label, value in lines:
                label_text = f"{label}:"
                line_str = f"{label_text:<12} {value}"
                self.print_box_line(line_str, box_width, "normal")

            # Data classes
            data_classes = breach_data.get('DataClasses', [])
            self.print_box_line("Data Classes:", box_width, "normal")
            for cls in data_classes:
                self.print_box_line(f"  - {cls}", box_width, "normal")

            verified = breach_data.get('IsVerified', 'N/A')
            fabricated = breach_data.get('IsFabricated', 'N/A')
            self.print_box_line(f"Verified:    {verified}", box_width, "normal")
            self.print_box_line(f"Fabricated:  {fabricated}", box_width, "normal")

            # Blank line
            self.print_box_line("", box_width, "normal")
            # DESCRIPTION header
            self.print_box_line("DESCRIPTION:", box_width, "normal")

            # Description (may be long)
            description = breach_data.get('Description', '')
            description_cleaned = self.clean_html_tags(description)
            # Wrap and print in lines
            self.wrap_and_box_print(description_cleaned, box_width, "normal")

            # Bottom border
            self.terminal.type_text(bot_border, "header")

        def clean_html_tags(self, text):
            text_no_tags = re.sub(r'<[^>]*>', '', text)
            return html.unescape(text_no_tags)

        def sanitize_email_for_folder(self, email):
            folder_name = email.replace("@", "_at_").replace(".", "_dot_")
            return folder_name

        def save_breach_data_to_json(self, breach_data, filename):
            with open(filename, "w", encoding="utf-8") as outfile:
                json.dump(breach_data, outfile, indent=2)

def UTF8_encode():
    if SYSTEM == "Windows":
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        except:
            pass


# Function to hide console window on Windows
def hide_console_window():
    """Hide the console window on Windows"""
    if SYSTEM == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

# Main execution block
if __name__ == "__main__":
    # Hide console window on Windows
    hide_console_window()
    
    # Check if we're running in a terminal-only environment
    gui_available = is_display_available()
    
    if gui_available:
        # Only import GUI modules when needed
        if import_gui_modules():
            # Define GUI classes only when needed
            define_gui_classes()
            # Start GUI application
            root = tk.Tk()
            app = HIBPScannerApp(root)
            root.mainloop()
        else:
            print("Failed to import GUI modules. Running in terminal-only mode.")
            app = TerminalOnlyApp()
    else:
        # Terminal-only mode - no need to import GUI-related modules
        print("No display detected. Running in terminal-only mode.")
        app = TerminalOnlyApp()
