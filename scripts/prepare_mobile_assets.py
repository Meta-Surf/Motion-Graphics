"""Prepare reviewed Cloudflare assets. Black-background matte, not AI segmentation.

Requires Pillow. Preserves dark interior pixels inside closed silhouettes.
Visual alpha review is still required; an alpha channel alone does not prove quality.
"""
import argparse,json,shutil
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFilter,ImageOps

def prepare(base:Path,output:Path):
    source=base/'mobile-ai-layered-short-20261024'
    corrections=base/'mobile-ai-empty-backgrounds-20261024'
    output.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name in ['ai-core','cloud-node','privacy-shield']:
        im=Image.open(source/(name+'.jpg')).convert('RGB')
        r,g,b=im.split();lum=ImageChops.lighter(ImageChops.lighter(r,g),b)
        mask=lum.point(lambda v:255 if v>23 else 0).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
        padded=ImageOps.expand(mask,border=1,fill=0)
        ImageDraw.floodfill(padded,(0,0),128,thresh=0)
        mask=padded.point(lambda v:0 if v==128 else 255).crop((1,1,im.width+1,im.height+1))
        mask=mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.65))
        bbox=mask.point(lambda v:255 if v>1 else 0).getbbox()
        if bbox is None:raise ValueError('Empty silhouette for '+name)
        x0,y0,x1,y1=bbox;bbox=(max(0,x0-24),max(0,y0-24),min(im.width,x1+24),min(im.height,y1+24))
        im.putalpha(mask);im=im.crop(bbox);im.save(output/(name+'.png'))
        manifest.append({'file':name+'.png','source':name+'.jpg','operation':'threshold 23, close 7px, exterior flood fill, preserve interior, edge feather 0.65px','bbox':bbox,'alpha_channel_verified':True,'visual_review':'required'})
    for name in ['cafe-photo','mountain-photo','neural-wallpaper']:
        shutil.copy2(source/(name+'.jpg'),output/(name+'.jpg'))
    for name in ['studio-empty','city-empty']:
        shutil.copy2(corrections/(name+'.jpg'),output/(name+'.jpg'))
    (output/'treatment-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.base,a.output),ensure_ascii=False))
