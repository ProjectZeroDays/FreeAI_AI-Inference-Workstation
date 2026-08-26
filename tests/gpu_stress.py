"""GPU stress harness (ROADMAP 9)."""
import subprocess, time, sys
def stress(duration_s=60):
    start=time.time()
    while time.time()-start < duration_s:
        subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader"], capture_output=True)
        time.sleep(0.5)
    print("GPU stress done")
if __name__=="__main__": stress(int(sys.argv[1]) if len(sys.argv)>1 else 60)
