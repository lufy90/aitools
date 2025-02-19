import random
import os
from PIL import Image,UnidentifiedImageError
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io
import numpy as np
import json

def merge_img(bg_path, fg_paths, output, scale=1, max_offset=3, allowed_position=None, resolution=(1920,1080)):
    '''
    max_offset: max offset allowed (pixels)
    allowed_position: allowed position
    '''

    ## prepare background image
    bg = Image.open(bg_path)
    bg.convert('RGBA')
    bg = bg.resize(resolution)
    w,h = bg.size

    if not allowed_position:
        allowed_position = (0, 0, w, h)

    if os.path.exists(output):
        raise Exception(f'file exists: {output}')

    annotations = []

    ## prepare foreground image
    token_areas = []
    print(f'using {bg_path} as background')
    for fg_path in fg_paths:
        try:
            fg = Image.open(fg_path)
        except UnidentifiedImageError:
            drawing = svg2rlg(fg_path)
            png_data = renderPM.drawToString(drawing, fmt="PNG")
            fg = Image.open(io.BytesIO(png_data)).convert("RGBA")
        fg = fg.resize((round(x*scale) for x in fg.size))

        fg_w,fg_h = fg.size

        excepted_positions = []
        for pos in token_areas:
            a,b,c,d = pos
            p = (a-fg_w if a-fg_w >0 else 0,b-fg_h if b-fg_h>0 else 0,c,d)
            excepted_positions.append(p)

        pos = get_random_position(fg.size, allowed_position, excepted_positions=excepted_positions)
        fg_x,fg_y = pos
        fg_w,fg_h = fg.size
        token_areas.append((fg_x,fg_y,fg_x+fg_w,fg_y+fg_h))
        print(f'using {fg_path} as icon at position {pos}')
        bg.paste(fg, pos)
        base_name = os.path.basename(fg_path)
        label_name ='.'.join(base_name.split('_')[-1].split('.')[:-1])
        loc = [*pos, fg_w, fg_h]
        location = [int(x) for x in loc]
        annotations.append({"name":label_name,"location":location,"resolution":list(resolution)})

    bg.save(output)
    return annotations

def get_matrix(box):
    x0,y0,x1,y1 = box
    x = np.arange(x0,x1)
    y = np.arange(y0,y1)
    xx, yy = np.meshgrid(x,y)
    return np.column_stack([xx.ravel(), yy.ravel()])

def get_exclude(arr1, arr2):
    #mask = ~np.isin(arr1.view([('', arr1.dtype)] * arr1.shape[1]), arr2.view([('', arr2.dtype)] * arr2.shape[1]))
    #mask = np.all((~(arr1[:, None] == arr2)).all(axis=2), axis=1)
    #t1 = [tuple(row) for row in arr1]
    #t2 = [tuple(row) for row in arr2]
    #mask = ~np.isin(t1,t2)
    #t1 = map(tuple, arr1)
    #t2 = map(tuple, arr2)
    #mask = ~np.isin(t1,t2)
    #mask = ~np.isin(arr1.view([('', arr1.dtype)] * arr1.shape[1]), arr2.view([('', arr2.dtype)] * arr2.shape[1]))
    #mask = np.all(~np.isin(arr1, arr2), axis=1)
    #v1= arr1.view([('', arr1.dtype)] * arr1.shape[1])
    #v2= arr2.view([('', arr2.dtype)] * arr2.shape[1])
    #mask = ~np.isin(v1, v2)
    rows_to_delete = set(map(tuple, arr2))
    mask = [tuple(row) not in rows_to_delete for row in arr1]
    return arr1[mask]

def get_random_position(size, allowed_position, excepted_positions=[], gap=2):
    # size: (w,h)
    # allowed_position: (x0,y0,x1,y1)
    # excepted_positions: [(x00,y00,x10,y10),(x01,y01,x11,y11),...]
    #print('exclude areas:', excepted_positions)
    #print('size:',size)
    #print('allowed_position:',allowed_position)

    w,h = size
    x0,y0,x1,y1 = allowed_position
    # exclude left and bottom edge:
    inner_exclude_areas = [*excepted_positions]
    inner_exclude_areas.append((x1-w,0,x1,y1))
    inner_exclude_areas.append((0,y1-h,x1,y1))
    allowed_matrix = get_matrix(allowed_position)
    for pos in inner_exclude_areas:
        x0,y0,x1,y1 = pos
        #x_0 = x0-w-gap if x0-w-gap >0 else 0
        #y_0 = y0 - h - gap if y0 - h - gap >0 else 0
        #except_matrix = get_matrix((x_0, y_0, x1+gap, y1+gap))
        except_matrix = get_matrix(pos)
        allowed_matrix = get_exclude(allowed_matrix, except_matrix)

    #for i in allowed_matrix:
    #    if i in except_matrix:
    #        continue
    #    else:
    #        result.append(i)
    length = allowed_matrix.shape[0]
    return tuple(allowed_matrix[random.randint(0, length)])


