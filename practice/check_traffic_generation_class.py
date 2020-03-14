from scheduler.envs.service_period_allocation import ConstantBitRateTraffic


cbr = ConstantBitRateTraffic(
    maximum_generated_packet=10,
    packet_generation_period=3,
    maximum_queue_length=10,
    delay_bound=10,
    first_packet_time=0
)
for tt in range(0, 50, 5):
    print(f'The time is now: {tt}')
    cbr.update_queue(tt)
    # cbr.transmit_traffic(2, 50000)
    # cbr.delete_outdated_packets(tt)
    # cbr.generate_new_packets(tt)
    cbr.delete_outdated_packets(tt)