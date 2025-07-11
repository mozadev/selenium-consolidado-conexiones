from fastapi import HTTPException
from app.modules.web_bots.browser.setup import setup_edge_driver
from app.modules.web_bots.semaforo.scripts.semaforo_scraper import scrape_semaforo_page
from config import SEMAFORO_USER, SEMAFORO_PASSWORD
import time
from utils.logger_config import get_semaforo_logger
import os

logger = get_semaforo_logger()

class SemaforoService:
    def descargarReporteWebScraping(self, fecha_inicio, fecha_fin):
        driver = None
        try:
            if not SEMAFORO_USER or not SEMAFORO_PASSWORD:
                logger.error("New Call Center credenciales no encontradas en .env file")
                raise HTTPException(
                    status_code=500,
                    detail="Credenciales de Semaforo no configuradas"
                )
            
            download_path = os.path.abspath("media/semaforo/")
            if not os.path.exists(download_path):
                os.makedirs(download_path)

            try:        
                logger.info('Empezando scraping de SEMAFORO')
                
                driver = setup_edge_driver(download_directory=download_path)
                logger.info("-> Navegando a la página de login...")
                driver.get("http://10.200.81.218:3000/login")
                logger.info("URL actual tras get(): %s", driver.current_url)
                
                path_semaforo_report = scrape_semaforo_page(driver, SEMAFORO_USER, SEMAFORO_PASSWORD, fecha_inicio, fecha_fin)
                
                if path_semaforo_report:
                    logger.info(f"Resultado del scraping: {path_semaforo_report}")
                    return path_semaforo_report
                else:
                    logger.error("No se pudo obtener un reporte de Semaforo")
                    raise HTTPException(
                        status_code=500,
                        detail="Fallo al obtener el reporte de Semaforo"
                    )

            except Exception as e:
                logger.error(f"Error en scraping de SEMAFORO: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error en proceso de scraping: {str(e)}"
                )

            finally:
                if driver:
                    try:
                        driver.quit()
                        logger.info("SEMAFORO CERRADO")
                    except Exception as e:
                        logger.error(f"Error al cerrar el driver: {str(e)}")
                
        except HTTPException:
            raise
            
        except Exception as e:
            error_message = f"Error al descargar reporte: {str(e)}"
            logger.error(error_message)
            raise HTTPException(
                status_code=500,
                detail=error_message
            )