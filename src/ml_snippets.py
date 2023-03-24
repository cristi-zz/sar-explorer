"""
Snippets of code from various personal projects. Very useful in the context of ML.

"""

import torch.multiprocessing as torch_mp
import multiprocessing as mp
from datetime import datetime
import random
import torch

num_dloader_workers = 0
num_cuda_workers = 2


def manual_pool(func_name, param_list, num_workers):
    crt_idx = 0
    pool = []
    while crt_idx < len(param_list):
        while len(pool) < num_workers:
            if crt_idx >= len(param_list):
                break
            # print(f"{datetime.now()} Creating process id {crt_idx}")
            p = torch_mp.Process(target=func_name, name=f"manual_pool_{crt_idx}",
                              args=param_list[crt_idx],
                              daemon=False)
            # print(f"{datetime.now()} Starting process id {crt_idx}")
            p.start()
            pool.append(p)
            crt_idx += 1

        finished_processes = mp.connection.wait([p.sentinel for p in pool])
        tmp_pool = []
        for p in pool:
            if p.sentinel not in finished_processes:
                tmp_pool.append(p)
        pool = tmp_pool
    # wait for the last processes to finish
    for p in pool:
        p.join()


def parallel_train_and_eval_the_networks(experiment_basepath, experiment_data_file, resume, cuda_devices, randomize_exp_order=True):
    # print(f"{datetime.now()} Start multiprocessing result computation")
    print(f"{datetime.now()} Set spawn method ON")
    torch_mp.set_start_method('spawn')
    # Because reasons, VERY SLOW on dgx
    print(f"{datetime.now()} Creating the Manager context...")
    with mp.Manager() as manager:
        print(f"{datetime.now()} Generating the locks")
        progress_lock = manager.Lock()
        results_lock = manager.Lock()
        log_file = read_progress_file(experiment_basepath / progress_filename, progress_lock)
        call_params = []
        no_of_devices = len(cuda_devices)
        cuda_device = None
        experiment_indexes = list(log_file.index)
        if randomize_exp_order:
            experiment_indexes = random.sample(experiment_indexes, k=len(experiment_indexes))
        for k, row_idx in enumerate(experiment_indexes):
            if no_of_devices > 0:
                cuda_device = cuda_devices[k % no_of_devices]
            call_param = (experiment_basepath, experiment_data_file, row_idx, progress_lock, results_lock, resume, cuda_device)
            call_params.append(call_param)
        print(f"{datetime.now()} About to start experiment with {len(log_file.index)} experiments on {no_of_devices} cuda devices, with {num_cuda_workers} parallel workers")
        manual_pool(train_and_eval_one_network, call_params, num_cuda_workers)
        print(f"{datetime.now()} Done multiprocessing result computation")


def get_gpu_stats():
    no_devices = torch.cuda.device_count()
    devices = [f"cuda:{k}" for k in range(no_devices)]
    return devices
