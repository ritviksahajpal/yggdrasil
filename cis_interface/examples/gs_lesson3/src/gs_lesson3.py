# Import classes for input/output channels
from cis_interface.interface.PsiInterface import PsiInput, PsiOutput

# Initialize input/output channels
in_channel = PsiInput('input')
out_channel = PsiOutput('output')

# Receive input from input channel
# If there is an error, the flag will be False
flag, msg = in_channel.recv()

# Print received message
print(msg)

# Send output to output channel
# If there is an error, the flag will be False
flag = out_channel.send(msg)