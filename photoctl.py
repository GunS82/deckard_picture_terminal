import json
import socket
import sys


def send(obj: dict, host="127.0.0.1", port=8765):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=1.0) as s:
        s.sendall(data)


def main(argv):
    if len(argv) < 2:
        print("Usage:")
        print("  python photoctl.py zoom <factor> [ms]")
        print("  python photoctl.py pan <dx> <dy> [ms]")
        print("  python photoctl.py fit [ms]")
        print("  python photoctl.py sharpen <amount>")
        print("  python photoctl.py crop [out.png]")
        print("  python photoctl.py reset_image")
        return 1

    cmd = argv[1]

    if cmd == "zoom":
        factor = float(argv[2])
        ms = int(argv[3]) if len(argv) > 3 else 250
        send({"cmd": "zoom", "factor": factor, "ms": ms})

    elif cmd == "pan":
        dx = float(argv[2])
        dy = float(argv[3])
        ms = int(argv[4]) if len(argv) > 4 else 250
        send({"cmd": "pan", "dx": dx, "dy": dy, "ms": ms})

    elif cmd == "fit":
        ms = int(argv[2]) if len(argv) > 2 else 300
        send({"cmd": "fit", "ms": ms})

    elif cmd == "sharpen":
        amount = float(argv[2]) if len(argv) > 2 else 1.0
        send({"cmd": "sharpen", "amount": amount})

    elif cmd == "crop":
        out = argv[2] if len(argv) > 2 else None
        payload = {"cmd": "crop_view"}
        if out:
            payload["out"] = out
        send(payload)

    elif cmd == "reset_image":
        send({"cmd": "reset_image"})

    else:
        print("Unknown command:", cmd)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