def get_random_file(path, allowed_suffix=['png','jpeg','jpg'], maxcount=100000):
    count = 0
    output = random.randint(1, maxcount)
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] in allowed_suffix:
                count = count + 1
                if count == output:
                    return os.path.join(root, f)
    if count == 0:
        raise Exception(f'No file found in {path} with specific suffix')
    return get_random_file(path, allowed_suffix=allowed_suffix, maxcount=count)

def gen_dataset(bg_dir, fg_dir, output_dir='./output', count=10, max_labels=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(count):
        print(f'generating ....... {i}')
        bg_path = get_random_file(bg_dir)
        fg_paths = []
        for j in range(random.randint(1,max_labels)):
            fg_path = get_random_file(fg_dir)
            fg_paths.append(fg_path)
        try:
            merge_img(bg_path, fg_paths, os.path.join(output_dir, f'{i}.jpg'))
        except Exception as e:
            print('Generate failed cause of ${str(e)}')

def gen_yolo_dataset(bg_dir, fg_dir, dataset_dir='./yolo_dataset', count=10,max_labels=3, resolution=(1920,1080)):
    img_dir = os.path.join(dataset_dir, 'images')
    label_dir = os.path.join(dataset_dir, 'labels')
    annotation_dir = os.path.join(dataset_dir, 'annotations')
    class_file = os.path.join(dataset_dir, 'classes.txt')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)
    if not os.path.exists(annotation_dir):
        os.makedirs(annotation_dir)
    for i in range(count):
        bg_path = get_random_file(bg_dir)
        fg_paths = []
        print(f'generating ................................... {i}')
        for j in range(random.randint(1,max_labels)):
            fg_path = get_random_file(fg_dir)
            fg_paths.append(fg_path)
        try:
            annotations = merge_img(bg_path, fg_paths, os.path.join(img_dir, f'{i}.jpg'), resolution=resolution)
            with open(os.path.join(annotation_dir, f'{i}.json'), 'w') as f:
                json.dump(annotations, f)
            yolo_str = ''
            for annotation in annotations:
                class_id = get_class_id(annotation['name'], class_file=class_file)
                if class_id is None:
                    with open(class_file, 'a') as f:
                        f.write(f'{annotation["name"]}\n')
                    class_id = get_class_id(annotation['name'], class_file=class_file)
                yolo_data = bbox_to_yolo(annotation['location'],resolution)
                yolo_str = yolo_str + f'{class_id} {yolo_data[0]} {yolo_data[1]} {yolo_data[2]} {yolo_data[3]}\n'
            with open(os.path.join(label_dir, f'{i}.txt'), 'w') as f:
                f.write(yolo_str)
        except Exception as e:
            print(f'generate {i} failed: Exception: {str(e)}')
        print(f'generated yolo data in {dataset_dir}\n')


def get_class_id(class_name, class_file="classes.txt"):
    if not os.path.exists(class_file):
        return None
    with open(class_file,'r') as f:
        for number, line in enumerate(f,start=0):
            if class_name == line.strip():
                return number
    return None

def bbox_to_yolo(bbox,resolution):
    x_center = (bbox[0] + (bbox[2] / 2 ))/ resolution[0]
    y_center = (bbox[1] + bbox[3] /2 ) / resolution[1]
    width = bbox[2]/resolution[0]
    height = bbox[3]/ resolution[1]
    return (x_center,y_center,width,height)


if __name__ == '__main__':
    import sys
    #gen_dataset('/usr/share/wallpapers', './png', count=100)
    #gen_yolo_dataset('/usr/share/wallpapers', './v20_bloom_48',dataset_dir='./yolo_v20_bloom_48_dataset', count=5000)
    fg_dir = sys.argv[1]
    count = int(sys.argv[2])
    ds_dir = fg_dir + f"_dataset_{count}"
    gen_yolo_dataset('/usr/share/wallpapers', fg_dir, dataset_dir=ds_dir, count=count)
