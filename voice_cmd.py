import sys
from natural_parser import parse_russian_command
from photoctl import send

def main():
    if len(sys.argv) > 1:
        # Если команда передана аргументами
        phrase = " ".join(sys.argv[1:])
        cmd = parse_russian_command(phrase)
        if cmd:
            print(f"Executing: {cmd}")
            send(cmd)
        else:
            print("Unknown command phrase.")
    else:
        # Интерактивный режим
        print("Blade Runner 'ENHANCE' Voice Interface Emulator")
        print("Enter commands in Russian (e.g., 'увеличь чуть-чуть', 'влево сильно', 'сброс')")
        print("Type 'exit' to quit.")
        
        while True:
            try:
                phrase = input("\n> ")
                if phrase.lower() in ["exit", "quit", "выход"]:
                    break
                
                cmd = parse_russian_command(phrase)
                if cmd:
                    send(cmd)
                    print(f"Sent: {cmd}")
                else:
                    print("Could not parse that. Try: 'увеличь', 'вправо', 'резкость', 'сброс'")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()

