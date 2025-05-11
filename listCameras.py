import cv2

def list_cameras():
    """
    Lists available cameras by testing ports.
    Returns a tuple containing lists of working and available ports.
    """
    working_ports = []
    available_ports = []
    for i in range(10): # Check up to 10 ports (adjust as needed)
        cap = cv2.VideoCapture(i)
        available_ports.append(i)
        if cap.isOpened():
            working_ports.append(i)
            cap.release()
    return available_ports, working_ports

available_ports, working_ports = list_cameras()

print("Available ports:", available_ports)
print("Working ports:", working_ports)