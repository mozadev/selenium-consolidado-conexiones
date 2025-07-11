from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from app.modules.web_bots.config.settings import BROWSER_SETTINGS
import os
import tempfile
import shutil
import time
import random
import string
import subprocess

def setup_edge_driver(download_directory=None):
    """Setup Edge driver with window staying open"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    # Create a unique temporary profile directory with random string to avoid conflicts
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    profile_dir = tempfile.mkdtemp(prefix=f"edge_profile_{random_suffix}_")
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    # NUEVAS OPCIONES - Modo incógnito para evitar problemas de identidad
    options.add_argument("--inprivate")
    
    # NUEVAS OPCIONES - Deshabilitar componentes de la cuenta
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-features=msAccount,msProfileUiDefaultState,msOsSyncServiceToggleAllowed")
    
    # Configuración para evitar errores de autenticación de Microsoft
    options.add_argument("--disable-features=msSignInOnHub")
    options.add_argument("--disable-features=msSignedInOnHub")
    options.add_argument("--disable-features=msEdgeIdentityHub")
    options.add_argument("--disable-features=msEdgeSignInOnCredential")
    options.add_argument("--disable-features=msEdgeMSAConfig")
    options.add_argument("--disable-features=msIdentity")
    
    # Mantener la ventana abierta (en Edge se usa diferente)
    options.add_experimental_option("detach", True)
    
    # Modo headless si está configurado
    if BROWSER_SETTINGS['headless']:
        options.add_argument("--headless=new")  # Ejecutar en modo headless
    
    # Anti-detección de automatización
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Manejo de certificados y SSL
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    
    # Opciones adicionales para estabilidad
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-sync')
    
    prefs = {
        # Desactivar diálogos de guardar contraseña
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        # Desactivar inicio de sesión
        "credentials_enable_autosignin": False,
        "autologin.enabled": False,
        # Desactivar otras notificaciones
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.geolocation": 2,
        # Configuraciones por defecto para descargas
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "download.default_directory": download_directory if download_directory else "",
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
    }
    
    # Si se especifica un directorio de descarga, actualizarlo en las preferencias
    if download_directory:
        prefs["download.default_directory"] = os.path.abspath(download_directory)
    
    options.add_experimental_option("prefs", prefs)
    
    # Matar procesos existentes de Edge
    try:
        if os.name == 'nt':  # Solo en Windows
            # Use taskkill con más parámetros para asegurar que se maten todos los procesos
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe", "/T"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
            subprocess.run(["taskkill", "/F", "/IM", "msedgedriver.exe", "/T"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
            # Esperar a que los procesos terminen
            time.sleep(2)
    except Exception:
        pass  # Ignorar si falla la terminación de procesos
    
    # Crear el servicio y driver de Edge
    try:
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(
            service=service,
            options=options
        )
        
        # Configurar timeouts
        driver.implicitly_wait(BROWSER_SETTINGS['timeout'])
        driver.set_page_load_timeout(BROWSER_SETTINGS['page_load_timeout'])
        
        # Ocultar webdriver
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        # Configuración de ventana
        driver.set_window_position(0, 0)
        driver.maximize_window()
        
        # Move mouse para evitar detección
        ActionChains(driver).move_by_offset(100, 100).click().perform()
        
        return driver
    except Exception as e:
        if profile_dir and os.path.exists(profile_dir):
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except:
                pass
        raise e