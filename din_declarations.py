
from dataclasses import dataclass

@dataclass
class Led:
    x: float # from lower left component-side corner of board
    y: float # from lower_left component-side corner of board
    txt: str = ""
    
# front board  : usb up orientation(if any) 
# top board    : usb up orientation
# bottom board : usb down orientation

@dataclass
class Board:
    position:     str # either "top" | "bottom"| "front"
    board_width:  float  # excluding optional JST XH connectors
    length:       float
    thickness:    float = 1.5
    usb_height:   float | None = None   # center to under side of board; None if no usb required
    mount_height: float = 0 # from inner floor of case to under side of board
                            # id position = front: vertical board: front to upper side of board
    jst_extrawidth_left:  float = 0     # jst xh connector may extend beyond border e.g. 2 mm
    jst_extrawidth_right: float = 0     # jst xh connector may extend beyond border e.e. 2 mm
    leds:         list  | None = None   # list of Led declarations

    @property
    def width(self): return self.board_width + self.jst_extrawidth_left + self.jst_extrawidth_right

    @property
    def usb_offset(self): return (self.jst_extrawidth_left - self.jst_extrawidth_right)/2

    