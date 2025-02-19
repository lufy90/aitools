
import cairosvg
import os
import sys

def svg_to_png(src_dir, output_dir='./png', ):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.svg'):
                print(f'transfering {os.path.join(root,f)} ....')
                pname = root[len(src_dir):].replace('/','_')
                if not pname.endswith('_'):
                    pname = pname+'_'
                png_name = pname+f[:-3] + 'png'
                png_name = os.path.join(output_dir, png_name)
                try:
                    cairosvg.svg2png(url=os.path.join(root,f), write_to=png_name)
                    print(f'png saved to {png_name}')
                except Exception as e:
                    print(f'transfer failed cause of {str(e)}')


if __name__ == '__main__':
    svg_to_png(sys.argv[1], sys.argv[2])
