# copyright @infradom
# ======================= component class declarations ========

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
    
    
# ======================================== PARAMETERS ======================================
# this small part of the program can be redistributed to create other enclosure descriptions
#
# currently only designed for 3 boards

board1 = Board("front",  board_width=16,   length=43.4, thickness=2.0, usb_height = None, mount_height = 10, # vertical board behind front
                         leds= [ Led( x=1.4, y=21.0, txt=""), Led( x=3.8, y=21.0, txt="")] )                 # vertical board behind front
board2 = Board("top",    board_width=18,   length=23.2, thickness=2.0, usb_height = 1.8,  mount_height = 3.0, # 23.2 length for C3 zero; 24 length for S3 zerp
                         jst_extrawidth_right = 2.0)
board3 = Board("bottom", board_width=25.5, length=32.5, thickness=2.0, usb_height = 1.8,  mount_height = 3.0, # mini C3 or S3 board
                         jst_extrawidth_left = 0.0)

    


MODULE_NAME       =  None # "modbus1"
NR_WAGO_TOP       =  2    # number of wago 221 at top
NR_WAGO_BOTTOM    =  2    # number of wago 221 at bottom
WAGO_UPPER_TEXT   =  ["+5", "0", ]  # single character strings recommended
WAGO_LOWER_TEXT   =  ["A", "B", ] # single character strings recommended
CASE_WIDTH        = 18    # standard unit = 18 mm - unless wago count makes it wider
CASE_THICKNESS    =  2    # untested if you modify this

SCREW_HOLE_DIAM    =  3      # diameter of hole for screw body (thread diam)
SCREW_HEAD_DIAM    =  5.6    # diameter of the hole for screw head
SCREW_HEAD_DEPTH   =  2.5
SCREW_INSERT_DIAM  =  4.3    # set equal to SCREW_HOLE_DIAM if working without insert
SCREW_INSERT_DEPTH =  4.1
SCREW_HOLE_DEPTH   =  12
SCREW_BLOCK_SIZE   =  7.0
SCREW_LID_EXTRA    =  3.5

WAGO_TXT_SIZE = 4

# ================ DIN RAIL - QUASI FIXED DIMENTIONS =========
# usually no need to modify
DIN_HEIGHT        = 82    # can be modified slightly
DIN_DEEP_HIGH     = 55    # typical 60 - can be modified slightly
DIN_DEEP_LOW      = 49    # almost no room for modification (if board 1 is installed)
DIN_NARROW_HEIGHT = 45    # fixed - visible front height
DIN_RAIL_LOWER    = 18.7  # fixed - between middle of front and bottom of rail
DIN_RAIL_UPPER    = 17    # fixed - etween middle of front and top of rail

# OTHER QUASI FIXED DIMENSIONS
WAGO_OFFSET          = 7.88
WAGO_FIX_WIDTH       = 5.0
WAGO_LIP_LENGTH      = 13
WAGO_HEIGHT          = 8.5
WAGO_LENGTH          = 35

# USB-C cutout dimension
USB_WIDTH  = 9.3 # 9.1
USB_HEIGHT = 3.3 # 3.3 some margin for easy insertion

BOARD_FIX_WIDTH = 2.2
LIGHT_GUIDE_DIAMETER = 2.0
LIGHT_CARRIER_DIAM = LIGHT_GUIDE_DIAMETER+1.3


# ======================================= END of the redistributable part =================================

# ======================================== start of the more restricted part ==============================
# copyright @infradom

# ========================== import cadquery ===========================

import cadquery as cq
from cadquery.func import *
from pathlib import Path
import os
print(cq.__version__)


# ============================ Sanity checks ===========================


WAGO_POS_DEPTH_UPPER = board2.width+2*CASE_THICKNESS # from front of rail
WAGO_POS_DEPTH_LOWER = board3.width+2*CASE_THICKNESS # from front of rail


if ((NR_WAGO_BOTTOM*WAGO_OFFSET + CASE_THICKNESS > CASE_WIDTH) or 
    (NR_WAGO_TOP*WAGO_OFFSET + CASE_THICKNESS > CASE_WIDTH)):
    print(f"Warning: extending case width to support more WAGO's")
    CASE_WIDTH = max(NR_WAGO_BOTTOM, NR_WAGO_TOP)*WAGO_OFFSET + CASE_THICKNESS
    
if (len(WAGO_UPPER_TEXT) < NR_WAGO_TOP) or (len(WAGO_LOWER_TEXT) < NR_WAGO_BOTTOM):
    print(f"Warning: please extend WAGO_UPPER_TEXT or WAGO_LOWER_TEXT lists")
