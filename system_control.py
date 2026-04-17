from pycaw.pycaw import AudioUtilities


def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    return devices.EndpointVolume


def volume_up(step=0.05):
    volume = get_volume_interface()

    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(1.0, current + step), None)


def volume_down(step=0.05):
    volume = get_volume_interface()

    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(0.0, current - step), None)


def mute_volume():
    volume = get_volume_interface()
    volume.SetMute(1, None)


def unmute():
    volume = get_volume_interface()
    volume.SetMute(0, None)


import os


def shutdown_pc():
    os.system("shutdown /s /t 1")


def restart_pc():
    os.system("shutdown /r /t 1")


def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")


def sleep_pc():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")    

