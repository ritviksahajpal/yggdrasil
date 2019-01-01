# Import Python interface
from cis_interface.interface import CisInput, CisOutput
# Import Python module containing model calculation
from shoot import calc_shoot_mass


# Create input/output channels
ShootGrowthRate = CisInput('shoot_growth_rate')
InitShootMass = CisInput('init_shoot_mass')
InitRootMass = CisInput('init_root_mass_shoot')
TimeStep = CisInput('shoot_time_step')
NextRootMass = CisInput('next_root_mass')
NextShootMass = CisOutput('next_shoot_mass', '%lf\n')

# Receive shoot growth rate
flag, input = ShootGrowthRate.recv()
if not flag:
    raise RuntimeError('shoot: Error receiving shoot growth rate.')
r_s = input[0]
print('shoot: Received shoot growth rate: %f' % r_s)

# Receive initial shoot mass
flag, input = InitShootMass.recv()
if not flag:
    raise RuntimeError('shoot: Error receiving initial shootmass.')
S_t = input[0]
print('shoot: Received initial shoot mass: %f' % S_t)

# Receive inital root mass
flag, input = InitRootMass.recv()
if not flag:
    raise RuntimeError('shoot: Error receiving initial root mass.')
R_t = input[0]
print('shoot: Received initial root mass: %f' % R_t)

# Send initial shoot mass
flag = NextShootMass.send(S_t)
if not flag:
    raise RuntimeError('shoot: Error sending initial shoot mass.')

# Keep advancing until there arn't any new input times
i = 0
while True:
    
    # Receive the time step
    flag, input = TimeStep.recv()
    if not flag:
        print('shoot: No more time steps.')
        break
    dt = input[0]
    print('shoot: Received next time step: %f' % dt)

    # Receive the next root mass
    flag, input = NextRootMass.recv()
    if not flag:
        # This raises an error because there must be a root mass for each time step
        raise RuntimeError('shoot: Error receiving root mass for timestep %d.' % (i + 1))
    R_tp1 = input[0]
    print('shoot: Received next root mass: %f' % R_tp1)

    # Calculate shoot mass
    S_tp1 = calc_shoot_mass(r_s, dt, S_t, R_t, R_tp1)
    print('shoot: Calculated next shoot mass: %f' % S_tp1)

    # Output shoot mass
    flag = NextShootMass.send(S_tp1)
    if not flag:
        raise RuntimeError('shoot: Error sending shoot amss for timestep %d.' % (i + 1))

    # Advance masses to next timestep
    S_t = S_tp1
    R_t = R_tp1
    i += 1
