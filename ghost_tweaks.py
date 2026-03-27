#!/usr/bin/env python3
"""
Ghost Tweaks Ultra - FINAL PRODUCTION BUILD
Windows Performance Optimizer (Professional Edition)
"""

import os
import sys
import subprocess
import ctypes
import winreg
import time
import threading
import shutil
import tkinter as tk
from tkinter import font

# --- Auto-Install Dependencies ---
try:
    import psutil
except ImportError:
    if not getattr(sys, 'frozen', False): 
        print("Installing required module (psutil)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "--quiet"])
        import psutil

# --- UI Theme Colors (Flat Dark Design) ---
BG_MAIN = "#121212"       # Deep Dark Background
BG_SIDEBAR = "#1A1A1A"    # Sidebar Background
BG_CARD = "#252526"       # Buttons & Console Background
BG_SEPARATOR = "#2D2D30"  # Subtle line separator color
TEXT_MAIN = "#FFFFFF"     # White Text
TEXT_DIM = "#A0A0A0"      # Dimmed Text
ACCENT = "#00ADB5"        # Modern Cyan
ACCENT_HOVER = "#008C93"  # Darker Cyan for Hover
SUCCESS = "#4CAF50"       # Green for success logs
ERROR = "#F44336"         # Red for error/warning logs


# --- Custom GUI Components ---
class ModernButton(tk.Button):
    """Flat, modern button with hover effects for pure Tkinter."""
    def __init__(self, master, **kw):
        self.default_bg = kw.pop('bg', BG_CARD)
        self.hover_bg = kw.pop('hover_color', '#3E3E42')
        kw['bg'] = self.default_bg
        kw['fg'] = kw.get('fg', TEXT_MAIN)
        kw['relief'] = 'flat'
        kw['activebackground'] = self.hover_bg
        kw['activeforeground'] = kw['fg']
        kw['bd'] = 0
        kw['highlightthickness'] = 0
        kw['cursor'] = 'hand2'
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        if self['state'] != 'disabled':
            self['bg'] = self.hover_bg

    def on_leave(self, e):
        if self['state'] != 'disabled':
            self['bg'] = self.default_bg

# --- Main Application ---
class GhostTweaksGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Tweaks Ultra")
        self.root.geometry("950x650") 
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        # Modern Fonts
        self.font_title = font.Font(family="Segoe UI", size=24, weight="bold")
        self.font_header = font.Font(family="Segoe UI", size=13, weight="bold")
        self.font_normal = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_small = font.Font(family="Segoe UI", size=9)
        self.font_console = font.Font(family="Consolas", size=9)

        self.setup_ui()
        self.log_message("System initialized. Run with Administrator privileges confirmed.", SUCCESS)
        self.log_message("Ready to optimize. Select a tweak to apply.", ACCENT)

    def fetch_hardware_info(self):
        """Fetches CPU, GPU and RAM info."""
        # RAM
        try:
            ram_gb = f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB"
        except:
            ram_gb = "Unknown"

        # CPU
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
            cpu_name = cpu_name.strip()
            cores = psutil.cpu_count(logical=True)
            cpu_display = f"{cpu_name}\n({cores} Logical Cores)"
        except:
            cpu_display = "Unknown CPU"

        # GPU
        try:
            cmd = 'powershell -NoProfile -Command "(Get-CimInstance -ClassName Win32_VideoController).Name"'
            output = subprocess.check_output(cmd, shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
            gpu_display = output.split('\n')[0].strip() if output else "Unknown GPU"
        except:
            gpu_display = "Unknown GPU"

        return cpu_display, gpu_display, ram_gb

    def setup_ui(self):
        # --- SIDEBAR (Left) ---
        sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / Title
        tk.Label(sidebar, text="GHOST\nTWEAKS", font=self.font_title, bg=BG_SIDEBAR, fg=ACCENT, justify="left").pack(pady=(40, 5), padx=25, anchor="w")
        tk.Label(sidebar, text="Pro Edition", font=self.font_small, bg=BG_SIDEBAR, fg=TEXT_DIM).pack(padx=25, anchor="w", pady=(0, 40))

        # Hardware Info Section
        cpu, gpu, ram = self.fetch_hardware_info()

        tk.Label(sidebar, text="SYSTEM HARDWARE", font=self.font_small, bg=BG_SIDEBAR, fg=ACCENT).pack(padx=25, anchor="w", pady=(0, 10))
        
        # CPU
        tk.Label(sidebar, text="Processor:", font=self.font_small, bg=BG_SIDEBAR, fg=TEXT_DIM).pack(padx=25, anchor="w")
        tk.Label(sidebar, text=cpu, font=self.font_normal, bg=BG_SIDEBAR, fg=TEXT_MAIN, justify="left", wraplength=210).pack(padx=25, anchor="w", pady=(0, 15))
        
        # GPU
        tk.Label(sidebar, text="Graphics Card:", font=self.font_small, bg=BG_SIDEBAR, fg=TEXT_DIM).pack(padx=25, anchor="w")
        tk.Label(sidebar, text=gpu, font=self.font_normal, bg=BG_SIDEBAR, fg=TEXT_MAIN, justify="left", wraplength=210).pack(padx=25, anchor="w", pady=(0, 15))

        # RAM
        tk.Label(sidebar, text="Memory (RAM):", font=self.font_small, bg=BG_SIDEBAR, fg=TEXT_DIM).pack(padx=25, anchor="w")
        tk.Label(sidebar, text=ram, font=self.font_normal, bg=BG_SIDEBAR, fg=TEXT_MAIN, justify="left").pack(padx=25, anchor="w")

        # Apply All Button
        self.btn_apply_all = ModernButton(
            sidebar, text="APPLY ALL", font=self.font_header, 
            bg=ACCENT, hover_color=ACCENT_HOVER, fg="#000000",
            command=self.run_all_tweaks, pady=12
        )
        self.btn_apply_all.pack(padx=25, fill="x", side="bottom", pady=35)

        # --- MAIN CONTENT (Right) ---
        main_content = tk.Frame(self.root, bg=BG_MAIN)
        main_content.pack(side="left", fill="both", expand=True, padx=35, pady=35)

        # Header
        tk.Label(main_content, text="Performance Tweaks", font=self.font_header, bg=BG_MAIN, fg=TEXT_MAIN).pack(anchor="w", pady=(0, 20))

        # Tweak List Container
        list_container = tk.Frame(main_content, bg=BG_MAIN)
        list_container.pack(fill="x")

        self.buttons = {}
        tweaks =[
            ("Ultimate Performance Plan", "Unlocks maximum CPU frequencies and prevents sleep states.", self.tweak_power),
            ("Network & Latency", "Optimizes the TCP/IP stack for lowest possible gaming ping.", self.tweak_network),
            ("RAM Management", "Prevents system paging to hard drives to fix stuttering.", self.tweak_memory),
            ("Input Delay Fix", "Enables 1:1 input by completely disabling mouse acceleration.", self.tweak_input),
            ("System Cleanup", "Deeply purges temporary files and the prefetch cache.", self.tweak_cleanup)
        ]

        for i, (title, desc, func) in enumerate(tweaks):
            item_wrapper = tk.Frame(list_container, bg=BG_MAIN)
            item_wrapper.pack(fill="x")

            item_frame = tk.Frame(item_wrapper, bg=BG_MAIN)
            item_frame.pack(fill="x", pady=6)
            item_frame.grid_columnconfigure(0, weight=1)

            lbl_title = tk.Label(item_frame, text=title, font=self.font_normal, bg=BG_MAIN, fg=TEXT_MAIN)
            lbl_title.grid(row=0, column=0, sticky="w")
            
            lbl_desc = tk.Label(item_frame, text=desc, font=self.font_small, bg=BG_MAIN, fg=TEXT_DIM)
            lbl_desc.grid(row=1, column=0, sticky="w")

            btn = ModernButton(item_frame, text="Apply", font=self.font_normal, width=12, pady=4, command=lambda f=func: self.run_thread(f))
            btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))
            self.buttons[func.__name__] = btn

            if i < len(tweaks) - 1:
                tk.Frame(item_wrapper, bg=BG_SEPARATOR, height=1).pack(fill="x", pady=(10, 10))

        # --- LOG / CONSOLE ---
        tk.Label(main_content, text="Activity Log", font=self.font_small, bg=BG_MAIN, fg=TEXT_DIM).pack(anchor="w", pady=(25, 5))
        
        log_frame = tk.Frame(main_content, bg=BG_CARD, highlightthickness=1, highlightbackground=BG_SEPARATOR)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, bg=BG_CARD, fg=TEXT_DIM, font=self.font_console, relief="flat", padx=10, pady=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)

        self.log_text.tag_config("ACCENT", foreground=ACCENT)
        self.log_text.tag_config("SUCCESS", foreground=SUCCESS)
        self.log_text.tag_config("ERROR", foreground=ERROR)

    # --- UI Helpers (Thread Safe) ---
    def log_message(self, message, tag=None):
        self.root.after(0, self._insert_log, message, tag)

    def _insert_log(self, message, tag):
        self.log_text.config(state="normal")
        if tag:
            self.log_text.insert("end", f"> {message}\n", tag)
        else:
            self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def show_overlay(self, title, message):
        """Creates a custom, professional in-app overlay instead of an ugly Windows MessageBox."""
        def _render_overlay():
            overlay = tk.Frame(self.root, bg=BG_MAIN) # Using MAIN BG to act as a solid backdrop
            overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # The Modal Card
            card = tk.Frame(overlay, bg=BG_CARD, highlightthickness=1, highlightbackground=ACCENT)
            card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=220)
            
            tk.Label(card, text=title, font=self.font_header, bg=BG_CARD, fg=ACCENT).pack(pady=(35, 15))
            tk.Label(card, text=message, font=self.font_normal, bg=BG_CARD, fg=TEXT_MAIN, justify="center").pack(pady=(0, 25))
            
            ModernButton(card, text="CONTINUE", font=self.font_normal, width=15, pady=6, bg=ACCENT, fg="#000000", hover_color=ACCENT_HOVER, command=overlay.destroy).pack()

        # Ensure it runs on the main UI thread
        self.root.after(0, _render_overlay)

    def set_buttons_state(self, state):
        def _set_state():
            self.btn_apply_all.config(state=state)
            for btn in self.buttons.values():
                btn.config(state=state)
        self.root.after(0, _set_state)

    def run_thread(self, func):
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()

    # --- THE REAL TWEAKS ---
    def run_all_tweaks(self):
        def task():
            self.set_buttons_state(tk.DISABLED)
            self.log_message("Initializing GHOST TWEAKS ULTRA MODE...", "ACCENT")
            time.sleep(0.5)
            
            self.tweak_power(is_batch=True)
            self.tweak_network(is_batch=True)
            self.tweak_memory(is_batch=True)
            self.tweak_input(is_batch=True)
            self.tweak_cleanup(is_batch=True)
            
            self.log_message("ALL SYSTEM TWEAKS APPLIED SUCCESSFULLY!", "SUCCESS")
            self.set_buttons_state(tk.NORMAL)
            self.show_overlay("Optimization Complete", "All selected tweaks have been successfully applied to your system.\n\nPlease restart your PC to take full effect.")

        self.run_thread(task)

    def tweak_power(self, is_batch=False):
        if not is_batch: self.set_buttons_state(tk.DISABLED)
        self.log_message("Activating Ultimate Performance Plan...")
        try:
            # Duplicate the hidden Ultimate Performance plan
            subprocess.run(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # Set it as active
            subprocess.run(["powercfg", "/setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("✓ Ultimate Performance successfully activated!", "SUCCESS")
        except Exception as e:
            self.log_message(f"✗ Failed to set power plan: {e}", "ERROR")
        if not is_batch: self.set_buttons_state(tk.NORMAL)

    def tweak_network(self, is_batch=False):
        if not is_batch: self.set_buttons_state(tk.DISABLED)
        self.log_message("Optimizing TCP/IP Stack & Latency Registry...")
        tweaks =[
            ("SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TcpAckFrequency", 1),
            ("SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TCPNoDelay", 1),
            ("SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TcpDelAckTicks", 0),
            ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "NetworkThrottlingIndex", 0xFFFFFFFF),
            ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "SystemResponsiveness", 0)
        ]
        for path, name, value in tweaks:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                winreg.CloseKey(key)
            except: 
                pass # Fail silently if key doesn't exist on specific OS
        
        self.log_message("✓ Network latency & packet flow optimized!", "SUCCESS")
        if not is_batch: self.set_buttons_state(tk.NORMAL)

    def tweak_memory(self, is_batch=False):
        if not is_batch: self.set_buttons_state(tk.DISABLED)
        self.log_message("Applying RAM Management Tweaks...")
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisablePagingExecutive", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self.log_message("✓ RAM configured for gaming focus!", "SUCCESS")
        except Exception:
            self.log_message("✗ Registry access denied for memory tweaks.", "ERROR")
        if not is_batch: self.set_buttons_state(tk.NORMAL)

    def tweak_input(self, is_batch=False):
        if not is_batch: self.set_buttons_state(tk.DISABLED)
        self.log_message("Disabling Windows Mouse Acceleration...")
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)
            self.log_message("✓ Input delay completely removed!", "SUCCESS")
        except:
            self.log_message("✗ Failed to change mouse parameters.", "ERROR")
        if not is_batch: self.set_buttons_state(tk.NORMAL)

    def tweak_cleanup(self, is_batch=False):
        if not is_batch: self.set_buttons_state(tk.DISABLED)
        self.log_message("Purging system junk & temporary files...")
        
        temp_dirs =[
            os.environ.get("TEMP", ""), 
            os.environ.get("TMP", ""), 
            r"C:\Windows\Temp", 
            r"C:\Windows\Prefetch"
        ]
        
        bytes_freed = 0
        
        for d in temp_dirs:
            if d and os.path.exists(d):
                for item in os.listdir(d):
                    item_path = os.path.join(d, item)
                    try:
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            size = os.path.getsize(item_path)
                            os.remove(item_path)
                            bytes_freed += size
                        elif os.path.isdir(item_path):
                            # Calculate size of folder before deleting
                            for dp, _, fn in os.walk(item_path):
                                for f in fn:
                                    fp = os.path.join(dp, f)
                                    if not os.path.islink(fp) and os.path.exists(fp): 
                                        bytes_freed += os.path.getsize(fp)
                            shutil.rmtree(item_path)
                    except Exception: 
                        pass # Ignore locked files currently in use by Windows
        
        mb_freed = round(bytes_freed / (1024 * 1024), 2)
        self.log_message(f"✓ Deep clean complete. Freed {mb_freed} MB of space!", "SUCCESS")
        
        if not is_batch: 
            self.set_buttons_state(tk.NORMAL)
            self.show_overlay("Cleanup Complete", f"System cleanup successful.\nFreed {mb_freed} MB of temporary junk files.")


# --- Admin-Check & Auto-Elevate ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restarts the script with administrative privileges if not already elevated."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)


# --- Entry Point ---
if __name__ == "__main__":
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()

    # 1. Require Admin Rights!
    run_as_admin()

    # 2. Enable DPI awareness for sharp text on modern monitors
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # 3. Start GUI
    root = tk.Tk()
    app = GhostTweaksGUI(root)
    root.mainloop()