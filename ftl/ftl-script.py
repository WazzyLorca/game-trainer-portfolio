# FTL (Faster Than Light) Infinite Resources Trainer
# This script demonstrates memory manipulation to grant infinite Fuel and Scrap.
# Developed as a reverse engineering portfolio project.

import pymem
import pymem.process
import time

# --- CONFIGURATION - The clues from the investigation ---

# The name of the game's process.
PROCESS_NAME = "FTLGame.exe"

# The static pointer offset found by tracing the base pointer (from ECX/EBX).
# This is the permanent "signpost" that leads to the player's data.
STATIC_POINTER_OFFSET = 0x51348C

# The final offsets from the player object to the specific resource values.
# These were found by analyzing the assembly instructions in the debugger.
FUEL_OFFSET = 0x494
SCRAP_OFFSET = 0x4D4

# The desired values to write to memory.
GOD_MODE_FUEL = 99
GOD_MODE_SCRAP = 9999

# How often the script should write to memory (in seconds).
WRITE_INTERVAL = 1.0

def main():
    """
    Main function to find the game process, resolve pointers, and write new values.
    """
    print("--- FTL Infinite Resources Trainer ---")
    
    # --- Step 1: Find and attach to the game process ---
    print("Searching for FTLGame.exe process...")
    try:
        # Initialize pymem and open the game process with the desired access rights.
        pm = pymem.Pymem(PROCESS_NAME)
        print(f"Successfully attached to process ID: {pm.process_id}")
    except pymem.exception.ProcessNotFound:
        print(f"Error: Process '{PROCESS_NAME}' not found. Please make sure the game is running.")
        input("Press Enter to exit...")
        return

    # --- Step 2: Get the base address of the game's main module ---
    # This is needed because the static pointer is an offset from this base address.
    try:
        # module_from_name gets the handle and base address of the FTLGame.exe module in memory.
        module_base = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        print(f"Base address of {PROCESS_NAME} found at: {hex(module_base)}")
    except AttributeError:
        print(f"Error: Could not find module '{PROCESS_NAME}'. The game might not be fully loaded.")
        input("Press Enter to exit...")
        return

    print("\nTrainer is active! Fuel and Scrap will be set to max.")
    print("You can leave this window running in the background.")
    print("Press Ctrl+C in this window to stop the trainer.")
    print("--------------------------------------------------")

    # --- Step 3: Main loop to continuously write values ---
    try:
        while True:
            try:
                # 1. Find the address of our static pointer.
                static_address = module_base + STATIC_POINTER_OFFSET
                
                # 2. Read the value at the static address to get the dynamic base pointer to the player object.
                player_base_ptr = pm.read_int(static_address)
                
                # 3. If the pointer is null (e.g., in a menu), skip this iteration.
                if player_base_ptr == 0:
                    time.sleep(WRITE_INTERVAL)
                    continue

                # 4. Calculate the final memory addresses for Fuel and Scrap.
                fuel_address = player_base_ptr + FUEL_OFFSET
                scrap_address = player_base_ptr + SCRAP_OFFSET
                
                # 5. Write our desired god-mode values to those final addresses.
                pm.write_int(fuel_address, GOD_MODE_FUEL)
                pm.write_int(scrap_address, GOD_MODE_SCRAP)

            except pymem.exception.MemoryReadError:
                # This can happen during loading screens or when quitting the game.
                # We just ignore it and let the loop try again.
                pass
            
            # Wait for the specified interval before writing again.
            time.sleep(WRITE_INTERVAL)

    except KeyboardInterrupt:
        print("\n--------------------------------------------------")
        print("Trainer deactivated by user. Have fun!")
        input("Press Enter to exit...")

# --- Entry point of the script ---
if __name__ == '__main__':
    main()