
import numpy as np
import cv2
import os
import sys

def get_mask(template_with_alpha):
    h, w = template_with_alpha.shape[:2]
    # 分离alpha通道作为mask
    if template_with_alpha.shape[2] == 4:
        # 分割出alpha通道作为mask，并转换为二值图像
        mask = template_with_alpha[:, :, 3]
        mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]
        # 转换模板为灰度图像
    else:
        # 如果没有alpha通道，那么所有像素都是重要的
        mask = np.ones((h, w), dtype=np.uint8) * 255  # 全白即全部区域都是重要的
    return mask

def template_match(cropped_path, template_path, scales=np.arange(0.375, 2, 0.05)):
    cropped_img = cv2.imread(cropped_path, cv2.IMREAD_GRAYSCALE)
    s_list = scales.tolist()
    if 1.0 in s_list:
        pass
    else:
        s_list.insert(0, 1.0)
    scales = np.array(s_list)

    s = []
    if template_path == 'now.png':
        s = ['now.png']
    else:
        s = os.listdir(template_path)
        s = [os.path.join(template_path, filename) for filename in s]
    x1, y1, x2, y2 = -1, -1, -1, -1
    max_v, max_val = 0, 0
    for tem in s:
        print('本次模板', tem)
        cropped_img_height, cropped_img_width = cropped_img.shape[:2]
        template = cv2.imread(tem, cv2.IMREAD_UNCHANGED)
        template_rgb = cv2.imread(tem, cv2.IMREAD_GRAYSCALE)
        for scale in scales:
            if scale != 1.0:
                resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                resized_rgb = cv2.resize(template_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            else:
                resized_template = template
                resized_rgb = template_rgb
            # 计算mask不要灰度 匹配要灰度
            mask = get_mask(resized_template)
            template_height, template_width = resized_rgb.shape[:2]
            if template_width <= cropped_img_width and template_height <= cropped_img_height:
                # 修改模板图形为RGB
                # resized_template= cv2.cvtColor(resized_template, cv2.COLOR_BGR2RGB)
                # cv2.imwrite('x.png',cropped_img)
                # cv2.imwrite('y.png',resized_template)
                # res = cv2.matchTemplate(cropped_img, resized_template,cv2.TM_CCOEFF_NORMED,mask=mask)
                res = cv2.matchTemplate(cropped_img, resized_rgb, cv2.TM_CCOEFF_NORMED, mask=mask)
                aa, bb = np.isnan(res), np.isinf(res)
                res[np.isnan(res)] = 0
                res[np.isinf(res)] = 0
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                threshold = 0.95
                if max_val >= threshold and max_val != float('inf'):
                    if max_val > max_v:
                        max_v = max_val
                        x1, y1 = max_loc
                        x2 = x1 + template_width
                        y2 = y1 + template_height
                        print(max_val, x1, y1, x2, y2)
    if x1 == -1 and y2 == x1 and y2 == y1 and x2 == x1:
        return None
    return x1, y1, x2, y2  # 返回坐标字符串

if __name__== '__main__':
    print(template_match(sys.argv[1],sys.argv[2]))
