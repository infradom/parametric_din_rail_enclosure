# copyright @infradom
# ======================= component class declarations ========
        
        
# ======================================== PARAMETERS ======================================
from din_declarations import *


        
# ======================================== start of the more restricted part ==============================
# copyright @infradom
        
# ========================== import cadquery ===========================
        
import cadquery as cq
from cadquery.func import *
from pathlib import Path
import os




def generate_enclosure(c: Config):
    print(cq.__version__)
    global case, lid, clip, top_wago_fix, bottom_wago_fix

    # ============================ Sanity checks ===========================
        
        
    WAGO_POS_DEPTH_UPPER = c.board2.width+2*c.CASE_THICKNESS # from front of rail
    WAGO_POS_DEPTH_LOWER = c.board3.width+2*c.CASE_THICKNESS # from front of rail
        
        
    if ((c.NR_WAGO_BOTTOM*c.WAGO_OFFSET + c.CASE_THICKNESS > c.CASE_WIDTH) or 
        (c.NR_WAGO_TOP*c.WAGO_OFFSET + c.CASE_THICKNESS > c.CASE_WIDTH)):
        print(f"Warning: extending case width to support more WAGO's")
        c.CASE_WIDTH = max(c.NR_WAGO_BOTTOM, c.NR_WAGO_TOP)*c.WAGO_OFFSET + c.CASE_THICKNESS
            
    if (len(c.WAGO_UPPER_TEXT) < c.NR_WAGO_TOP) or (len(c.WAGO_LOWER_TEXT) < c.NR_WAGO_BOTTOM):
        print(f"Warning: please extend WAGO_UPPER_TEXT or WAGO_LOWER_TEXT lists")
    while len(c.WAGO_UPPER_TEXT) < c.NR_WAGO_TOP:    c.WAGO_UPPER_TEXT.append("U") # Undefined
    while len(c.WAGO_LOWER_TEXT) < c.NR_WAGO_BOTTOM: c.WAGO_LOWER_TEXT.append("U") # Undefined
    
    
    # ======================== dummy cutout (or union) object ==================
    # at a harmless place
    
    dummy_cutout = cq.Workplane("XY").box(0.1 , 0.1 , 0.1).translate((-0.1, c.DIN_HEIGHT/2 - 10, 5))
    
    # ======================== DIN rail clip ===================================
    
    CLIP_GAP   = 0.1
    CLIP_WIDTH = c.CASE_WIDTH - 2*c.CASE_THICKNESS - 2*CLIP_GAP
    CLIP_THICKNESS = 3.5
    CLIP_SLOT_DEPTH = CLIP_THICKNESS
    CLIP_HIDDEN_LENGTH = c.DIN_HEIGHT/2 - c.DIN_RAIL_LOWER + CLIP_SLOT_DEPTH
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
        .translate( (-(CLIP_THICKNESS + CLIP_GAP), -c.DIN_HEIGHT/2, c.CASE_WIDTH/2) )
    )
    
    
    CLIP_CUTOUT_HEIGHT = c.DIN_HEIGHT/2 - c.DIN_RAIL_LOWER
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
    clip_cutout = clip_cutout.translate((-CLIP_THICKNESS/2-CLIP_GAP, -CLIP_CUTOUT_HEIGHT/2 -c.DIN_RAIL_LOWER, c.CASE_WIDTH/2) )
    
    # ======================== wago fixation parts =================
    
    WAGO_FIX_HEIGHT = 2.5
    WAGO_FIX_EXTRUDE = 1.25
    def wago_fix(count, x, y, z):
        wago_221_fix    = cq.Workplane("front").box(c.CASE_WIDTH, c.WAGO_FIX_WIDTH, WAGO_FIX_HEIGHT).edges("#X").fillet(0.4)
        wago_fix_cutout = cq.Workplane("front").box(c.CASE_WIDTH +4, c.WAGO_FIX_WIDTH+0.1, WAGO_FIX_HEIGHT+0.1)
        wago_221_fix = wago_221_fix.center(-c.WAGO_OFFSET * (count - 1) / 2, 0).rect(4.0, 2.5).extrude(WAGO_FIX_EXTRUDE*2)
        for i in range(1, count): wago_221_fix = wago_221_fix.center(c.WAGO_OFFSET, 0).rect(4.0, 2.5).extrude(WAGO_FIX_EXTRUDE*2)
        wago_221_fix =    wago_221_fix.rotate((0, 0, 0), (0, 1, 0), -90).translate((x, y, z))
        wago_fix_cutout = wago_fix_cutout.rotate((0, 0, 0), (0, 1, 0), -90).translate((x, y, z))
        return wago_221_fix, wago_fix_cutout
    
    if c.NR_WAGO_BOTTOM > 0:
        bottom_wago_fix, bottom_wago_fix_cutout = wago_fix(c.NR_WAGO_BOTTOM,
            WAGO_POS_DEPTH_LOWER + c.WAGO_HEIGHT + WAGO_FIX_HEIGHT/2+WAGO_FIX_EXTRUDE - WAGO_FIX_EXTRUDE,
            -c.DIN_HEIGHT/2 + c.WAGO_LIP_LENGTH +c.WAGO_FIX_WIDTH/2 + c.CASE_THICKNESS,
            c.CASE_WIDTH/2 )
    else: bottom_wago_fix =  bottom_wago_fix_cutout = dummy_cutout
    if c.NR_WAGO_TOP > 0:
        top_wago_fix, top_wago_fix_cutout   = wago_fix(c.NR_WAGO_TOP,
            WAGO_POS_DEPTH_UPPER + c.WAGO_HEIGHT + WAGO_FIX_HEIGHT/2+WAGO_FIX_EXTRUDE - WAGO_FIX_EXTRUDE,
            c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.WAGO_FIX_WIDTH/2 - c.CASE_THICKNESS,
            c.CASE_WIDTH/2 )
    else: top_wago_fix = top_wago_fix_cutout = dummy_cutout
    
    # ====================== main case =========================
    
    sketch_outer = ( cq.Sketch()
        .segment( (0, c.DIN_RAIL_UPPER),(-0.8, c.DIN_RAIL_UPPER) )
        .segment( (-3.2, c.DIN_RAIL_UPPER - 3.2) )
        .segment( (-5, c.DIN_RAIL_UPPER - 3.2) )
        .segment( (-5, c.DIN_HEIGHT/2) )
        .segment( (c.board2.width+2*c.CASE_THICKNESS, c.DIN_HEIGHT/2))
        .segment( (c.board2.width+2*c.CASE_THICKNESS, c.DIN_HEIGHT/2-c.WAGO_LIP_LENGTH) )
        .segment( (c.DIN_DEEP_LOW, c.DIN_HEIGHT/2-c.WAGO_LIP_LENGTH) )
        .segment( (c.DIN_DEEP_LOW, c.DIN_NARROW_HEIGHT/2) )
        .segment( (c.DIN_DEEP_HIGH, c.DIN_NARROW_HEIGHT/2) )
        .segment( (c.DIN_DEEP_HIGH, -c.DIN_NARROW_HEIGHT/2) )
        .segment( (c.DIN_DEEP_LOW, -c.DIN_NARROW_HEIGHT/2) )
        .segment( (c.DIN_DEEP_LOW, -c.DIN_HEIGHT/2+c.WAGO_LIP_LENGTH) )
        .segment( (c.board3.width+2*c.CASE_THICKNESS,   -c.DIN_HEIGHT/2+c.WAGO_LIP_LENGTH) )
        .segment( (c.board3.width+2*c.CASE_THICKNESS,-c.DIN_HEIGHT/2))
        .segment( (-5, -c.DIN_HEIGHT/2) )
        .segment( (-5, -c.DIN_RAIL_LOWER) )
        .segment( (0, -c.DIN_RAIL_LOWER) )
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
        .segment( (c.CASE_THICKNESS, 0), (c.CASE_THICKNESS, c.DIN_HEIGHT/2 - c.CASE_THICKNESS) )
        .segment( (c.board2.width+c.CASE_THICKNESS, c.DIN_HEIGHT/2-c.CASE_THICKNESS))
        .segment( (c.board2.width+c.CASE_THICKNESS, c.DIN_HEIGHT/2-c.WAGO_LIP_LENGTH-c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_LOW-c.CASE_THICKNESS, c.DIN_HEIGHT/2-c.WAGO_LIP_LENGTH-c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_LOW - c.CASE_THICKNESS, c.DIN_HEIGHT/2 - c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_LOW - c.CASE_THICKNESS, c.DIN_NARROW_HEIGHT/2 - c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_HIGH -c.CASE_THICKNESS, c.DIN_NARROW_HEIGHT/2 - c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_HIGH -c.CASE_THICKNESS, -c.DIN_NARROW_HEIGHT/2 + c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_LOW - c.CASE_THICKNESS, -c.DIN_NARROW_HEIGHT/2 + c.CASE_THICKNESS) )
        .segment( (c.DIN_DEEP_LOW - c.CASE_THICKNESS, -c.DIN_HEIGHT/2+c.WAGO_LIP_LENGTH+c.CASE_THICKNESS) )
        .segment( (c.board3.width+c.CASE_THICKNESS, -c.DIN_HEIGHT/2+c.WAGO_LIP_LENGTH+c.CASE_THICKNESS) )
        .segment( (c.board3.width+c.CASE_THICKNESS,-c.DIN_HEIGHT/2+c.CASE_THICKNESS))
        .segment( ( c.CASE_THICKNESS, -c.DIN_HEIGHT/2 + c.CASE_THICKNESS) )
        .close()                
        .assemble(tag="innerface")
        .vertices()
        .fillet(0.6)
        .clean()
        )
    
    outer  = cq.Workplane("XY").placeSketch(sketch_outer).extrude(c.CASE_WIDTH)
    inner = cq.Workplane("XY",( 0.0, 0.0, c.CASE_WIDTH)).placeSketch(sketch_inner).extrude(-(c.CASE_WIDTH-c.CASE_THICKNESS))
    
    def case_screw_block(x, y):
        z = c.CASE_WIDTH-2*c.CASE_THICKNESS-c.SCREW_LID_EXTRA
        return ( cq.Workplane("XY").box(c.SCREW_BLOCK_SIZE, c.SCREW_BLOCK_SIZE, z).faces(">Z").cboreHole(c.SCREW_HOLE_DIAM, c.SCREW_INSERT_DIAM, c.SCREW_INSERT_DEPTH, c.SCREW_HOLE_DEPTH)
        .translate((x, y , z/2+c.CASE_THICKNESS))
        .edges("|Z").fillet(1) )
    
    def lid_screw_block(x, y):
        z = c.CASE_THICKNESS + c.SCREW_LID_EXTRA
        return ( cq.Workplane("XY").box(c.SCREW_BLOCK_SIZE, c.SCREW_BLOCK_SIZE, z)
        .translate((x, y , c.CASE_WIDTH - z/2))
        .edges("|Z").fillet(1) )
    
    def screw_block_clip(board, x, y):
        z = c.CASE_WIDTH-2*c.CASE_THICKNESS-c.SCREW_LID_EXTRA-board.mount_height-board.thickness-1.5
        b1 = box(c.SCREW_BLOCK_SIZE+2, c.SCREW_BLOCK_SIZE+2, z)
        b2 = box(c.SCREW_BLOCK_SIZE, c.SCREW_BLOCK_SIZE,  z*2 + 2)
        return ( b1.cut(b2).translate((x , y, 0)) )  
    
    def board_fix(board, centerX, centerY, rotate = False): # for horizontal boards only
        rad = 1
        th = 1.3
        w = c.BOARD_FIX_WIDTH
        if rotate: w = -w
        fix =  ( cq.Workplane("ZY", (centerX+c.BOARD_FIX_WIDTH/2, centerY, c.CASE_THICKNESS))
        .hLine(board.mount_height+board.thickness)
        .threePointArc( (board.mount_height+board.thickness+rad, rad), (board.mount_height+board.thickness+2*rad, 0) )
        .vLine(-th).hLine(-board.mount_height-board.thickness-2*rad).vLine(th).close()
        .extrude(w)
        #.edges("|X").
        #.fillet(0.3)
        )
        if rotate: fix = fix.rotate((centerX+c.BOARD_FIX_WIDTH/2, centerY, 0), (centerX+c.BOARD_FIX_WIDTH/2, centerY, 1), 180)
        return fix
    
    board_fixes = ( board_fix(c.board2, c.board2.width + c.CASE_THICKNESS -3-c.board2.jst_extrawidth_right,  c.DIN_HEIGHT/2-c.CASE_THICKNESS-c.board2.length, False)
                    .union(board_fix(c.board2, c.CASE_THICKNESS +3+c.board2.jst_extrawidth_left,  c.DIN_HEIGHT/2-c.CASE_THICKNESS-c.board2.length, False))
                    .union(board_fix(c.board3, c.board3.width + c.CASE_THICKNESS -3+c.board3.jst_extrawidth_right, -c.DIN_HEIGHT/2+c.CASE_THICKNESS+c.board3.length, True))
                    .union(board_fix(c.board3, c.CASE_THICKNESS +3+c.board3.jst_extrawidth_left, -c.DIN_HEIGHT/2+c.CASE_THICKNESS+c.board3.length, True))
                  )
    
    wago_support_upper = ( cq.Workplane("XY").box(c.CASE_THICKNESS, c.WAGO_LENGTH, c.CASE_WIDTH-2*c.CASE_THICKNESS)
        .translate((WAGO_POS_DEPTH_UPPER - c.CASE_THICKNESS/2, c.DIN_HEIGHT/2-c.WAGO_LENGTH/2 , c.CASE_WIDTH/2)) )
    wago_support_lower = ( cq.Workplane("XY").box(c.CASE_THICKNESS, c.WAGO_LENGTH, c.CASE_WIDTH-2*c.CASE_THICKNESS)
        .translate((WAGO_POS_DEPTH_LOWER - c.CASE_THICKNESS/2, -c.DIN_HEIGHT/2+c.WAGO_LENGTH/2 , c.CASE_WIDTH/2)) )
    
    if c.NR_WAGO_TOP == 0: wago_height_t = 0 
    else: wago_height_t = c.WAGO_HEIGHT + WAGO_FIX_HEIGHT
    if c.NR_WAGO_BOTTOM == 0: wago_height_b = 0 
    else: wago_height_b = c.WAGO_HEIGHT + WAGO_FIX_HEIGHT
    screw_positions = [ 
               (WAGO_POS_DEPTH_UPPER + wago_height_t + c.SCREW_BLOCK_SIZE/2,  c.DIN_HEIGHT/2-c.WAGO_LIP_LENGTH - c.CASE_THICKNESS - c.SCREW_BLOCK_SIZE/2, ),
               (WAGO_POS_DEPTH_LOWER + wago_height_b + c.SCREW_BLOCK_SIZE/2, -c.DIN_HEIGHT/2+c.WAGO_LIP_LENGTH + c.CASE_THICKNESS + c.SCREW_BLOCK_SIZE/2, ),
               (c.board2.width/2 + c.CASE_THICKNESS, c.DIN_HEIGHT/2-c.CASE_THICKNESS-c.board2.length - c.SCREW_BLOCK_SIZE/2, ),
               (c.board3.width/2 + c.CASE_THICKNESS, -c.DIN_HEIGHT/2+c.CASE_THICKNESS+c.board3.length + c.SCREW_BLOCK_SIZE/2,),
        ]
    
    case_screw_blocks = []
    lid_screw_blocks  = []
    for (x, y,) in screw_positions: case_screw_blocks.append(case_screw_block(x, y))
    for (x, y,) in screw_positions: lid_screw_blocks.append(lid_screw_block(x, y))
    
    screw_block_clip2 = screw_block_clip(c.board2, 0, -20)
    screw_block_clip3 = screw_block_clip(c.board3, 0, -30)
    
    
    
    if c.NR_WAGO_TOP > 0:
        wago_upper_cutout = cq.Workplane("XY", (WAGO_POS_DEPTH_UPPER + c.WAGO_HEIGHT/2, c.DIN_HEIGHT/2-c.WAGO_LENGTH/2 , c.CASE_WIDTH/2)).box(c.WAGO_HEIGHT, c.WAGO_LENGTH, c.WAGO_OFFSET*c.NR_WAGO_TOP)
        wago_upper_lid_addon = cq.Workplane("XY", (WAGO_POS_DEPTH_UPPER + c.WAGO_HEIGHT/2, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.CASE_THICKNESS/2 , c.CASE_WIDTH/2 + 0*c.CASE_THICKNESS + c.NR_WAGO_TOP*c.WAGO_OFFSET/2)).box(c.WAGO_HEIGHT, c.CASE_THICKNESS, c.CASE_WIDTH - c.NR_WAGO_TOP*c.WAGO_OFFSET)
    else: 
        wago_upper_cutout = dummy_cutout
        wago_upper_lid_addon = dummy_cutout
    if c.NR_WAGO_BOTTOM > 0:
        wago_lower_cutout = cq.Workplane("XY", (WAGO_POS_DEPTH_LOWER + c.WAGO_HEIGHT/2, -c.DIN_HEIGHT/2+c.WAGO_LENGTH/2 , c.CASE_WIDTH/2)).box(c.WAGO_HEIGHT, c.WAGO_LENGTH, c.WAGO_OFFSET*c.NR_WAGO_BOTTOM)
        wago_lower_lid_addon = cq.Workplane("XY", (WAGO_POS_DEPTH_LOWER + c.WAGO_HEIGHT/2, -c.DIN_HEIGHT/2 + c.WAGO_LIP_LENGTH + c.CASE_THICKNESS/2 , c.CASE_WIDTH/2 + 0*c.CASE_THICKNESS + c.NR_WAGO_BOTTOM*c.WAGO_OFFSET/2)).box(c.WAGO_HEIGHT, c.CASE_THICKNESS, c.CASE_WIDTH - c.NR_WAGO_BOTTOM*c.WAGO_OFFSET)
    else: 
        wago_lower_cutout = dummy_cutout
        wago_lower_lid_addon = dummy_cutout
    
    b1_carrier_height = c.CASE_WIDTH - c.board1.width - c.CASE_THICKNESS
    if b1_carrier_height>0:
        board1_carrier = cq.Workplane("XY", (c.DIN_DEEP_HIGH-c.board1.mount_height, c.DIN_HEIGHT/2 -c.WAGO_LIP_LENGTH -c.board1.length/2 -c.CASE_THICKNESS/2, c.CASE_THICKNESS + b1_carrier_height/2)).box(c.board1.thickness+3, c.board1.length + c.CASE_THICKNESS, b1_carrier_height)
    else: board1_carrier = dummy_cutout
    
    board1_carrier = board1_carrier.union(cq.Workplane("XY", (c.DIN_DEEP_HIGH-c.board1.mount_height + c.board1.thickness/2 , c.DIN_HEIGHT/2 -c.WAGO_LIP_LENGTH -c.board1.length-c.CASE_THICKNESS/2 -0, c.CASE_WIDTH/2+b1_carrier_height/2)).box(c.CASE_THICKNESS+2, c.CASE_THICKNESS, c.board1.width-c.CASE_THICKNESS/2))
    board1_cutout = cq.Workplane("XY", (c.DIN_DEEP_HIGH-c.board1.mount_height,c.DIN_HEIGHT/2 -c.WAGO_LIP_LENGTH -c.board1.length/2 -c.CASE_THICKNESS/2, c.CASE_WIDTH/2+b1_carrier_height/2)).box(c.board1.thickness, c.board1.length, c.board1.width)
    
    def usb_cutout(workplane, x, y, z, extrude):
        return ( cq.Workplane(workplane, (x, y, z))
            .moveTo(0, c.USB_HEIGHT/2)
            .hLine(c.USB_WIDTH/2 -c.USB_HEIGHT/2)
            .threePointArc((c.USB_WIDTH/2, 0),  ( c.USB_WIDTH/2 - c.USB_HEIGHT/2, -c.USB_HEIGHT/2))
            .hLine(-c.USB_WIDTH + c.USB_HEIGHT)
            .threePointArc((-c.USB_WIDTH/2, 0), (-c.USB_WIDTH/2 + c.USB_HEIGHT/2, +c.USB_HEIGHT/2))
            .hLine(c.USB_WIDTH/2 - c.USB_HEIGHT/2)
            .close()
            .extrude(extrude, taper = -30) )
    
    
    if c.board1.usb_height is None: usb_front_cutout = dummy_cutout
    else: usb_front_cutout = usb_cutout("ZX", c.DIN_DEEP_HIGH + c.board1.usb_height + c.board1.thickness/2 - c.board1.mount_height, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH, c.CASE_WIDTH/2+b1_carrier_height/2 - c.board1.usb_offset, -c.CASE_THICKNESS)
    if c.board2.usb_height is None: usb_upper_cutout = dummy_cutout
    else: usb_upper_cutout = usb_cutout("XZ", c.CASE_THICKNESS+c.board2.width/2+c.board2.usb_offset,  c.DIN_HEIGHT/2, c.CASE_THICKNESS+c.board2.usb_height+c.board2.mount_height+c.board2.thickness/2, c.CASE_THICKNESS )
    if c.board3.usb_height is None: usb_lower_cutout = dummy_cutout
    else: usb_lower_cutout = usb_cutout("XZ",c.CASE_THICKNESS+c.board3.width/2+c.board3.usb_offset, -c.DIN_HEIGHT/2, c.CASE_THICKNESS+c.board3.usb_height+c.board3.mount_height+c.board3.thickness/2, -c.CASE_THICKNESS)
    
    
    
    CARRIER_X = 7
    CARRIER_Y = 2
    board2_carriers =  ( cq.Workplane("XY", (0, -c.CASE_THICKNESS, c.CASE_THICKNESS))
            .pushPoints([ (c.CASE_THICKNESS + c.board2.width/2 + c.board2.usb_offset, c.DIN_HEIGHT/2 -CARRIER_Y/2),
                          (c.CASE_THICKNESS + c.board2.width/2, c.DIN_HEIGHT/2 -c.board2.length+CARRIER_Y/2) ])
            .rect(CARRIER_X, CARRIER_Y)
            .extrude(c.board2.mount_height) )
    board3_carriers = ( cq.Workplane("XY", (0, +c.CASE_THICKNESS, c.CASE_THICKNESS))
            .pushPoints( [(c.CASE_THICKNESS + c.board3.width/2 + c.board3.usb_offset, -c.DIN_HEIGHT/2 + CARRIER_Y/2 ),
                       (c.CASE_THICKNESS + c.board3.width/2, -c.DIN_HEIGHT/2 +c.board3.length -CARRIER_Y/2) ])
            .rect(CARRIER_X, CARRIER_Y)
            .extrude(c.board3.mount_height) )
    
    def ledcarrier(board):
        if board.position == "front": # currently only supported case
            carrier = cq.Workplane("ZY", (c.DIN_DEEP_HIGH, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.CASE_THICKNESS/2 - board.length, c.CASE_WIDTH - c.CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
            for led in board.leds:
                #c1 = carrier.moveTo((c.CASE_WIDTH-c.CASE_THICKNESS)/2, led.y).rect(c.CASE_WIDTH-2*c.CASE_THICKNESS, c.LIGHT_CARRIER_DIAM).extrude(-board.mount_height +4) 
                cr = carrier.moveTo(led.x, led.y).rect(c.LIGHT_CARRIER_DIAM, c.LIGHT_CARRIER_DIAM).extrude(-board.mount_height + board.thickness/2+0.4) # 0.4: dont touch the led'
                carrier = carrier.union(cr)
            return carrier
    
    
    def ledcutout(board):
        if board.position == "front": # currently only supported case
            carrier = cq.Workplane("ZY", (c.DIN_DEEP_HIGH, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.CASE_THICKNESS/2 - board.length, c.CASE_WIDTH - c.CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
            lidwp   = cq.Workplane("ZY", (c.DIN_DEEP_HIGH, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.CASE_THICKNESS/2 - board.length, c.CASE_WIDTH - c.CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
            txtwp   = cq.Workplane("ZY", (c.DIN_DEEP_HIGH, c.DIN_HEIGHT/2 - c.WAGO_LIP_LENGTH - c.CASE_THICKNESS/2 - board.length, c.CASE_WIDTH - c.CASE_THICKNESS/2,)).transformed(rotate = cq.Vector(0, 180, 0))
            txt = txtwp.union(dummy_cutout)
            lid = lidwp
            for led in board.leds:
                cr  = carrier.moveTo(led.x, led.y).circle(c.LIGHT_GUIDE_DIAMETER/2).extrude(-board.mount_height + 0.2)
                cl = carrier.moveTo(led.x, led.y).rect(c.LIGHT_CARRIER_DIAM+0.1, c.LIGHT_CARRIER_DIAM+0.25 ).extrude(-board.mount_height -0.2 )
                carrier = carrier.union(cr)
                lid     = lid.union(cl)
                if led.txt: txt     = txt.union(txtwp.center(led.x, led.y+2.7).text(led.txt, 2.7, -0.3))
            return (carrier, lid, txt) #carrier.union(txt)
    
    board1_ledcarrier = ledcarrier(c.board1)
    (case_ledcutout, lid_ledcutout, led_txtcutout)  = ledcutout(c.board1)
    
    # ========================== case text ======================================
    
    text_brand  = cq.Workplane("YX").center(0,12).text(c.BRAND, 8, -0.3)
    if c.MODULE_NAME: text_name = cq.Workplane("YZ", (c.DIN_DEEP_HIGH, -c.DIN_NARROW_HEIGHT/2+2.5, 5)).text(c.MODULE_NAME, 6, -0.3, kind="bold", halign="left")
    else: text_name = dummy_cutout
    
    #text_upper = case.faces("<X[2]").workplane().transformed(rotate=(0, 0, -90))
    
    wp = cq.Workplane("ZY", (c.DIN_DEEP_LOW, c.DIN_NARROW_HEIGHT/2+2.6, c.CASE_WIDTH/2) ).transformed(rotate = cq.Vector(0, 180, 0))
    text_upper = wp
    for i in range(0, c.NR_WAGO_TOP) :
        text_upper = text_upper.union( wp.center( - (c.NR_WAGO_TOP-1)*c.WAGO_OFFSET/2 + i*c.WAGO_OFFSET, 0).text(c.WAGO_UPPER_TEXT[i], c.WAGO_TXT_SIZE, -0.3) )
    if c.NR_WAGO_TOP <=0: text_upper = dummy_cutout
    
    wp = cq.Workplane("ZY", (c.DIN_DEEP_LOW, -c.DIN_NARROW_HEIGHT/2-2.8, c.CASE_WIDTH/2) ).transformed(rotate = cq.Vector(0, 180, 0))
    text_lower = wp
    for i in range(0, c.NR_WAGO_BOTTOM) :
        text_lower = text_lower.union( wp.center( - (c.NR_WAGO_BOTTOM-1)*c.WAGO_OFFSET/2 + i*c.WAGO_OFFSET, 0).text(c.WAGO_LOWER_TEXT[i], c.WAGO_TXT_SIZE, -0.3) )
    if c.NR_WAGO_BOTTOM <=0: text_lower = dummy_cutout
    
    
    
    # ========================== lid =========================================
    
    lid = ( cq.Workplane("XY", (0, 0, c.CASE_WIDTH)).placeSketch(sketch_inner.copy().wires().offset(1)).extrude(-c.CASE_THICKNESS)
        .cut(board1_cutout).cut(lid_ledcutout) )
    for l in lid_screw_blocks: lid = lid.union(l, clean= True)
    for (x, y,) in screw_positions: 
        lid = lid.moveTo(x, y).cboreHole(c.SCREW_HOLE_DIAM+0.4, c.SCREW_HEAD_DIAM, c.SCREW_HEAD_DEPTH, c.SCREW_HOLE_DEPTH) 
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
        results[i].rotate(*rotations[i]).translate(*translations[i]).export(Path(os.path.basename(__file__)).stem+"_"+c.CONFIG_NAME+"_"+i+".stl")
    small_parts.export(Path(os.path.basename(__file__)).stem+"_"+c.CONFIG_NAME+"_small_parts.stl")
    
    
    
    result = (
        cq.Assembly(case)
            .add(bottom_wago_fix)
            .add(top_wago_fix)
            .add(lid)
            .add(clip)
        )
    
    
    result.export(Path(os.path.basename(__file__)).stem+"_"+c.CONFIG_NAME+"_"+"assbly"+".step")
    
    compound = result.toCompound()
    compound.export(Path(os.path.basename(__file__)).stem+"_"+c.CONFIG_NAME+"_"+"compound"+".step")
    
def show():
    show_object(case)
    show_object(clip)
    show_object(bottom_wago_fix)
    show_object(top_wago_fix)
    show_object(lid.translate((0, 0, 50 )))
    
    
    
    