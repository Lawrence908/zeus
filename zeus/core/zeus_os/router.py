# zeus/core/zeus_os/router.py — Top-level /zeus-os router; mounts subrouters.
from fastapi import APIRouter

from zeus.core.zeus_os.apps_router import router as apps_router
from zeus.core.zeus_os.config_router import router as config_router
from zeus.core.zeus_os.fs_router import router as fs_router
from zeus.core.zeus_os.pty_ws import router as pty_router
from zeus.core.zeus_os.integrations_router import router as integrations_router
from zeus.core.zeus_os.sys_ws import router as sys_router
from zeus.core.zeus_os.vault_router import router as obsidian_router

router = APIRouter(prefix="/zeus-os", tags=["zeus-os"])
router.include_router(apps_router)
router.include_router(config_router)
router.include_router(fs_router)
router.include_router(pty_router)
router.include_router(sys_router)
router.include_router(obsidian_router)
router.include_router(integrations_router)
