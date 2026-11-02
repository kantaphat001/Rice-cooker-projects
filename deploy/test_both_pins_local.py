import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.50.49.17', username='pi', password='1234', timeout=5)

script = """
import lgpio
import time

h = lgpio.gpiochip_open(0)

def test(trig, echo):
    lgpio.gpio_claim_output(h, trig, 0)
    lgpio.gpio_claim_input(h, echo, lgpio.SET_PULL_DOWN)
    
    # Pulse
    lgpio.gpio_write(h, trig, 1)
    time.sleep(0.000015)
    lgpio.gpio_write(h, trig, 0)
    
    t0 = time.perf_counter()
    timeout = t0 + 0.02
    while lgpio.gpio_read(h, echo) == 0:
        t0 = time.perf_counter()
        if t0 > timeout:
            break
    if t0 > timeout:
        lgpio.gpio_free(h, trig)
        lgpio.gpio_free(h, echo)
        return None
        
    t1 = t0
    timeout = t0 + 0.025
    while lgpio.gpio_read(h, echo) == 1:
        t1 = time.perf_counter()
        if t1 > timeout:
            break
    if t1 > timeout:
        lgpio.gpio_free(h, trig)
        lgpio.gpio_free(h, echo)
        return None
        
    d = ((t1 - t0) * 34300) / 2
    lgpio.gpio_free(h, trig)
    lgpio.gpio_free(h, echo)
    return d

print("20, 21:", [test(20, 21) for _ in range(3)])
print("23, 24:", [test(23, 24) for _ in range(3)])
lgpio.gpiochip_close(h)
"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/test_both_pins.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/test_both_pins.py')
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
