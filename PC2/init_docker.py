import subprocess

# Check for docker
try:
    subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    print("Docker is running")
except subprocess.CalledProcessError:
    raise RuntimeError("Docker is installed but not running")
except FileNotFoundError:
    raise RuntimeError("Docker is not installed")

subprocess.run(["docker", "compose", "up", "-d"], check=True)