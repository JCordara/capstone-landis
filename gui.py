"""
Simple User Interface for keylogger
We may consider routing all future project functionality through this GUI

Dependencies:
- None

Known issues:
- Changing the log location while program is running is unreliable
  (May just write to previous location until UI is restarted)
- Unable to capture keystroke combinations for pausing (eg. ctrl+c)
"""

import input_logger as keylogger

import tkinter as tk
import pathlib


# Profiles to choose from
profiles = [
    "JON",
    "MAR",
    "ZIR",
    "JOS",
    "HEN",
    "MIT",
    "OTH"
]

characters = [
    "SCO",
    "SOL",
    "PYR",
    "DEM",
    "HEA",
    "ENG",
    "MED",
    "SNI",
    "SPY"
]


# Create main window
gui = tk.Tk()

# Persistent variable initial values
pausekey = "`"
root_logdir = "./"
curr_profile = tk.StringVar()
curr_profile.set("profile")
curr_character = tk.StringVar()
curr_character.set("character")

started = False

# Non-editable names of log files
mouse_logdir = "mouse_actions.log"
kb_logdir = "keyboard_actions.log"

# Window settings
_windowwidth  = 350
_windowheight = 200

# Save user preferences
def save_preferences():
    with open('.preferences', 'w', encoding='utf-8') as f:
            f.write("pausekey: " + pausekey + '\n')
            f.write("root_dir: " + root_logdir + '\n')
            f.write("profile: " + curr_profile.get())
            f.write("character: " + curr_character.get())

# Load user preferences
def load_preferences():
    global pausekey, root_logdir
    # Check that .preferences file exists
    file = pathlib.Path('.preferences')
    if file.exists():
        # If any of the following operations fail, delete .preferences
        try:
            with open('.preferences', 'r', encoding='utf-8') as f:
                data = f.readlines()
                pausekey = data[0][10:-1]
                root_logdir = data[1][10:-1]
                curr_profile.set(data[2][9:])
                curr_character.set(data[3][11:])
        except:
            file.unlink() # unlink = delete



# Load user preferences
load_preferences()
keylogger.set_log_directory(root_logdir)
keylogger.set_pause_key(pausekey)
keylogger.set_profile(curr_profile.get())
keylogger.set_character(curr_character.get())


# Main window
gui.title("Landis")
gui.resizable(False, False)
gui.rowconfigure(0, minsize=_windowheight/2, weight=1)
gui.rowconfigure(1, minsize=_windowheight/2, weight=1)
gui.columnconfigure(0, minsize=_windowwidth, weight=1)

# ----- Frame widgets -----
# Input logger status frame
frm_status = tk.Frame(gui, width=_windowwidth)
frm_status.rowconfigure(0, minsize=50)
frm_status.columnconfigure(0, minsize=_windowwidth/5, weight=1)
frm_status.columnconfigure(4, minsize=_windowwidth/5, weight=1)

# Settings frame
frm_settings = tk.Frame(gui, width=_windowwidth)

# Frame positioning
frm_status.grid(row=0, sticky="ns")
frm_settings.grid(row=1, sticky="ns")


# ----- Status widgets -----
# Text control variable used for showing elapsed time
elapsed_time = tk.StringVar()
elapsed_time.set("00m 00s")

# Create widgets
lbl_running = tk.Label(frm_status, width=25, font=("Helvetica", 12))
btn_toggle = tk.Button(frm_status, text="Start", width=7)
btn_stop = tk.Button(frm_status, text="Stop", state='disabled', width=7)
btn_profile = tk.OptionMenu(frm_status, curr_profile, *profiles)
btn_character = tk.OptionMenu(frm_status, curr_character, *characters)
lbl_loglength = tk.Label(frm_status, text="Log length:")
lbl_time = tk.Label(frm_status, textvariable=elapsed_time, width=6, font=("Helvetica", 10))

# Adjust widgets
btn_profile.config(width=8)

# Status widgets positioning
lbl_running.grid(row=0, column=1, columnspan=3)
btn_toggle.grid(row=1, column=1, padx=5)
btn_stop.grid(row=1, column=2, padx=5)
btn_profile.grid(row=1, column=3)
btn_character.grid(row=1, column=4)
lbl_loglength.grid(row=2, column=2)
lbl_time.grid(row=2, column=3, pady=8)

# Status widget behavior
def update_lbl_status(status):
    lbl_running['text'] = f"Input logger status: {status}"

def toggle_status(event):
    global started
    # State machine of toggle button
    if btn_toggle['text'] == "Start":
        keylogger.start()
        btn_toggle['text'] = "Pause"
        btn_stop['state'] = 'normal'
        started = True
        check_status() # Start periodic status update checks
    elif btn_toggle['text'] == "Pause":
        keylogger.pause()
        btn_toggle['text'] = "Resume"
    elif btn_toggle['text'] == "Resume":
        keylogger.resume()
        update_lbl_status("Running")
        btn_toggle['text'] = "Pause"

