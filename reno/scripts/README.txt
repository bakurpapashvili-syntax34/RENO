===============================================================================
                          🏮 RENO FILE MANAGER 🏮
               Custom Python/Qt6 Explorer for Hyprland/Wayland
===============================================================================

RENO (Rapid Explorer & Native Object (Manager)) is a high-performance built on 
Python, neon-infused file manager designed for users who demand a Cyberpunk 
aesthetic and seamless tiling integration.

-------------------------------------------------------------------------------
1. PREREQUISITES & SYSTEM CONDITIONS
-------------------------------------------------------------------------------
To run Reno, your system MUST meet the following conditions:

- OS: Linux (Tested on Arch Linux Hyprland/Wayland)
- Python: version 3.10 or higher
- Libraries: PyQt6 (pip install PyQt6)
- Fonts: JetBrainsMono Nerd Font (Required for UI icons/text)
- Icon Theme: Papirus-Dark (Recommended for visual consistency)
- Portals: xdg-desktop-portal-hyprland (For file opening via xdg-open)

-------------------------------------------------------------------------------
2. INSTALLATION TUTORIAL
-------------------------------------------------------------------------------
Follow these steps to set up Reno on your system:

STEP 1: Install Python dependencies
        $ pip install PyQt6

STEP 2: Install Required Fonts & Icons (Arch Linux example)
        $ sudo pacman -S ttf-jetbrains-mono-nerd papirus-icon-theme

STEP 3: Configure Hyprland
        Add the following block to your ~/.config/hypr/hyprland.conf:

        windowrule {
            name = Reno
            match:class = Reno
            float = true
            border_size = 0
            rounding = 0
        }

STEP 4: Add the path ~/.config/reno/scripts/ and create "reno.py" by nvim or nano

STEP 5: Copy & Paste the script of reno.py in your ~/.config/reno/scripts/

STEP 6: Run Reno
        $ python3 ~/.config/reno/scripts/reno.py

-------------------------------------------------------------------------------
3. USER GUIDE (HOW TO USE)
-------------------------------------------------------------------------------
- NAVIGATION: Use the Back () and Forward () buttons to browse history.
- ADDRESS BAR: Type a path (e.g. ~/Pictures) and press Enter to jump there.
- SELECTION: Click and drag the mouse to draw a "Rubber Band" selection box.
- MOVING: Click and hold a file to move it; it will "Snap" to the grid.
- SEARCHING: Start typing in the search box () for instant live filtering.
- CONTEXT MENU: Right-click any file to see Properties, Rename, or Open.

-------------------------------------------------------------------------------
4. TROUBLESHOOTING
-------------------------------------------------------------------------------
- Gaps around the window? Ensure 'border_size = 0' is set in your windowrule.
- Protruding edges? Ensure the 'update_mask' function is active in your code.
- Files won't open? Ensure 'xdg-utils' is installed on your system.

-------------------------------------------------------------------------------
5. IMPORTANT!!!
-------------------------------------------------------------------------------
The is a trial version, the complete version we'll be done with finishing our 
Distro project, with possibility of upload updates of it.
The updates it'll be automatic, just use the update command in your terminal 
"sudo pacman -Syu --noconfirm" to recept it easily.
And most of that, It still free, FOREVER!!!!
===============================================================================
Developed by BakurPapashvili34 in 2026 for the Linux Community.
===============================================================================
