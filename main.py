import io
import sys
import subprocess

ps = subprocess.Popen(
    [sys.executable, "-u", "./sub.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)

reader = io.TextIOWrapper(ps.stdout, encoding='utf8')
while ps.poll() is None:
    char = reader.read(1)
    if char == '\n':
        print('break')
    sys.stdout.write(char)
