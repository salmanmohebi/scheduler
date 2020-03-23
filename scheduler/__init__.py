from gym.envs.registration import register

register(
    id='ServicePeriodAllocation-v0',
    entry_point='scheduler.envs:ServicePeriodAllocationV0',
)
register(
    id='ServicePeriodAllocation-v1',
    entry_point='scheduler.envs:ServicePeriodAllocationV1',
)

register(
    id='CommsRLTimeFreqResourceAllocation-v0',
    entry_point='scheduler.envs:CommsRLTimeFreqResourceAllocationV0',
)

register(
    id='DtiAllocation-v0',
    entry_point='scheduler.envs:DtiAllocationV0',
)
