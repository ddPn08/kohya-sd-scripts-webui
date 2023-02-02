from tqdm import tqdm
from time import sleep

progress_bar = tqdm(range(10), smoothing=0, desc="steps")
for i in range(10):
    sleep(5)
    progress_bar.update(1)
    progress_bar.set_postfix({"log": f"sleeping 5 sec {i}"})