while len(WAGO_UPPER_TEXT) < NR_WAGO_TOP:    WAGO_UPPER_TEXT.append("U") # Undefined
while len(WAGO_LOWER_TEXT) < NR_WAGO_BOTTOM: WAGO_LOWER_TEXT.append("U") # Undefined


# ======================== dummy cutout (or union) object ==================
# at a harmless place

dummy_cutout = cq.Workplane("XY").box(0.1 , 0.1 , 0.1).translate((-0.1, DIN_HEIGHT/2 - 10, 5))

# ======================== DIN rail clip ===================================

CLIP_GAP   = 0.1
CLIP_WIDTH = CASE_WIDTH - 2*CASE_THICKNESS - 2*CLIP_GAP
CLIP_THICKNESS = 3.5
CLIP_SLOT_DEPTH = CLIP_THICKNESS
CLIP_HIDDEN_LENGTH = DIN_HEIGHT/2 - DIN_RAIL_LOWER + CLIP_SLOT_DEPTH
CLIP_TOP_HEIGHT = 8
CLIP_LEG_WIDTH = 2.6
CLIP_LEG_HEADROOM = 1

CLIP_LEG_RADIUS = 1.2
CLIP_LEG_LENGTH = CLIP_HIDDEN_LENGTH - CLIP_TOP_HEIGHT - CLIP_LEG_HEADROOM
CLIP_LEG_GAP_WIDTH = 1.5

CLIP_BASE_HEIGHT = 6
CLIP_CHAMFER = 1.5

CLIP_UPPER_LOCK = CLIP_TOP_HEIGHT - CLIP_SLOT_DEPTH + CLIP_LEG_HEADROOM + CLIP_LEG_RADIUS # below bottom of din rail
CLIP_LOCK_DISTANCE = 5
CLIP_SLOT_WIDTH = 1.4
CLIP_SLOT_TAPER = 3


clip = ( cq.Workplane("front")
    .moveTo(0, -CLIP_BASE_HEIGHT)
    .hLine(CLIP_WIDTH/2.0)
    .vLine(CLIP_LEG_LENGTH + CLIP_BASE_HEIGHT - 2*CLIP_LEG_RADIUS)
    .threePointArc((CLIP_WIDTH/2 + CLIP_LEG_RADIUS, CLIP_LEG_LENGTH - CLIP_LEG_RADIUS), (CLIP_WIDTH/2 , CLIP_LEG_LENGTH))
    .hLine(-CLIP_LEG_WIDTH)
    .vLine(-CLIP_LEG_LENGTH)
    .hLine(-CLIP_LEG_GAP_WIDTH)
    .vLine(CLIP_HIDDEN_LENGTH - CLIP_TOP_HEIGHT)
    .hLine( CLIP_LEG_GAP_WIDTH + CLIP_LEG_WIDTH)
    .vLine(CLIP_TOP_HEIGHT)
    .hLine(-CLIP_WIDTH/2)
    .mirrorY()
    .moveTo(0, -3)
    .rect(6, 2)
    .extrude(CLIP_THICKNESS)
    .edges(">(0, 1, -1)").chamfer(CLIP_CHAMFER)
    .edges("|Z")
    .fillet(0.5)
    .faces(">Y").workplane()
    .center(0,  (CLIP_THICKNESS-CLIP_SLOT_WIDTH/2+0.18))
    .rect(CLIP_WIDTH+3, CLIP_SLOT_WIDTH)
    .extrude(-CLIP_SLOT_DEPTH , combine='s', taper=CLIP_SLOT_TAPER)
    .rotate((0, 0, 0), (0, 1, 0), 90)
    .translate( (-(CLIP_THICKNESS + CLIP_GAP), -DIN_HEIGHT/2, CASE_WIDTH/2) )
)


CLIP_CUTOUT_HEIGHT = DIN_HEIGHT/2 - DIN_RAIL_LOWER
clip_cutout = cq.Workplane("XY").box(CLIP_THICKNESS + 2*CLIP_GAP, CLIP_CUTOUT_HEIGHT, CLIP_WIDTH + 2*CLIP_GAP)

clip_cutout = ( clip_cutout.faces("<X").workplane() 
      .center(-CLIP_CUTOUT_HEIGHT/2 + CLIP_UPPER_LOCK, -CLIP_WIDTH/2) #  mm below DIN rail space
      .circle(CLIP_LEG_RADIUS+CLIP_GAP) # upper clip slot 1
      .center(0, CLIP_WIDTH)
      .circle(CLIP_LEG_RADIUS+CLIP_GAP) # uppor clip slot 2
      .center(CLIP_LOCK_DISTANCE, 0)
      .circle(CLIP_LEG_RADIUS+CLIP_GAP) # lower clip slot 1
      .center(0, -CLIP_WIDTH)
      .circle(CLIP_LEG_RADIUS+CLIP_GAP) # lower clip slot 2
      .extrude(-CLIP_THICKNESS - 2*CLIP_GAP)
      )
