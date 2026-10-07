from pathlib import Path
import subprocess,re
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
QA=ROOT/'qa'/'review-closure';QA.mkdir(parents=True,exist_ok=True)
for name in ('main','supplement'):
    dest=QA/name;dest.mkdir(exist_ok=True)
    subprocess.run(['pdftoppm','-png','-scale-to','1500',str(ROOT/(name+'.pdf')),str(dest/'page')],check=True,capture_output=True)
    info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
    page_count=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
    pages=sorted((p for p in dest.glob('page-*.png') if int(p.stem.split('-')[-1])<=page_count),key=lambda p:int(p.stem.split('-')[-1]))
    assert len(pages)==page_count
    for start in range(0,len(pages),6):
        selected=pages[start:start+6]
        sheet=Image.new('RGB',(1800,2600),'#d8d8d8');draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(selected):
            im=Image.open(path).convert('RGB');im.thumbnail((870,1220))
            x=(j%2)*900+(900-im.width)//2;y=(j//2)*865+28
            # Fit each page to its actual 2x3 slot, preserving page shape.
            im.thumbnail((870,825));x=(j%2)*900+(900-im.width)//2
            sheet.paste(im,(x,y));draw.text((j%2*900+15,j//2*865+6),name+' page '+path.stem.split('-')[-1],fill='black')
        sheet.save(QA/(name+'-sheet-'+str(start//6+1)+'.png'))
    print(name+': '+str(len(pages))+' pages rendered')
