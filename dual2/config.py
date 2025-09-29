

"""
This configuration accepts an RS485 board in the front slot (board1), and can have processor boards in the horizontal slots:
- an ESP32-C3-zero board in the board3 position
- a lolin S3 mini board (or similar) in the board2 position
There is only one row of 2 wagos (lower wago row)
"""

# ============================ extend path with ============================================

import sys
sys.path.append('../')
from din_declarations import *    


# ======================================== PARAMETERS ======================================
# configuratoin declaration 
#
# currently only designed for 3 boards

config = Config (
    CONFIG_NAME     = "dual2",
    board1 = Board("front", # vertical board behind front
                   board_width=16,
                   length=43.4,
                   thickness=2.0,
                   usb_height = None,
                   mount_height = 12, # vertical board behind front
                   leds= [ Led( x=1.4, y=21.0, txt=""), Led( x=3.8, y=21.0, txt="")] 
                   ), 
    board2 = Board("top", # lolin S3 mini board (or equivalent)
                   board_width=26,
                   length=35,
                   thickness=2.0,
                   usb_height = 1.8, 
                   mount_height = 2.5, # assuming no jst connector that needs mount height
                   jst_extrawidth_left = 1.4 # space for button
                   ),
    board3 = Board("bottom", # esp32-c3-zero board
                   board_width=18,
                   length=24, 
                   thickness=2.0,
                   usb_height = 1.8,
                   mount_height = 1.5, # extra low for jst xh connector space
                   jst_extrawidth_right = 2.0 # jst xh connector
                   ),

    BRAND             = "@infradom",
 
    MODULE_NAME       =  None, # "modbus1"
    NR_WAGO_TOP       =  0,    # number of wago 221 at top
    NR_WAGO_BOTTOM    =  2,    # number of wago 221 at bottom
    WAGO_UPPER_TEXT   =  [ ],  # single character strings recommended
    WAGO_LOWER_TEXT   =  ["A", "B"], #["5", "0", ] # single character strings recommended
    CASE_WIDTH        = 18,    # standard unit = 18 mm - unless wago count makes it wider
    CASE_THICKNESS    =  2,    # untested if you modify this

    SCREW_HOLE_DIAM    =  3,      # diameter of hole for screw body (thread diam)
    SCREW_HEAD_DIAM    =  5.6,    # diameter of the hole for screw head
    SCREW_HEAD_DEPTH   =  2.5,
    SCREW_INSERT_DIAM  =  4.3,    # set equal to SCREW_HOLE_DIAM if working without insert
    SCREW_INSERT_DEPTH =  4.1,
    SCREW_HOLE_DEPTH   =  12,
    SCREW_BLOCK_SIZE   =  7.0,
    SCREW_LID_EXTRA    =  3.5,

    WAGO_TXT_SIZE      = 4,

    # ================ DIN RAIL - QUASI FIXED DIMENTIONS =========
    # usually no need to modify
    DIN_HEIGHT        = 82,    # can be modified slightly
    DIN_DEEP_HIGH     = 55,    # typical 60 - can be modified slightly
    DIN_DEEP_LOW      = 47,    # almost no room for modification (if board 1 is installed)
    DIN_NARROW_HEIGHT = 45,    # fixed - visible front height
    DIN_RAIL_LOWER    = 18.7,  # fixed - between middle of front and bottom of rail
    DIN_RAIL_UPPER    = 17,    # fixed - etween middle of front and top of rail

    # OTHER QUASI FIXED DIMENSIONS
    WAGO_OFFSET          = 7.88,
    WAGO_FIX_WIDTH       = 5.0,
    WAGO_LIP_LENGTH      = 13,
    WAGO_HEIGHT          = 8.5,
    WAGO_LENGTH          = 35,

    # USB-C cutout dimension
    USB_WIDTH  = 9.3, # 9.1
    USB_HEIGHT = 3.3, # 3.3 some margin for easy insertion

    BOARD_FIX_WIDTH = 2.2,
    LIGHT_GUIDE_DIAMETER = 2.0,
    LIGHT_CARRIER_DIAM = 3.3
)

# ======================================= END of the config part =================================
import cadquery as cq
import din_enclosure
if 'show_object' not in globals(): # if running outside cq-editor
    def show_object(*args, **kwargs):
        pass

din_enclosure.generate_enclosure(config)
din_enclosure.show_object = show_object
din_enclosure.show()