clip_cutout = clip_cutout.translate((-CLIP_THICKNESS/2-CLIP_GAP, -CLIP_CUTOUT_HEIGHT/2 -DIN_RAIL_LOWER, CASE_WIDTH/2) )

# ======================== wago fixation parts =================

WAGO_FIX_HEIGHT = 2.5
WAGO_FIX_EXTRUDE = 1.25
def wago_fix(count, x, y, z):
    wago_221_fix    = cq.Workplane("front").box(CASE_WIDTH, WAGO_FIX_WIDTH, WAGO_FIX_HEIGHT).edges("#X").fillet(0.4)
    wago_fix_cutout = cq.Workplane("front").box(CASE_WIDTH +4, WAGO_FIX_WIDTH+0.1, WAGO_FIX_HEIGHT+0.1)
    wago_221_fix = wago_221_fix.center(-WAGO_OFFSET * (count - 1) / 2, 0).rect(4.0, 2.5).extrude(WAGO_FIX_EXTRUDE*2)
    for i in range(1, count): wago_221_fix = wago_221_fix.center(WAGO_OFFSET, 0).rect(4.0, 2.5).extrude(WAGO_FIX_EXTRUDE*2)
    wago_221_fix =    wago_221_fix.rotate((0, 0, 0), (0, 1, 0), -90).translate((x, y, z))
    wago_fix_cutout = wago_fix_cutout.rotate((0, 0, 0), (0, 1, 0), -90).translate((x, y, z))
    return wago_221_fix, wago_fix_cutout


bottom_wago_fix, bottom_wago_fix_cutout = wago_fix(NR_WAGO_BOTTOM,
      WAGO_POS_DEPTH_LOWER + WAGO_HEIGHT + WAGO_FIX_HEIGHT/2+WAGO_FIX_EXTRUDE - WAGO_FIX_EXTRUDE,
      -DIN_HEIGHT/2 + WAGO_LIP_LENGTH +WAGO_FIX_WIDTH/2 + CASE_THICKNESS,
      CASE_WIDTH/2 )
top_wago_fix, top_wago_fix_cutout   = wago_fix(NR_WAGO_TOP,
      WAGO_POS_DEPTH_UPPER + WAGO_HEIGHT + WAGO_FIX_HEIGHT/2+WAGO_FIX_EXTRUDE - WAGO_FIX_EXTRUDE,
      DIN_HEIGHT/2 - WAGO_LIP_LENGTH - WAGO_FIX_WIDTH/2 - CASE_THICKNESS,
      CASE_WIDTH/2 )


# ====================== main case =========================

sketch_outer = ( cq.Sketch()
    .segment( (0, DIN_RAIL_UPPER),(-0.8, DIN_RAIL_UPPER) )
    .segment( (-3.2, DIN_RAIL_UPPER - 3.2) )
    .segment( (-5, DIN_RAIL_UPPER - 3.2) )
    .segment( (-5, DIN_HEIGHT/2) )
    .segment( (board2.width+2*CASE_THICKNESS, DIN_HEIGHT/2))
    .segment( (board2.width+2*CASE_THICKNESS, DIN_HEIGHT/2-WAGO_LIP_LENGTH) )
    .segment( (DIN_DEEP_LOW, DIN_HEIGHT/2-WAGO_LIP_LENGTH) )
    .segment( (DIN_DEEP_LOW, DIN_NARROW_HEIGHT/2) )
    .segment( (DIN_DEEP_HIGH, DIN_NARROW_HEIGHT/2) )
    .segment( (DIN_DEEP_HIGH, -DIN_NARROW_HEIGHT/2) )
    .segment( (DIN_DEEP_LOW, -DIN_NARROW_HEIGHT/2) )
    .segment( (DIN_DEEP_LOW, -DIN_HEIGHT/2+WAGO_LIP_LENGTH) )
    .segment( (board3.width+2*CASE_THICKNESS,   -DIN_HEIGHT/2+WAGO_LIP_LENGTH) )
    .segment( (board3.width+2*CASE_THICKNESS,-DIN_HEIGHT/2))
    .segment( (-5, -DIN_HEIGHT/2) )
    .segment( (-5, -DIN_RAIL_LOWER) )
    .segment( (0, -DIN_RAIL_LOWER) )
    .close()
    .assemble(tag="outerface")
    .edges("|Z" and "<X", tag="outerface")
    .vertices()
    .fillet(0.5)
    .edges("|Z" and ">X", tag="outerface")
    .vertices()
    .fillet(1.5)
    .clean()
    )

