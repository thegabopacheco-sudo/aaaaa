import pymem
import pymem.process
import pymem.memory
import ctypes
from ctypes import wintypes

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

def read_region(pm, addr, size):
    try:
        return pm.read_bytes(addr, size)
    except Exception:
        return None

def pattern_scan_region(data, pattern, mask):
    if not data: return 0
    pattern_len = len(mask)
    for i in range(len(data) - pattern_len):
        found = True
        for j in range(pattern_len):
            if mask[j] != '?' and data[i + j] != pattern[j]:
                found = False
                break
        if found:
            return i
    return 0

def main():
    print("[*] Buscando FiveM...")
    pm = None
    target_process = None

    for process in pymem.process.list_processes():
        try:
            name = process.szExeFile.decode('utf-8', errors='ignore')
            if "GTAProcess" in name:
                pm = pymem.Pymem(process.th32ProcessID)
                target_process = name
                break
        except Exception:
            pass

    if not pm:
        print("[-] FiveM no esta abierto.")
        input()
        return

    print(f"[+] Conectado a {target_process} (PID: {pm.process_id})")
    module = pymem.process.module_from_name(pm.process_handle, target_process)
    base = module.lpBaseOfDll
    size = module.SizeOfImage

    world_patterns = [
        (b'\x48\x8B\x05\x00\x00\x00\x00\x45\x00\x00\x00\x48\x8B\x48\x08\x48\x85\xC9', 'xxx????x???xxxxxx'),
        (b'\x48\x8B\x05\x00\x00\x00\x00\x45\x8B', 'xxx????xx'),
        (b'\x48\x8B\x05\x00\x00\x00\x00\x48\x8B\x48\x08', 'xxx????xxxx'),
        (b'\x48\x8B\x05\x00\x00\x00\x00\x48\x8B\x08', 'xxx????xxx'),
    ]
    
    replay_patterns = [
        (b'\x48\x8D\x0D\x00\x00\x00\x00\x48\x8B\xD7', 'xxx????xx'),
        (b'\x48\x8D\x0D\x00\x00\x00\x00\x48\x8B\xD6', 'xxx????xx'),
    ]
    
    viewport_patterns = [
        (b'\x48\x8B\x15\x00\x00\x00\x00\x48\x8D\x2D\x00\x00\x00\x00\x48\x8B\xCD', 'xxx????xxx????xxx'),
        (b'\x48\x8B\x15\x00\x00\x00\x00\x48\x8D\x2D', 'xxx????xxx'),
    ]

    print("[*] Escaneando memoria por bloques...")
    world_addr = replay_addr = viewport_addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    addr = base
    end = base + size

    while addr < end:
        if not ctypes.windll.kernel32.VirtualQueryEx(pm.process_handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == 0x1000:
            chunk = read_region(pm, addr, mbi.RegionSize)
            if chunk:
                if not world_addr:
                    for p, m in world_patterns:
                        off = pattern_scan_region(chunk, p, m)
                        if off: world_addr = addr + off; break
                if not replay_addr:
                    for p, m in replay_patterns:
                        off = pattern_scan_region(chunk, p, m)
                        if off: replay_addr = addr + off; break
                if not viewport_addr:
                    for p, m in viewport_patterns:
                        off = pattern_scan_region(chunk, p, m)
                        if off: viewport_addr = addr + off; break
                if world_addr and replay_addr and viewport_addr:
                    break
        addr += mbi.RegionSize

    def get_offset(addr, base, pm):
        if not addr: return 0
        rel = pm.read_int(addr + 3)
        return rel + 7 + (addr - base)

    if world_addr and replay_addr and viewport_addr:
        world_off = get_offset(world_addr, base, pm)
        replay_off = get_offset(replay_addr, base, pm)
        viewport_off = get_offset(viewport_addr, base, pm)
        
        print("\n--- OFFSETS CORRECTOS ---")
        print(f"world: {world_off}")
        print(f"replay: {replay_off}")
        print(f"viewport: {viewport_off}")
        
        with open("offsets.json", "w") as f:
            f.write(f'{{\n  "world": {world_off},\n  "replay": {replay_off},\n  "viewport": {viewport_off},\n  "localplayer": 8,\n  "pos": 144,\n  "ped_list": 24\n}}\n')
        print("\n[+] offsets.json generado.")
    else:
        print("\n[-] ERROR: Patrones no encontrados.")
        print("Si esto falla, el juego cambio mucho. Usa el dumper de Master-Dream404 en GitHub.")

    input("\nENTER para salir...")

if __name__ == "__main__":
    main()