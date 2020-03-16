from gym.envs.registration import register

register(
    id='ServicePeriodAllocation-v0',
    entry_point='scheduler.envs:ServicePeriodAllocationV0',
)

register(
    id='CommsRLTimeFreqResourceAllocation-v0',
    entry_point='scheduler.envs:CommsRLTimeFreqResourceAllocationV0',
)