sketch_inner = ( cq.Sketch()
    .segment( (CASE_THICKNESS, 0), (CASE_THICKNESS, DIN_HEIGHT/2 - CASE_THICKNESS) )
    .segment( (board2.width+CASE_THICKNESS, DIN_HEIGHT/2-CASE_THICKNESS))
    .segment( (board2.width+CASE_THICKNESS, DIN_HEIGHT/2-WAGO_LIP_LENGTH-CASE_THICKNESS) )
    .segment( (DIN_DEEP_LOW-CASE_THICKNESS, DIN_HEIGHT/2-WAGO_LIP_LENGTH-CASE_THICKNESS) )
    .segment( (DIN_DEEP_LOW - CASE_THICKNESS, DIN_HEIGHT/2 - CASE_THICKNESS) )
    .segment( (DIN_DEEP_LOW - CASE_THICKNESS, DIN_NARROW_HEIGHT/2 - CASE_THICKNESS) )
    .segment( (DIN_DEEP_HIGH -CASE_THICKNESS, DIN_NARROW_HEIGHT/2 - CASE_THICKNESS) )
    .segment( (DIN_DEEP_HIGH -CASE_THICKNESS, -DIN_NARROW_HEIGHT/2 + CASE_THICKNESS) )
    .segment( (DIN_DEEP_LOW - CASE_THICKNESS, -DIN_NARROW_HEIGHT/2 + CASE_THICKNESS) )
    .segment( (DIN_DEEP_LOW - CASE_THICKNESS, -DIN_HEIGHT/2+WAGO_LIP_LENGTH+CASE_THICKNESS) )
    .segment( (board3.width+CASE_THICKNESS, -DIN_HEIGHT/2+WAGO_LIP_LENGTH+CASE_THICKNESS) )
    .segment( (board3.width+CASE_THICKNESS,-DIN_HEIGHT/2+CASE_THICKNESS))
    .segment( ( CASE_THICKNESS, -DIN_HEIGHT/2 + CASE_THICKNESS) )
    .close()                
    .assemble(tag="innerface")
    .vertices()
    .fillet(0.6)
    .clean()
    )

outer  = cq.Workplane("XY").placeSketch(sketch_outer).extrude(CASE_WIDTH)
inner = cq.Workplane("XY",( 0.0, 0.0, CASE_WIDTH)).placeSketch(sketch_inner).extrude(-(CASE_WIDTH-CASE_THICKNESS))

def case_screw_block(x, y):
    z = CASE_WIDTH-2*CASE_THICKNESS-SCREW_LID_EXTRA
    return ( cq.Workplane("XY").box(SCREW_BLOCK_SIZE, SCREW_BLOCK_SIZE, z).faces(">Z").cboreHole(SCREW_HOLE_DIAM, SCREW_INSERT_DIAM, SCREW_INSERT_DEPTH, SCREW_HOLE_DEPTH)
    .translate((x, y , z/2+CASE_THICKNESS))
    .edges("|Z").fillet(1) )

def lid_screw_block(x, y):
    z = CASE_THICKNESS + SCREW_LID_EXTRA
    return ( cq.Workplane("XY").box(SCREW_BLOCK_SIZE, SCREW_BLOCK_SIZE, z)
    .translate((x, y , CASE_WIDTH - z/2))
    .edges("|Z").fillet(1) )

def screw_block_clip(board, x, y):
    z = CASE_WIDTH-2*CASE_THICKNESS-SCREW_LID_EXTRA-board.mount_height-board.thickness-1.5
    b1 = box(SCREW_BLOCK_SIZE+2, SCREW_BLOCK_SIZE+2, z)
    b2 = box(SCREW_BLOCK_SIZE, SCREW_BLOCK_SIZE,  z*2 + 2)
    return ( b1.cut(b2).translate((x , y, 0)) )  

def board_fix(board, centerX, centerY, rotate = False): # for horizontal boards only
    rad = 1
    th = 1.3
    w = BOARD_FIX_WIDTH
    if rotate: w = -w
    fix =  ( cq.Workplane("ZY", (centerX+BOARD_FIX_WIDTH/2, centerY, CASE_THICKNESS))
    .hLine(board.mount_height+board.thickness)
    .threePointArc( (board.mount_height+board.thickness+rad, rad), (board.mount_height+board.thickness+2*rad, 0) )
    .vLine(-th).hLine(-board.mount_height-board.thickness-2*rad).vLine(th).close()
    .extrude(w)
    #.edges("|X").
    #.fillet(0.3)
    )
    if rotate: fix = fix.rotate((centerX+BOARD_FIX_WIDTH/2, centerY, 0), (centerX+BOARD_FIX_WIDTH/2, centerY, 1), 180)
    return fix

