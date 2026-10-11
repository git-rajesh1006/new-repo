"""Offline Telugu text-to-speech via the espeak-ng library bundled in `espeakng-loader`."""
import ctypes, numpy as np, espeakng_loader

_lib = ctypes.CDLL(espeakng_loader.get_library_path())
_lib.espeak_Initialize.restype = ctypes.c_int
SR = _lib.espeak_Initialize(2, 0, espeakng_loader.get_data_path().encode(), 0)
_buf = []
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
@CB
def _cb(wav, n, ev):
    if wav and n > 0: _buf.append(np.ctypeslib.as_array(wav, (n,)).copy())
    return 0
_lib.espeak_SetSynthCallback(_cb)
assert _lib.espeak_SetVoiceByName(b"te") == 0

def speak(text, rate=105, pitch=55):
    _lib.espeak_SetParameter(1, rate, 0); _lib.espeak_SetParameter(3, pitch, 0)
    _buf.clear(); b = text.encode()
    _lib.espeak_Synth(b, len(b) + 1, 0, 1, 0, 1, None, None); _lib.espeak_Synchronize()
    return (np.concatenate(_buf).astype(np.float32) / 32768.0) if _buf else np.zeros(1, np.float32)
