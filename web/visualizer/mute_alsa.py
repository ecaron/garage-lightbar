"""Make Alsa's text output less noisy"""
import ctypes

ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
    None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p
)


def py_error_handler(filename, line, function, err, fmt): # pylint: disable=unused-argument
    """Capture the error handle, but don't do anything with it"""
    pass # pylint: disable=unnecessary-pass


c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

try:
    asound = ctypes.cdll.LoadLibrary("libasound.so.2")
    asound.snd_lib_error_set_handler(c_error_handler)
except OSError:
    pass
