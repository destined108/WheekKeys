"""Windows key-down counting. No text conversion, event log, or network I/O."""
import ctypes
from ctypes import wintypes
import sys
import threading

MODIFIERS = {16, 17, 18, 91, 92, 160, 161, 162, 163, 164, 165}


class PressAccumulator:
    def __init__(self):
        self.down = set()
        self.count = 0

    def event(self, key, pressed):
        if key < 8 or key in MODIFIERS:
            return
        if pressed:
            if key not in self.down:
                self.count += 1
                self.down.add(key)
        else:
            self.down.discard(key)

    def drain(self):
        count, self.count = self.count, 0
        return count


class KeyCounter:
    """A message-pumped hook catches taps between animation frames."""
    def __init__(self):
        if sys.platform != 'win32':
            raise RuntimeError('Global typing detection requires Windows.')
        self.accumulator = PressAccumulator()
        self.lock = threading.Lock()
        self.ready = threading.Event()
        self.error = None
        self.thread_id = None
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        # Explicit pointer-sized signatures are essential on 64-bit Windows.
        self.user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
        self.user32.SetWindowsHookExW.restype = wintypes.HANDLE
        self.user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        self.user32.CallNextHookEx.restype = ctypes.c_ssize_t
        self.user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
        self.user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        self.user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        self.user32.GetMessageW.restype = wintypes.BOOL
        self.user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
        self.user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        self.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        if not self.ready.wait(5):
            self.close()
            raise RuntimeError('Keyboard listener did not start. Try restarting WheekKeys.')
        if self.error:
            raise RuntimeError(f'Cannot start keyboard listener: {self.error}')

    def _listen(self):
        class KeyboardEvent(ctypes.Structure):
            _fields_ = [('vkCode', wintypes.DWORD), ('scanCode', wintypes.DWORD),
                        ('flags', wintypes.DWORD), ('time', wintypes.DWORD),
                        ('dwExtraInfo', ctypes.c_size_t)]
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        def receive(code, message, address):
            if code == 0 and message in (0x100, 0x101, 0x104, 0x105):
                # Only the key identifier is examined for hold/repeat deduplication.
                key = ctypes.cast(address, ctypes.POINTER(KeyboardEvent)).contents.vkCode
                with self.lock:
                    self.accumulator.event(key, message in (0x100, 0x104))
            return self.user32.CallNextHookEx(None, code, message, address)

        callback = callback_type(receive)  # Retain until the hook is removed.
        hook = None
        try:
            self.thread_id = self.kernel32.GetCurrentThreadId()
            msg = wintypes.MSG()
            self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
            hook = self.user32.SetWindowsHookExW(13, callback, self.kernel32.GetModuleHandleW(None), 0)
            if not hook:
                raise ctypes.WinError(ctypes.get_last_error())
            self.ready.set()
            while True:
                result = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result == 0:
                    break
                if result == -1:
                    raise ctypes.WinError(ctypes.get_last_error())
        except Exception as error:
            self.error = str(error)
        finally:
            if hook:
                self.user32.UnhookWindowsHookEx(hook)
            self.ready.set()

    def poll(self):
        if self.error:
            raise RuntimeError(f'Keyboard listener stopped: {self.error}')
        with self.lock:
            return self.accumulator.drain()

    def close(self):
        if self.thread_id:
            self.user32.PostThreadMessageW(self.thread_id, 0x12, 0, 0)  # WM_QUIT
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2)