board_fixes = ( board_fix(board2, board2.width + CASE_THICKNESS -3-board2.jst_extrawidth_right,  DIN_HEIGHT/2-CASE_THICKNESS-board2.length, False)
                .union(board_fix(board2, CASE_THICKNESS +3+board2.jst_extrawidth_left,  DIN_HEIGHT/2-CASE_THICKNESS-board2.length, False))
                .union(board_fix(board3, board3.width + CASE_THICKNESS -3+board3.jst_extrawidth_right, -DIN_HEIGHT/2+CASE_THICKNESS+board3.length, True))
                .union(board_fix(board3, CASE_THICKNESS +3+board3.jst_extrawidth_left, -DIN_HEIGHT/2+CASE_THICKNESS+board3.length, True))
              )

wago_support_upper = ( cq.Workplane("XY").box(CASE_THICKNESS, WAGO_LENGTH, CASE_WIDTH-2*CASE_THICKNESS)
    .translate((WAGO_POS_DEPTH_UPPER - CASE_THICKNESS/2, DIN_HEIGHT/2-WAGO_LENGTH/2 , CASE_WIDTH/2)) )
wago_support_lower = ( cq.Workplane("XY").box(CASE_THICKNESS, WAGO_LENGTH, CASE_WIDTH-2*CASE_THICKNESS)
    .translate((WAGO_POS_DEPTH_LOWER - CASE_THICKNESS/2, -DIN_HEIGHT/2+WAGO_LENGTH/2 , CASE_WIDTH/2)) )

screw_positions = [ 
           (WAGO_POS_DEPTH_UPPER + WAGO_HEIGHT + SCREW_BLOCK_SIZE/2 + WAGO_FIX_HEIGHT,  DIN_HEIGHT/2-WAGO_LIP_LENGTH - CASE_THICKNESS - SCREW_BLOCK_SIZE/2, ),
           (WAGO_POS_DEPTH_LOWER + WAGO_HEIGHT + SCREW_BLOCK_SIZE/2 + WAGO_FIX_HEIGHT, -DIN_HEIGHT/2+WAGO_LIP_LENGTH + CASE_THICKNESS + SCREW_BLOCK_SIZE/2, ),
           (board2.width/2 + CASE_THICKNESS, DIN_HEIGHT/2-CASE_THICKNESS-board2.length - SCREW_BLOCK_SIZE/2, ),
           (board3.width/2 + CASE_THICKNESS, -DIN_HEIGHT/2+CASE_THICKNESS+board3.length + SCREW_BLOCK_SIZE/2,),
    ]

case_screw_blocks = []
lid_screw_blocks  = []
for (x, y,) in screw_positions: case_screw_blocks.append(case_screw_block(x, y))
for (x, y,) in screw_positions: lid_screw_blocks.append(lid_screw_block(x, y))

screw_block_clip2 = screw_block_clip(board2, 0, -20)
screw_block_clip3 = screw_block_clip(board3, 0, -30)



if NR_WAGO_TOP > 0:
    wago_upper_cutout = cq.Workplane("XY", (WAGO_POS_DEPTH_UPPER + WAGO_HEIGHT/2, DIN_HEIGHT/2-WAGO_LENGTH/2 , CASE_WIDTH/2)).box(WAGO_HEIGHT, WAGO_LENGTH, WAGO_OFFSET*NR_WAGO_TOP)
    wago_upper_lid_addon = cq.Workplane("XY", (WAGO_POS_DEPTH_UPPER + WAGO_HEIGHT/2, DIN_HEIGHT/2 - WAGO_LIP_LENGTH - CASE_THICKNESS/2 , CASE_WIDTH/2 + 0*CASE_THICKNESS + NR_WAGO_TOP*WAGO_OFFSET/2)).box(WAGO_HEIGHT, CASE_THICKNESS, CASE_WIDTH - NR_WAGO_TOP*WAGO_OFFSET)
else: 
    wago_upper_cutout = dummy_cutout
    wago_upper_lid_addon = dummy_cutout
