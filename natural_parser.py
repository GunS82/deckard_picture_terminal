import re

def parse_russian_command(text: str):
    text = text.lower().strip()
    
    # Коэффициенты для "наречий"
    power = 1.0
    if "чуть-чуть" in text or "немного" in text or "слегка" in text:
        power = 0.5
    elif "сильно" in text or "резко" in text or "максимум" in text:
        power = 2.5

    # 1. ZOOM (увеличить/уменьшить)
    if any(word in text for word in ["увелич", "приблиз", "zoom in", "больше"]):
        factor = 1.0 + (0.2 * power)
        return {"cmd": "zoom", "factor": round(factor, 2), "ms": 300}
    
    if any(word in text for word in ["уменьш", "отдали", "zoom out", "меньше"]):
        factor = 1.0 / (1.0 + (0.2 * power))
        return {"cmd": "zoom", "factor": round(factor, 2), "ms": 300}

    # 2. PAN (вправо/влево/вверх/вниз)
    dx, dy = 0, 0
    move_dist = 150 * power
    
    if "вправо" in text or "направо" in text:
        dx = move_dist
    elif "влево" in text or "налево" in text:
        dx = -move_dist
        
    if "вверх" in text or "подними" in text:
        dy = -move_dist
    elif "вниз" in text or "опусти" in text:
        dy = move_dist

    if dx != 0 or dy != 0:
        return {"cmd": "pan", "dx": dx, "dy": dy, "ms": 250}

    # 3. SHARPEN (резкость/улучшить)
    if any(word in text for word in ["резко", "улучш", "enhance", "четч"]):
        return {"cmd": "sharpen", "amount": 1.0 * power}

    # 4. RESET / FIT
    if "сброс" in text or "назад" in text or "оригинал" in text:
        return {"cmd": "reset_image"}
    
    if "целик" in text or "весь" in text or "вписать" in text:
        return {"cmd": "fit", "ms": 500}

    return None

if __name__ == "__main__":
    # Тесты
    test_phrases = [
        "увеличь чуть-чуть",
        "сильно вправо",
        "улучши резкость",
        "вниз и влево",
        "верни оригинал"
    ]
    for p in test_phrases:
        print(f"'{p}' -> {parse_russian_command(p)}")
