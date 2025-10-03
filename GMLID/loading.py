from importlib.resources import path
from pathlib import Path

import GMLID.cuda as cuda_module
import GMLID.glsl as glsl_module

def get_glsl(name: str) -> Path:
    with path(glsl_module, f"{name}.glsl") as pth:
        return pth

def get_cuda(name: str) -> Path:
    with path(cuda_module, f"{name}.cpp") as pth:
        return pth
