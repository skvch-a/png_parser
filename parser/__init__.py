try:
    from PIL import Image
    CAN_VISUALIZE = True
except ImportError:
    CAN_VISUALIZE = False
    Image = None