def stop_keylogger(event):
    global started
    # Stop keylogger
    keylogger.stop()
    btn_toggle['text'] = "Start"
    btn_stop['state'] = 'disabled'
    update_lbl_status("Stopped")

def set_profile(var, ix, op):
    keylogger.set_profile(curr_profile.get())
    save_preferences()

def set_character(var, ix, op):
    keylogger.set_character(curr_character.get())
    save_preferences()

def check_status():
    if keylogger.running == False:
        btn_toggle['text'] = "Start"
        btn_stop['state'] = 'disabled'
        update_lbl_status("Stopped")
    else:
        if keylogger.paused == True:
            update_lbl_status("Paused")
            btn_toggle['text'] = "Resume"
        else:
            update_lbl_status("Running")
            btn_toggle['text'] = "Pause"
    
    minutes, seconds = divmod(keylogger.elapsed_time(), 60)
    elapsed_time.set(f"{minutes:02.0f}m {seconds:02.0f}s")

    if keylogger.running:
        gui.after(100, check_status) # Run this function every 0.1s


# Assign settings widget behavior
btn_toggle.bind('<Button-1>', toggle_status)
btn_stop.bind('<Button-1>', stop_keylogger)
curr_profile.trace('w', set_profile)
curr_character.trace('w', set_character)

# Fill text fields with initial values
update_lbl_status("Not started")

# ----- Settings widgets -----
# Title and info bar
lbl_settings = tk.Label(frm_settings, text="Settings", font=("Helvetica", 14, "bold underline"))
lbl_settings_info = tk.Label(frm_settings, font=("Helvetica", 10, "italic"))

# Pause key modification
lbl_pausekey = tk.Label(frm_settings, width=25)
ent_pausekey = tk.Entry(frm_settings, width=10, state='readonly', 
        readonlybackground='white', justify='center')
btn_setpausekey = tk.Button(frm_settings, text="Apply")

# Log directories modification
lbl_logdirs = tk.Label(frm_settings, width=25)
ent_logdir = tk.Entry(frm_settings)
btn_setlogdir = tk.Button(frm_settings, text="Apply")

# Settings widgets positioning
lbl_settings.grid(row=0, columnspan=2) # Along the top
lbl_settings_info.grid(row=4, columnspan=2) # Along the bottom

lbl_pausekey.grid(row=1, column=0)
ent_pausekey.grid(row=2, column=0)
btn_setpausekey.grid(row=3, column=0)

lbl_logdirs.grid(row=1, column=1)
ent_logdir.grid(row=2, column=1)
btn_setlogdir.grid(row=3, column=1)

# Settings widget behavior

def update_lbl_pausekey(key):
    lbl_pausekey['text'] = f"Pause key: {key}"

def update_lbl_logdirs():
    lbl_logdirs['text'] = root_logdir + mouse_logdir + '\n' + root_logdir + kb_logdir

def set_pausekey(event):
    global pausekey

    gui.focus() # Take focus off entry widget
    userinput = ent_pausekey.get()
    ent_pausekey.delete(0, 'end')
    
    pausekey = userinput
    keylogger.set_pause_key(pausekey)
    update_lbl_pausekey(userinput)

    save_preferences()

def ent_pausekey_update(event):
    # Update contents of entry widget with key pressed
    ent_pausekey.config(state='normal')
    ent_pausekey.delete(0, 'end')
    ent_pausekey.insert(0, event.keysym)
    ent_pausekey.config(state='readonly')

def set_log_directory(event):
    global root_logdir

    gui.focus() # Take focus off entry widget
    userinput = ent_logdir.get()
    
    # some input checking...
    valid = True
    if userinput and userinput[-1] != '/':
        userinput += '/' # Append forward slash if necessary

    if not pathlib.Path(userinput).exists():
        valid = False
    
    if valid:
        ent_logdir.delete(0, 'end')
        lbl_settings_info['text'] = ""
        lbl_settings_info.configure(fg="#000000")
        
        root_logdir = userinput
        keylogger.set_log_directory(root_logdir)
        update_lbl_logdirs()

        save_preferences()
    else:
        lbl_settings_info['text'] = f"Invalid directory: {userinput}"
        lbl_settings_info.configure(fg="#ff0000")

# Assign settings widget behavior
btn_setpausekey.bind('<Button-1>', set_pausekey)
ent_pausekey.bind('<Return>', set_pausekey)
btn_setlogdir.bind('<Button-1>', set_log_directory)
ent_logdir.bind('<Return>', set_log_directory)

# Capture special keys in entry widget
ent_pausekey.bind('<Key>', ent_pausekey_update)

# Fill text fields with initial values
update_lbl_pausekey(pausekey)
update_lbl_logdirs()

# Block until window closes
gui.mainloop()