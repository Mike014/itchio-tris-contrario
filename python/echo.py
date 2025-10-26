import sys
sys.stdout.write("Echo pronto. Scrivi qualcosa (exit per uscire): ")
sys.stdout.flush()

for line in sys.stdin:
    s = line.rstrip("\r\n")
    if s.lower() == "exit":
        print("Bye!")
        break
    print(f"Hai scritto: {s}")
    sys.stdout.write(">> ")
    sys.stdout.flush()
