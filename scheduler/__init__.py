from gym.envs.registration import register

register(
    id='SimpleServicePeriodAllocation-v0',
    entry_point='scheduler.envs:SimpleServicePeriodAllocationV0',
)