if NR_WAGO_BOTTOM > 0:
    wago_lower_cutout = cq.Workplane("XY", (WAGO_POS_DEPTH_LOWER + WAGO_HEIGHT/2, -DIN_HEIGHT/2+WAGO_LENGTH/2 , CASE_WIDTH/2)).box(WAGO_HEIGHT, WAGO_LENGTH, WAGO_OFFSET*NR_WAGO_BOTTOM)
    wago_lower_lid_addon = cq.Workplane("XY", (WAGO_POS_DEPTH_LOWER + WAGO_HEIGHT/2, -DIN_HEIGHT/2 + WAGO_LIP_LENGTH + CASE_THICKNESS/2 , CASE_WIDTH/2 + 0*CASE_THICKNESS + NR_WAGO_BOTTOM*WAGO_OFFSET/2)).box(WAGO_HEIGHT, CASE_THICKNESS, CASE_WIDTH - NR_WAGO_BOTTOM*WAGO_OFFSET)
else: 
    wago_lower_cutout = dummy_cutout
    wago_lower_lid_addon = dummy_cutout

b1_carrier_height = CASE_WIDTH - board1.width - CASE_THICKNESS
if b1_carrier_height>0:
    board1_carrier = cq.Workplane("XY", (DIN_DEEP_HIGH-board1.mount_height, DIN_HEIGHT/2 -WAGO_LIP_LENGTH -board1.length/2 -CASE_THICKNESS/2, CASE_THICKNESS + b1_carrier_height/2)).box(board1.thickness+3, board1.length + CASE_THICKNESS, b1_carrier_height)
else: board1_carrier = dummy_cutout

board1_carrier = board1_carrier.union(cq.Workplane("XY", (DIN_DEEP_HIGH-board1.mount_height + board1.thickness/2 , DIN_HEIGHT/2 -WAGO_LIP_LENGTH -board1.length-CASE_THICKNESS/2 -0, CASE_WIDTH/2+b1_carrier_height/2)).box(CASE_THICKNESS+2, CASE_THICKNESS, board1.width-CASE_THICKNESS/2))
board1_cutout = cq.Workplane("XY", (DIN_DEEP_HIGH-board1.mount_height,DIN_HEIGHT/2 -WAGO_LIP_LENGTH -board1.length/2 -CASE_THICKNESS/2, CASE_WIDTH/2+b1_carrier_height/2)).box(board1.thickness, board1.length, board1.width)

def usb_cutout(workplane, x, y, z, extrude):
    return ( cq.Workplane(workplane, (x, y, z))
        .moveTo(0, USB_HEIGHT/2)
        .hLine(USB_WIDTH/2 -USB_HEIGHT/2)
        .threePointArc((USB_WIDTH/2, 0),  ( USB_WIDTH/2 - USB_HEIGHT/2, -USB_HEIGHT/2))
        .hLine(-USB_WIDTH + USB_HEIGHT)
        .threePointArc((-USB_WIDTH/2, 0), (-USB_WIDTH/2 + USB_HEIGHT/2, +USB_HEIGHT/2))
        .hLine(USB_WIDTH/2 - USB_HEIGHT/2)
        .close()
        .extrude(extrude, taper = -30) )


if board1.usb_height is None: usb_front_cutout = dummy_cutout
else: usb_front_cutout = usb_cutout("ZX", DIN_DEEP_HIGH + board1.usb_height + board1.thickness/2 - board1.mount_height, DIN_HEIGHT/2 - WAGO_LIP_LENGTH, CASE_WIDTH/2+b1_carrier_height/2 - board1.usb_offset, -CASE_THICKNESS)
if board2.usb_height is None: usb_upper_cutout = dummy_cutout
else: usb_upper_cutout = usb_cutout("XZ", CASE_THICKNESS+board2.width/2+board2.usb_offset,  DIN_HEIGHT/2, CASE_THICKNESS+board2.usb_height+board2.mount_height+board2.thickness, CASE_THICKNESS )
if board3.usb_height is None: usb_lower_cutout = dummy_cutout
else: usb_lower_cutout = usb_cutout("XZ",CASE_THICKNESS+board3.width/2+board3.usb_offset, -DIN_HEIGHT/2, CASE_THICKNESS+board3.usb_height+board3.mount_height+board3.thickness, -CASE_THICKNESS)



CARRIER_X = 7
CARRIER_Y = 2
board2_carriers =  ( cq.Workplane("XY", (0, -CASE_THICKNESS, CASE_THICKNESS))
        .pushPoints([ (CASE_THICKNESS + board2.width/2 + board2.usb_offset, DIN_HEIGHT/2 -CARRIER_Y/2),
                      (CASE_THICKNESS + board2.width/2, DIN_HEIGHT/2 -board2.length+CARRIER_Y/2) ])
        .rect(CARRIER_X, CARRIER_Y)
        .extrude(board2.mount_height) )
