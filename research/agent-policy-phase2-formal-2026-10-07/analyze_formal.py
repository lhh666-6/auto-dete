import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from run_formal import verify_freeze
from phase2.export import export_tables
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--results',type=Path,default=ROOT/'formal-results')
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--figures',action='store_true');args=parser.parse_args()
    verify_freeze();result=export_tables(ROOT/'frozen-formal',args.results,args.output)
    print('planned_arms='+str(result['planned_arms'])+', formal_inference_allowed='+str(result['formal_inference_allowed']))

    if args.figures:
        from phase2.figures import draw
        draw(args.output)
