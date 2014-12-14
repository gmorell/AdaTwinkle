import argparse
from run_chaser import SimpleColorChaser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control a Nexturn Light Bulb (Yifang SH201)')
    subparsers = parser.add_subparsers()

    parse_twinkle = subparsers.add_parser('twinkle')
    parser.add_argument(
        "--device", type=str, help="Serial Port", action="store", dest="device", default="/dev/ttyACM0"
    )
    pt = parse_twinkle.add_subparsers(dest="command_twinkle")

    pt_rgb = pt.add_parser('rgb')

    pt_rgb.add_argument(
        '-r', '--redmin', type=int, help="Integer Value for Red Min value", action='store', dest="redmin", required=True
    )
    pt_rgb.add_argument(
        '-s', '--redmax', type=int, help="Integer Value for Red Max value", action='store', dest="redmax", required=True
    )
    pt_rgb.add_argument(
        '-g', '--greenmin', type=int, help="Integer Value for Green Min value", action='store', dest="greenmin", required=True
    )
    pt_rgb.add_argument(
        '-i', '--greenmax', type=int, help="Integer Value for Green Max value", action='store', dest="greenmax", required=True
    )
    pt_rgb.add_argument(
        '-b', '--bluemin', type=int, help="Integer Value for Blue Min value", action='store', dest="bluemin", required=True
    )
    pt_rgb.add_argument(
        '-a', '--bluemax', type=int, help="Integer Value for Blue Max value", action='store', dest="bluemax", required=True
    )
    pt_rgb.add_argument(
        '-f', '--fadetime', type=float, help="time between steps (seconds)", action='store', dest="fadetime", default=0.05
    )
    pt_rgb.add_argument(
        '-t', '--fadestep', type=int, help="step size", action='store', dest="stepsize", default=30
    )
    pt_rgb.add_argument(
        '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=900
    )
    pt_rgb.add_argument(
        '-c', '--count', type=int, help="LED Count", action='store', dest="count", required=True
    )
    ## python runner.py twinkle rgb --redmin 2 --redmax 3 --greenmin 5 --greenmax 6 --bluemin 7 --bluemax 8

    # pt_hue = pt.add_parser('hue')
    # pt_hue.add_argument(
    #     '-f', '--fadetime', type=float, help="time between steps (seconds)", action='store', dest="fadetime", default=0.05
    # )
    # pt_hue.add_argument(
    #     '-t', '--fadestep', type=int, help="step size", action='store', dest="stepsize", default=30
    # )
    # pt_hue.add_argument(
    #     '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=600
    # )

    parse_chaser = subparsers.add_parser('chase')
    pc = parse_chaser.add_subparsers(dest="command_chaser")

    pc_scc = pc.add_parser('scc', help="Simple Color Chaser")
    pc_scc.add_argument(
        '-c', '--count', type=int, help="LED Count", action='store', dest="count", required=True
    )
    pc_scc.add_argument(
        '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=900
    )
    pc_scc.add_argument(
        '-f', '--fadetime', type=float, help="time between steps (seconds)", action='store', dest="fadetime", default=0.05
    )
    pc_scc.add_argument(
        '-t', '--fadestep', type=int, help="step size", action='store', dest="stepsize", default=30
    )
    pc_scc.add_argument(
        '-i', '--hue', type=int, help="Chase Hue", action="store", dest="hue", required=True
    )
    pc_scc.add_argument(
        '-b', '--fadeby', type=int, help="Fade By X LEDs after leader", action="store", dest="hue", default=15
    )
    pc_scc.add_argument(
        '-s', '--spacing', type=int, help="Space between leaders", action="store", dest="hue", default=30
    )
    pc_scc.add_argument(
        '--saturation', type=int, help="Saturation", default=255
    )
    pc_scc.add_argument(
        '--value', type=int, help="Value", default=255
    )
    
    pc_sscc = pc.add_parser('sscc', help="Simple Shifting Color Chaser")
    pc_sscc.add_argument(
        '-c', '--count', type=int, help="LED Count", action='store', dest="count", required=True
    )
    pc_sscc.add_argument(
        '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=900
    )
    pc_sscc.add_argument(
        '-f', '--fadetime', type=float, help="time between steps (seconds)", action='store', dest="fadetime", default=0.05
    )
    pc_sscc.add_argument(
        '-t', '--fadestep', type=int, help="step size", action='store', dest="stepsize", default=30
    )
    pc_sscc.add_argument(
        '-i', '--hue', type=int, help="Chase Hue", action="store", dest="hue", required=True
    )
    pc_sscc.add_argument(
        '-b', '--fadeby', type=int, help="Fade By X LEDs after leader", action="store", dest="hue", default=15
    )
    pc_sscc.add_argument(
        '-s', '--spacing', type=int, help="Space between leaders", action="store", dest="hue", default=30
    )
    pc_sscc.add_argument(
        '--saturation', type=int, help="Saturation", default=255
    )
    pc_sscc.add_argument(
        '--value', type=int, help="Value", default=255
    )

    pc_rc = pc.add_parser('rc', help="Rainbow Chaser")
    pc_rc.add_argument(
        '-c', '--count', type=int, help="LED Count", action='store', dest="count", required=True
    )
    pc_rc.add_argument(
        '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=900
    )
    pc_rc.add_argument(
        '-f', '--fadetime', type=float, help="time between steps (seconds)", action='store', dest="fadetime", default=0.05
    )
    pc_rc.add_argument(
        '-t', '--fadestep', type=int, help="step size", action='store', dest="stepsize", default=30
    )
    pc_rc.add_argument(
        '--saturation', type=int, help="Saturation", default=255
    )
    pc_rc.add_argument(
        '--value', type=int, help="Value", default=255
    )
    
    pc_bc = pc.add_parser('bc', help="Bouncy Chaser")
    pc_bc.add_argument(
        '-c', '--count', type=int, help="LED Count", action='store', dest="count", required=True
    )
    pc_bc.add_argument(
        '-d', '--duration', type=int, help="Run duration (seconds)", action='store', dest="duration", default=900
    )
    pc_bc.add_argument(
        '-1', '--hue1', type=int, help="Min Hue", action='store', dest="hue1", default=240
    )
    pc_bc.add_argument(
        '-2', '--hue2', type=int, help="Max Hue", action='store', dest="hue2", default=120
    )
    pc_bc.add_argument(
        '--saturation', type=int, help="Saturation", default=255
    )
    pc_bc.add_argument(
        '--value', type=int, help="Value", default=255
    )
    arguments = parser.parse_args()
    argumentsdict = arguments.__dict__
    print argumentsdict
    # if argumentsdict.get('command_conf',None) in ['name_get', 'name_set']:
    #     SimpleColorChaser(**arguments)
    #
    # elif argumentsdict.get('command_hue', None) in ['color', 'minmax', 'random']:
    #     NexturnHSVController(arguments)
    #
    # elif argumentsdict.get('command_rgb', None) in ['color', 'random', 'bounce']:
    #     NexturnRGBController(arguments)
    #
    # else:
    #     raise Exception("Bad Args, No Class")