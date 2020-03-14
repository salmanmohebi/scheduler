from scheduler.envs.service_period_allocation import ConstantBitRateTraffic


cbr = ConstantBitRateTraffic(
    maximum_generated_packet=10,
    packet_generation_period=3,
    maximum_queue_length=10,
    delay_bound=10,
    first_packet_time=1
)
for tt in range(0, 50, 5):
    print(f'The time is now: {tt}')
    cbr.drop_outdated_packets(tt)
    cbr.generate_data(tt)
    cbr.drop_outdated_packets(tt)