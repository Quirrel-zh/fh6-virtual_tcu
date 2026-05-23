import struct
from typing import Optional

from virtual_tcu.telemetry.model import FH6_PACKET_SIZE, Telemetry


def parse_fh6_packet(data: bytes) -> Optional[Telemetry]:
    if len(data) < 324 or len(data) < FH6_PACKET_SIZE:
        return None
        
    try:
        is_race, _ts, max_rpm, _idle, cur_rpm = struct.unpack_from("<iIfff", data, 0)
        ax, ay, az = struct.unpack_from("<fff", data, 20)
        vx, vy, vz = struct.unpack_from("<fff", data, 32)
        avx, avy, avz = struct.unpack_from("<fff", data, 44)
        speed, power, torque = struct.unpack_from("<fff", data, 256)
        boost = struct.unpack_from("<f", data, 284)[0]
        
        accel = data[315]
        brake = data[316]
        clutch = data[317]
        gear = data[319]
        
        car_ord, car_cls, _pi, drivetrain, ncyl = struct.unpack_from(
            "<iiiii", data, 212
        )
        slip_fl, slip_fr, slip_rl, slip_rr = struct.unpack_from("<ffff", data, 136)
    except (struct.error, IndexError):
        return None

    is_shifting = gear > 10

    return Telemetry(
        is_race_on=is_race,
        engine_max_rpm=max_rpm,
        current_rpm=cur_rpm,
        accel_x=ax,
        accel_y=ay,
        accel_z=az,
        vel_x=vx,
        vel_y=vy,
        vel_z=vz,
        ang_vel_x=avx,
        ang_vel_y=avy,
        ang_vel_z=avz,
        speed_ms=speed,
        power_w=power,
        torque_nm=torque,
        boost_raw=boost,
        accel_raw=accel,
        brake_raw=brake,
        clutch_raw=clutch,
        gear=gear,
        car_ordinal=car_ord,
        car_class=car_cls,
        drivetrain=drivetrain,
        num_cylinders=ncyl,
        slip_fl=slip_fl,
        slip_fr=slip_fr,
        slip_rl=slip_rl,
        slip_rr=slip_rr,
        is_shifting=is_shifting,
    )
