"""Edit decision list for the POCO X8 unboxing (source times in seconds, speed 1.0 = real time).
Sections are joined with short transitions, clips inside a section with hard cuts."""
SRC_NAME = "Unboxing.mp4"
SECTIONS = [
  ("hook",   [("hook_reveal", 85.0, 87.0, 1.0, False)]),
  ("box",    [("box_intro", 0.0, 2.6, 1.0, False), ("box_cut", 9.0, 12.8, 1.0, False), ("box_tape_fast", 13.0, 30.0, 3.0, False),
              ("box_open", 35.5, 39.8, 1.0, False), ("box_pull", 41.0, 43.0, 1.0, False)]),
  ("poco",   [("poco_turn", 44.0, 49.5, 1.0, False), ("poco_seal_fast", 54.0, 68.5, 2.5, False)]),
  ("open",   [("open_lid", 76.0, 81.6, 1.0, False), ("reveal_a", 83.6, 84.6, 1.0, False), ("reveal_slow", 84.6, 86.6, 0.6, True)]),
  ("film",   [("wrapped", 92.2, 96.6, 1.0, False), ("peel", 100.0, 105.8, 1.0, False)]),
  ("power",  [("hands_front", 106.0, 107.6, 1.0, False), ("power_on", 114.0, 116.3, 1.0, False)]),
]
# transitions between sections (name, duration)
TRANS = [("fadeblack", .35), ("slideleft", .25), ("slideleft", .25), ("circleopen", .3), ("slideleft", .25)]
