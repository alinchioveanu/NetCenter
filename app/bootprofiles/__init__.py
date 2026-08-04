from .winpe import generate as winpe
from .windows_setup import generate as windows_setup
from .linux_live import generate as linux_live
from .rescue_iso import generate as rescue_iso

GENERATORS = {
    "winpe": winpe,
    "windows_setup": windows_setup,
    "linux_live": linux_live,
    "rescue_iso": rescue_iso,
}
