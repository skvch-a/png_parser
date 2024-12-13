try:
    from PIL import Image
    CAN_VISUALIZE = True
except ImportError:
    Image = None
    CAN_VISUALIZE = False