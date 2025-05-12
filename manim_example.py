from manim import *

class SquareToCircleExample(Scene):
    def construct(self):
        # 1. 显示标题
        title = Text("正方形到圆形的变换", font_size=42)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # 2. 创建正方形
        square = Square(side_length=2, color=BLUE)
        square.set_fill(BLUE_E, opacity=0.5)
        
        # 3. 添加正方形说明文字
        square_text = Text("正方形", font_size=24).next_to(square, DOWN)
        
        # 4. 显示正方形和文字
        self.play(FadeIn(square), Write(square_text))
        self.wait(1)
        
        # 5. 变换到圆形
        circle = Circle(radius=1, color=RED)
        circle.set_fill(RED_E, opacity=0.5)
        circle_text = Text("圆形", font_size=24).next_to(circle, DOWN)
        
        # 6. 执行变换动画
        self.play(
            ReplacementTransform(square, circle),
            ReplacementTransform(square_text, circle_text)
        )
        self.wait(1)
        
        # 7. 移动圆形到屏幕右侧
        self.play(circle.animate.shift(RIGHT * 3), circle_text.animate.shift(RIGHT * 3))
        self.wait(0.5)
        
        # 8. 创建新的正方形在左侧
        new_square = Square(side_length=2, color=GREEN)
        new_square.set_fill(GREEN_E, opacity=0.5)
        new_square.shift(LEFT * 3)
        new_square_text = Text("新正方形", font_size=24).next_to(new_square, DOWN)
        
        # 9. 显示新正方形
        self.play(FadeIn(new_square), Write(new_square_text))
        self.wait(1)
        
        # 10. 旋转两个形状
        self.play(
            Rotate(circle, angle=PI, about_point=circle.get_center()),
            Rotate(new_square, angle=PI, about_point=new_square.get_center())
        )
        self.wait(1)
        
        # 11. 将所有对象移动到中央并淡出
        self.play(
            circle.animate.move_to(ORIGIN),
            new_square.animate.move_to(ORIGIN),
            FadeOut(circle_text),
            FadeOut(new_square_text)
        )
        self.wait(0.5)
        
        # 12. 合并形状
        combined_shape = VGroup(circle, new_square)
        self.play(combined_shape.animate.scale(0.7).set_color(YELLOW))
        self.wait(1)
        
        # 13. 淡出并显示结束文字
        conclusion = Text("变换完成!", font_size=36, color=YELLOW)
        self.play(
            FadeOut(combined_shape),
            FadeOut(title),
            FadeIn(conclusion)
        )
        self.wait(2)
        self.play(FadeOut(conclusion)) 