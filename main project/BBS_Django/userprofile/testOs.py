import os

# 只是用来测试MEDIA_ROOT的路径是否正确

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
print(MEDIA_ROOT)