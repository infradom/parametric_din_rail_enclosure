
from dataclasses import dataclass, field

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

@dataclass
class Config:
    CONFIG_NAME:        str       = "modbus1"
    board1:   callable = field(default_factory = lambda: Board("front",  board_width=16,   length=43.4, thickness=2.0, usb_height = None, mount_height = 12, # vertical board behind front
                         leds= [ Led( x=1.4, y=21.0, txt=""), Led( x=3.8, y=21.0, txt="")] )   )              # vertical board behind front
    board2:   callable = field(default_factory = lambda: Board("top", board_width=26, length=35, thickness=2.0, usb_height = 1.8,  mount_height = 2.5, # mini C3 or S3 board
                         jst_extrawidth_left = 0.0) )
    board3:   callable = field(default_factory= lambda: Board("bottom",    board_width=18,   length=24, thickness=2.0, usb_height = 1.8,  mount_height = 1.5, # 23.2 length for C3 zero; 24 length for S3 zerp
                         jst_extrawidth_right = 0.0) )

    BRAND:              str       = "@infradom"

    MODULE_NAME:        str       =  None # "modbus1"
    NR_WAGO_TOP:        int       =  0    # number of wago 221 at top
    NR_WAGO_BOTTOM:     int       =  2    # number of wago 221 at bottom
    WAGO_UPPER_TEXT:    list      =  field(default_factory=lambda: []) # list of strings - single character strings recommended
    WAGO_LOWER_TEXT:    list      =  field(default_factory=lambda: ["A", "B"]) #["5", "0", ] # list of strings - single character strings recommended
    CASE_WIDTH:         float     = 18    # standard unit = 18 mm - unless wago count makes it wider
    CASE_THICKNESS:     float     =  2    # untested if you modify this

    SCREW_HOLE_DIAM:    float   =  3      # diameter of hole for screw body (thread diam)
    SCREW_HEAD_DIAM:    float   =  5.6    # diameter of the hole for screw head
    SCREW_HEAD_DEPTH:   float   =  2.5
    SCREW_INSERT_DIAM:  float   =  4.3    # set equal to SCREW_HOLE_DIAM if working without insert
    SCREW_INSERT_DEPTH: float   =  4.1
    SCREW_HOLE_DEPTH:   float   =  12
    SCREW_BLOCK_SIZE:   float   =  7.0
    SCREW_LID_EXTRA:    float   =  3.5

    WAGO_TXT_SIZE:      float   = 4

    # ================ DIN RAIL - QUASI FIXED DIMENTIONS =========
    # usually no need to modify
    DIN_HEIGHT:        float = 82    # can be modified slightly
    DIN_DEEP_HIGH:     float = 55    # typical 60 - can be modified slightly
    DIN_DEEP_LOW:      float = 47    # almost no room for modification (if board 1 is installed)
    DIN_NARROW_HEIGHT: float = 45    # fixed - visible front height
    DIN_RAIL_LOWER:    float = 18.7  # fixed - between middle of front and bottom of rail
    DIN_RAIL_UPPER:    float = 17    # fixed - etween middle of front and top of rail

    # OTHER QUASI FIXED DIMENSIONS
    WAGO_OFFSET:       float = 7.88
    WAGO_FIX_WIDTH:    float = 5.0
    WAGO_LIP_LENGTH:   float = 13
    WAGO_HEIGHT:       float = 8.5
    WAGO_LENGTH:       float = 35

    # USB-C cutout dimension
    USB_WIDTH:         float = 9.3 # 9.1
    USB_HEIGHT:        float = 3.3 # 3.3 some margin for easy insertion

    BOARD_FIX_WIDTH:      float= 2.2
    LIGHT_GUIDE_DIAMETER: float = 2.0
    LIGHT_CARRIER_DIAM:   float = LIGHT_GUIDE_DIAMETER+1.3


