import subprocess

def run(cmd):
    subprocess.run(cmd, check=True)

# Check Docker
try:
    run(["docker", "info"])
    print("Docker is running")
except subprocess.CalledProcessError:
    raise RuntimeError("Docker is installed but not running")
except FileNotFoundError:
    raise RuntimeError("Docker is not installed")

# Stop and remove old containers
print("Cleaning previous containers...")
run(["docker", "compose", "down"])

# Start fresh
print("Starting containers...")
run(["docker", "compose", "up", "-d"])
print("Containers started successfully")

# Show logs
run(["docker", "compose", "logs", "-f"])