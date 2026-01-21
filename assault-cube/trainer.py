import pymem
import pymem.process
import time

# --- CONFIGURATION ---
# Values discovered through reverse engineering!
PROCESS_NAME = "ac_client.exe"
BASE_POINTER_OFFSET = 0x10F4F4  # static green address
HEALTH_OFFSET = 0xF8           # the offset from the EDX register

# The value we want to write to the health address
GOD_MODE_HEALTH = 1337

def main():
    print("Searching for game process...")
    try:
        # Attach to the game process
        pm = pymem.Pymem(PROCESS_NAME)
        print(f"Successfully attached to process: {PROCESS_NAME}")
    except pymem.exception.ProcessNotFound:
        print(f"Process not found. Please make sure '{PROCESS_NAME}' is running.")
        return

    # Get the base address of the main game module (ac_client.exe)
    # This is the starting point for our static pointer.
    try:
        module_base = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        print(f"Base address of {PROCESS_NAME} found at: {hex(module_base)}")
    except AttributeError:
        print(f"Could not find module '{PROCESS_NAME}'. Exiting.")
        return

    print("\nTrainer is active! Press Ctrl+C in this window to exit.")
    print("Setting health to 1337...")

    try:
        # This is the main loop for our trainer
        while True:
            # --- POINTER RESOLUTION ---
            # This is where we follow the path found in Cheat Engine.
            try:
                # 1. Read the value at the static pointer to get the Player Object's base address
                player_base_addr = pm.read_int(module_base + BASE_POINTER_OFFSET)

                # 2. Add the health offset to get the final address of our health value
                health_addr = player_base_addr + HEALTH_OFFSET

                # Now that we have the final address, we can read and write to it
                current_health = pm.read_int(health_addr)
                
                # Only write the new value if the current health is not already our god mode value
                if current_health < GOD_MODE_HEALTH:
                    pm.write_int(health_addr, GOD_MODE_HEALTH)
                    print(f"Health was {current_health}, now set to {GOD_MODE_HEALTH}!")
            
            except pymem.exception.MemoryReadError:
                # This can happen during loading screens or if the address becomes invalid.
                # We'll just wait and try again on the next loop.
                pass
            
            # A small delay to prevent the script from using 100% of the CPU
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Trainer deactivated. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()