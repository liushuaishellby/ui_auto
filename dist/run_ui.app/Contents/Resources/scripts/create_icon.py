from PIL import Image, ImageDraw
import os
from math import sin, cos, pi

def create_gradient_color(y, height, start_color, end_color):
    """创建渐变色"""
    factor = y / height
    return tuple(int(start_color[i] + (end_color[i] - start_color[i]) * factor) for i in range(3))

def create_app_icon():
    # 创建一个更大的图像 1024x1024
    size = 1024
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 设置主题色彩
    primary_color = (24, 144, 255)    # 明亮的蓝色
    secondary_color = (47, 84, 235)   # 深蓝色
    accent_color = (250, 84, 28)      # 活力橙色
    highlight_color = (255, 255, 255)  # 白色高光
    
    # 绘制背景 - 使用更精细的渐变
    margin = 80  # 增加边距
    for y in range(size):
        for x in range(size):
            # 计算到中心的距离
            dx = x - size/2
            dy = y - size/2
            distance = (dx*dx + dy*dy) ** 0.5
            
            # 创建更平滑的径向渐变
            if distance < size/2:
                factor = distance / (size/2)
                # 添加非线性渐变使效果更自然
                factor = factor ** 1.2  # 稍微调整渐变曲线
                color = create_gradient_color(factor * 100, 100, primary_color, secondary_color)
                draw.point((x, y), fill=color + (255,))
    
    # 绘制主要图形 - 动态箭头环
    center = size // 2
    num_arrows = 3
    arrow_spacing = 360 / num_arrows
    
    for i in range(num_arrows):
        # 每个箭头的起始角度
        base_angle = i * arrow_spacing
        
        # 绘制弧形箭头
        points = []
        outer_radius = size * 0.35
        inner_radius = size * 0.25
        arc_length = 90  # 弧长度
        
        # 创建更平滑的弧形路径
        num_points = 80  # 增加点数使曲线更平滑
        for j in range(num_points):
            angle = base_angle + (arc_length * j / (num_points-1))
            angle_rad = angle * pi / 180
            
            # 外弧点
            x = center + outer_radius * cos(angle_rad)
            y = center + inner_radius * sin(angle_rad)
            points.append((x, y))
            
        # 添加箭头头部 - 优化箭头形状
        head_size = size * 0.15  # 稍微增大箭头
        final_angle_rad = (base_angle + arc_length) * pi / 180
        
        # 箭头尖端
        tip_x = center + (outer_radius + head_size/2) * cos(final_angle_rad)
        tip_y = center + (inner_radius + head_size/2) * sin(final_angle_rad)
        
        # 箭头底部两点
        base_x = center + outer_radius * cos(final_angle_rad)
        base_y = center + inner_radius * sin(final_angle_rad)
        
        # 添加箭头形状 - 使用更优化的箭头形状
        points.extend([
            (tip_x, tip_y),
            (base_x - head_size/2 * sin(final_angle_rad), 
             base_y + head_size/2 * cos(final_angle_rad)),
            (base_x + head_size/2 * sin(final_angle_rad),
             base_y - head_size/2 * cos(final_angle_rad))
        ])
        
        # 绘制箭头主体
        draw.polygon(points, fill=accent_color)
        
        # 添加增强的高光效果
        highlight_points = points[:-3]  # 不包括箭头头部
        draw.line(highlight_points, fill=highlight_color, width=6)  # 增加线宽
        
        # 添加箭头边缘高光
        edge_highlight = [(p[0], p[1]) for p in points]
        draw.line(edge_highlight + [edge_highlight[0]], fill=highlight_color, width=2)
    
    # 绘制更大的中心圆
    center_radius = size * 0.18
    draw.ellipse([center - center_radius, center - center_radius,
                  center + center_radius, center + center_radius],
                 fill=highlight_color)
    
    # 绘制内部小圆 - 添加渐变效果
    inner_radius = center_radius * 0.75
    for r in range(int(inner_radius), -1, -1):
        factor = r / inner_radius
        color = create_gradient_color(factor * 100, 100, primary_color, secondary_color)
        draw.ellipse([center - r, center - r, center + r, center + r],
                    fill=color + (255,))
    
    # 保存高质量图标
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons')
    os.makedirs(icon_dir, exist_ok=True)
    icon_path = os.path.join(icon_dir, 'app_icon.png')
    image.save(icon_path, 'PNG', quality=100, optimize=True)  # 使用最高质量设置
    print(f"图标已保存到: {icon_path}")

if __name__ == '__main__':
    create_app_icon() 