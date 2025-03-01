# scripts/deploy.py
import subprocess
import os

def run_terraform():
    os.chdir("../terraform")
    subprocess.run(["terraform", "init"], check=True)
    subprocess.run(["terraform", "apply", "-auto-approve"], check=True)
    os.chdir("../scripts")

def run_optimizer():
    subprocess.run(["python", "firewall_optimizer.py"], check=True)

if __name__ == "__main__":
    print("Deploying infrastructure via Terraform...")
    run_terraform()
    print("\nRunning firewall optimization...")
    run_optimizer()
