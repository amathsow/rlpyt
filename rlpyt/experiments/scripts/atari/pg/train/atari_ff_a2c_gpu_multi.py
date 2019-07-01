
import sys

from rlpyt.utils.launching.affinity import get_affinity
from rlpyt.samplers.gpu.parallel_sampler import GpuParallelSampler
from rlpyt.samplers.gpu.collectors import WaitResetCollector
from rlpyt.envs.atari.atari_env import AtariEnv, AtariTrajInfo
from rlpyt.algos.pg.a2c import A2C
from rlpyt.agents.pg.atari import AtariFfAgent
from rlpyt.runners.multigpu_sync import MultiGpuRl
from rlpyt.utils.logging.context import logger_context
from rlpyt.utils.launching.variant import load_variant, update_config

from rlpyt.experiments.configs.atari.pg.atari_ff_a2c import configs


def build_and_train(slot_affinity_code, log_dir, run_ID, config_key):
    affinity = get_affinity(slot_affinity_code)
    assert isinstance(affinity, list)  # One for each GPU.
    config = configs[config_key]
    variant = load_variant(log_dir)
    config = update_config(config, variant)

    sampler = GpuParallelSampler(
        EnvCls=AtariEnv,
        env_kwargs=config["env"],
        CollectorCls=WaitResetCollector,
        TrajInfoCls=AtariTrajInfo,
        **config["sampler"]
    )
    algo = A2C(optim_kwargs=config["optim"], **config["algo"])
    agent = AtariFfAgent(model_kwargs=config["model"], **config["agent"])
    runner = MultiGpuRl(
        algo=algo,
        agent=agent,
        sampler=sampler,
        affinity=affinity,
        **config["runner"]
    )
    name = config["env"]["game"]
    with logger_context(log_dir, run_ID, name, config):
        runner.train()


if __name__ == "__main__":
    build_and_train(*sys.argv[1:])