board3_carriers = ( cq.Workplane("XY", (0, +CASE_THICKNESS, CASE_THICKNESS))
        .pushPoints( [(CASE_THICKNESS + board3.width/2 + board3.usb_offset, -DIN_HEIGHT/2 + CARRIER_Y/2 ),
                   (CASE_THICKNESS + board3.width/2, -DIN_HEIGHT/2 +board3.length -CARRIER_Y/2) ])
        .rect(CARRIER_X, CARRIER_Y)
        .extrude(board3.mount_height) )

def ledcarrier(board):
    if board.position == "front": # currently only supported case
        carrier = cq.Workplane("ZY", (DIN_DEEP_HIGH, DIN_HEIGHT/2 - WAGO_LIP_LENGTH - CASE_THICKNESS/2 - board.length, CASE_WIDTH - CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
        for led in board.leds:
            #c1 = carrier.moveTo((CASE_WIDTH-CASE_THICKNESS)/2, led.y).rect(CASE_WIDTH-2*CASE_THICKNESS, LIGHT_CARRIER_DIAM).extrude(-board.mount_height +4) 
            c = carrier.moveTo(led.x, led.y).rect(LIGHT_CARRIER_DIAM, LIGHT_CARRIER_DIAM).extrude(-board.mount_height + board.thickness/2+0.4) # 0.4: dont touch the led'
            carrier = carrier.union(c)
        return carrier


def ledcutout(board):
    if board.position == "front": # currently only supported case
        carrier = cq.Workplane("ZY", (DIN_DEEP_HIGH, DIN_HEIGHT/2 - WAGO_LIP_LENGTH - CASE_THICKNESS/2 - board.length, CASE_WIDTH - CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
        lidwp   = cq.Workplane("ZY", (DIN_DEEP_HIGH, DIN_HEIGHT/2 - WAGO_LIP_LENGTH - CASE_THICKNESS/2 - board.length, CASE_WIDTH - CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
        txtwp   = cq.Workplane("ZY", (DIN_DEEP_HIGH, DIN_HEIGHT/2 - WAGO_LIP_LENGTH - CASE_THICKNESS/2 - board.length, CASE_WIDTH - CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
        txt = txtwp.union(dummy_cutout)
        lid = lidwp
        for led in board.leds:
            c  = carrier.moveTo(led.x, led.y).circle(LIGHT_GUIDE_DIAMETER/2).extrude(-board.mount_height + 0.2)
            cl = carrier.moveTo(led.x, led.y).rect(LIGHT_CARRIER_DIAM+0.1, LIGHT_CARRIER_DIAM+0.25 ).extrude(-board.mount_height -0.2 )
            carrier = carrier.union(c)
            lid     = lid.union(cl)
            if led.txt: txt     = txt.union(txtwp.center(led.x, led.y+2.7).text(led.txt, 2.7, -0.3))
        return (carrier, lid, txt) #carrier.union(txt)

board1_ledcarrier = ledcarrier(board1)
(case_ledcutout, lid_ledcutout, led_txtcutout)  = ledcutout(board1)

# ========================== case text ======================================

text_brand  = cq.Workplane("YX").center(0,12).text("@infradom", 8, -0.3)
if MODULE_NAME: text_name = cq.Workplane("YZ", (DIN_DEEP_HIGH, -DIN_NARROW_HEIGHT/2+2.5, 5)).text(MODULE_NAME, 6, -0.3, kind="bold", halign="left")
else: text_name = dummy_cutout

#text_upper = case.faces("<X[2]").workplane().transformed(rotate=(0, 0, -90))

wp = cq.Workplane("ZY", (DIN_DEEP_LOW, DIN_NARROW_HEIGHT/2+2.6, CASE_WIDTH/2) ).transformed(rotate = cq.Vector(0, 180, 0))
text_upper = wp
for i in range(0, NR_WAGO_TOP) :
    text_upper = text_upper.union( wp.center( - (NR_WAGO_TOP-1)*WAGO_OFFSET/2 + i*WAGO_OFFSET, 0).text(WAGO_UPPER_TEXT[i], WAGO_TXT_SIZE, -0.3) )
if NR_WAGO_TOP <=0: text_upper = dummy_cutout

wp = cq.Workplane("ZY", (DIN_DEEP_LOW, -DIN_NARROW_HEIGHT/2-2.8, CASE_WIDTH/2) ).transformed(rotate = cq.Vector(0, 180, 0))
text_lower = wp
for i in range(0, NR_WAGO_BOTTOM) :
    text_lower = text_lower.union( wp.center( - (NR_WAGO_BOTTOM-1)*WAGO_OFFSET/2 + i*WAGO_OFFSET, 0).text(WAGO_LOWER_TEXT[i], WAGO_TXT_SIZE, -0.3) )
if NR_WAGO_BOTTOM <=0: text_upper = dummy_cutout



# ========================== lid =========================================

lid = ( cq.Workplane("XY", (0, 0, CASE_WIDTH)).placeSketch(sketch_inner.copy().wires().offset(1)).extrude(-CASE_THICKNESS)
    .cut(board1_cutout).cut(lid_ledcutout) )
for l in lid_screw_blocks: lid = lid.union(l, clean= True)
for (x, y,) in screw_positions: 
    lid = lid.moveTo(x, y).cboreHole(SCREW_HOLE_DIAM+0.4, SCREW_HEAD_DIAM, SCREW_HEAD_DEPTH, SCREW_HOLE_DEPTH) 
lid = ( lid.union(wago_lower_lid_addon).union(wago_upper_lid_addon)
           .cut(top_wago_fix_cutout).cut(bottom_wago_fix_cutout)
           .cut(wago_upper_cutout).cut(wago_lower_cutout) )

# =========================== build case ==================================


case = ( outer.cut(inner)
        .cut(clip_cutout)
        .union(wago_support_upper).union(wago_support_lower)
        .cut(wago_upper_cutout)
        .cut(wago_lower_cutout)
        .cut(text_brand).cut(text_name)
        .cut(text_upper).cut(text_lower)
        .cut(usb_lower_cutout).cut(usb_upper_cutout).cut(usb_front_cutout)
        .union(board2_carriers).union(board3_carriers)
        .union(board1_carrier)
        .cut(board1_cutout)
        .union(board1_ledcarrier)
        .union(board_fixes)
        .cut(case_ledcutout)
        .cut(led_txtcutout)
        .cut(lid)
    )
for b in case_screw_blocks: case = case.union(b)

case = case.cut(top_wago_fix_cutout).cut(bottom_wago_fix_cutout)


# ================================= Final packaging ======================




results = {
       "case": case,
       "top_wago_fix": top_wago_fix, #.moved(10),
       "bottom_wago_fix":bottom_wago_fix,
       "clip": clip, #.moved(20),
       "lid": lid,
     }

rotations = {
       "case": ((0, 0, 0), (0, 1, 0), 0),
       "top_wago_fix": ((0, 0, 0), (0, 1, 0), 90),
       "bottom_wago_fix": ((0, 0, 0), (0, 1, 0), 90),
       "clip": ((0, 0, 0), (0, 1, 0), -90),
       "lid": ((0, 0, 0), (0, 1, 0), 180),
    }

translations = {
       "case": ((0, 0, 0),),
       "top_wago_fix": ((0, 80, 0),),
       "bottom_wago_fix": ((0, 70, 0),),
       "clip": ((0, 60, 0),),
       "lid": ((0, 0, 0),),
    }

# arrange small parts for printing
clip_r = clip.rotate(*rotations["clip"])
tfix_r = top_wago_fix.rotate(*rotations["top_wago_fix"])
bfix_r = bottom_wago_fix.rotate(*rotations["bottom_wago_fix"])
clipz  = clip_r.val().BoundingBox().zmin
tfixz  = tfix_r.val().BoundingBox().zmin
bfixz  = bfix_r.val().BoundingBox().zmin
small_parts = ( cq.Assembly(clip_r.translate( (0, 40, -clipz)  ) )
        .add( tfix_r.translate(( 0, -20, -tfixz) ))
        .add( bfix_r.translate(( 0, 20, -bfixz) ))
        .add(screw_block_clip2)
        .add(screw_block_clip3)
    ).toCompound()




for i in results: 
    print(f"{i}: \n {results[i]} \n ")
    results[i].rotate(*rotations[i]).translate(*translations[i]).export(Path(os.path.basename(__file__)).stem+"_"+i+".stl")
small_parts.export(Path(os.path.basename(__file__)).stem+"_small_parts.stl")


show_object(case)
show_object(clip)
show_object(bottom_wago_fix)
show_object(top_wago_fix)
show_object(lid.translate((0, 0, 50 )))



result = (
    cq.Assembly(case)
        .add(bottom_wago_fix)
        .add(top_wago_fix)
        .add(lid)
        .add(clip)
    )


result.export(Path(os.path.basename(__file__)).stem+"_"+"assbly"+".step")

compound = result.toCompound()
compound.export(Path(os.path.basename(__file__)).stem+"_"+"compound"+".step")



