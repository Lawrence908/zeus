# zeus/core/zeus_os/ — Bridge for Zeus OS, the tiling-WM web shell.
#
# Mounts under /zeus-os/* on the Zeus core FastAPI bus. See zeus-os/ for the
# SvelteKit frontend, and zeus/docs/zeus-os.md for the design overview.
from zeus.core.zeus_os.router import router

__all__ = ["router"]
