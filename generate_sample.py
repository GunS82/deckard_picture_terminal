from PIL import Image, ImageDraw

def create_sample():
    # Create a new white image 800x600
    img = Image.new('RGB', (800, 600), color = 'white')
    d = ImageDraw.Draw(img)
    
    # Draw grid
    for x in range(0, 800, 50):
        d.line([(x, 0), (x, 600)], fill='lightgray', width=1)
    for y in range(0, 600, 50):
        d.line([(0, y), (800, y)], fill='lightgray', width=1)
    
    # Draw some shapes to test zoom/pan
    d.ellipse([350, 250, 450, 350], fill='red', outline='black')
    d.rectangle([100, 100, 200, 200], fill='blue', outline='black')
    d.rectangle([600, 400, 700, 500], fill='green', outline='black')
    
    # Draw a "crosshair" in the center
    d.line([(400, 0), (400, 600)], fill='black', width=2)
    d.line([(0, 300), (800, 300)], fill='black', width=2)
    
    img.save('sample.png')
    print("sample.png created")

if __name__ == "__main__":
    create_sample()
