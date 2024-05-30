import argparse
import datetime
import json
import logging
import os
import random
import sys

from tqdm import tqdm

from spider2.envs.spider2 import Spider2Env
from llm_agents.agent import PromptAgent


#  Logger Configs {{{ #
logger = logging.getLogger("spider2")
logger.setLevel(logging.DEBUG)

datetime_str: str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")

file_handler = logging.FileHandler(os.path.join("logs", "normal-{:}.log".format(datetime_str)), encoding="utf-8")
debug_handler = logging.FileHandler(os.path.join("logs", "debug-{:}.log".format(datetime_str)), encoding="utf-8")
stdout_handler = logging.StreamHandler(sys.stdout)
sdebug_handler = logging.FileHandler(os.path.join("logs", "sdebug-{:}.log".format(datetime_str)), encoding="utf-8")

file_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)
stdout_handler.setLevel(logging.INFO)
sdebug_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(module)s/%(lineno)d-%(processName)s\x1b[1;33m] \x1b[0m%(message)s")
file_handler.setFormatter(formatter)
debug_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
sdebug_handler.setFormatter(formatter)

stdout_handler.addFilter(logging.Filter("spider2"))
sdebug_handler.addFilter(logging.Filter("spider2"))

logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(stdout_handler)
logger.addHandler(sdebug_handler)
#  }}} Logger Configs # 



def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end evaluation on the benchmark"
    )
    
    parser.add_argument("--max_steps", type=int, default=15)
    
    parser.add_argument("--max_memory_length", type=int, default=15)
    parser.add_argument("--suffix", type=str, default="")
    parser.add_argument("--test_config_base_dir", type=str, default="evaluation_examples")
    
    parser.add_argument("--model", type=str, default="azure")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=1500)
    parser.add_argument("--stop_token", type=str, default=None)
    
    # example config
    parser.add_argument("--domain", type=str, default="all")
    parser.add_argument("--test_all_meta_path", type=str, default="evaluation_examples/test_all.json")

    # output related
    parser.add_argument("--output_dir", type=str, default="./benchmark/output")
    parser.add_argument("--skip_existing", action="store_true", default=False)
    args = parser.parse_args()

    return args



def test(
    args: argparse.Namespace,
    test_all_meta: dict = None
) -> None:
    scores = []
    
    # log args
    logger.info("Args: %s", args)
    
    cfg_args = \
    {
        "max_steps": args.max_steps,
        "max_memory_length": args.max_memory_length,
        "model": args.model,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
    }

    env_config = \
    {
        "image_name": "dabench-image",
        "init_args": {
            "name": "spider2",
            "work_dir": "/workspace",
            "ports": {
                "5432": "12001"
            }
        }
    }
    
    agent = PromptAgent(
        model=args.model,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        temperature=args.temperature,
        max_memory_length=args.max_memory_length,
        max_steps=args.max_steps,
    )
    
    
    task_config_path = './benchmark/Visual.jsonl'
    with open(task_config_path, "r") as f:
        task_configs = [json.loads(line) for line in f]

    if args.suffix == "":
        experiment_id = args.model + "-" +datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    else:
        experiment_id = args.model + "-" + args.suffix
    
    # TODO: record the task state
    # save all setting to output_dir
    # delete container after finish
    for task_config in task_configs:
        instance_id = experiment_id +"/"+ task_config["id"]
        output_dir = os.path.join(args.output_dir, instance_id)
        result_json_path =os.path.join(output_dir, "dabench/result.json")
        if args.skip_existing and os.path.exists(result_json_path):
            logger.info("Skipping %s", instance_id)
            continue
        if os.path.exists(output_dir):
            os.system(f"rm -rf {output_dir}")
            logger.info("Removed existing %s", output_dir)

        os.makedirs(output_dir, exist_ok=True)

        env = Spider2Env(
            env_config=env_config,
            task_config=task_config,
            cache_dir="./cache",
            mnt_dir=output_dir
        )
    
        agent.set_env_and_task(env)
    
        logger.info('Task input:' + task_config['instruction'])
        done = agent.run()
        trajectory = agent.get_trajectory()

        os.makedirs(os.path.join(output_dir, "dabench"), exist_ok=True)
        result_files = env.post_process()
        dabench_result = {"finished": done, "steps": len(trajectory["trajectory"]),
                           **trajectory, "result_files": result_files}
        with open(os.path.join(output_dir, "dabench/result.json"), "w") as f:
            json.dump(dabench_result, f, indent=2)
        
        logger.info("Finished %s", instance_id)




if __name__ == '__main__':
    args = config()
    
    test(args)