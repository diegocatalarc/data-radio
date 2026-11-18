---
title: Fallo en Optimizely permitió inyectar skimmers en sitios de 178 organizaciones
dek: Atacantes explotaron una vulnerabilidad en el flujo de registro de Optimizely Web Experimentation para inyectar JavaScript malicioso en sitios de marcas australianas y globales.
region: au
date: '2026-11-18'
why: El caso muestra que el JavaScript de terceros de confianza puede convertirse en vector de skimming, lo que sugiere revisar qué scripts de proveedores se cargan en sitios con pagos y credenciales.
source:
  name: iTnews
  url: https://www.itnews.com.au/news/hijacked-website-testing-tool-plants-card-skimmer-on-australian-brands-sites-630407?utm_source=feed&utm_medium=rss&utm_campaign=iTnews+
tags:
- seguridad
- skimming
- optimizely
- javascript
score: 8.0
demo: false
---
Un fallo en el flujo de registro de cuentas de Optimizely Web Experimentation se usó para inyectar JavaScript malicioso en los sitios de al menos 178 organizaciones, entre ellas Vodafone Australia, HSBC Australia, Rest Super, TPG Telecom y Levi's Australia, además de firmas globales como Zoom, la BBC y CNN. El código apareció por primera vez a las 3:21pm AEDT del lunes y casi todos los scripts infectados se limpiaron hacia las 8:10am del martes, según el investigador Scott Helme.

Durante esa ventana el payload evolucionó para sustituir direcciones de wallets de criptomonedas, capturar datos de tarjetas introducidos en formularios propios del sitio, recoger cookies y capturas de pantalla, y redirigir iPhones y iPads sin parchear a kits de explotación. Optimizely confirmó el incidente y dijo haber bloqueado la ruta vulnerable, aplicado un parche, eliminado el código inyectado y notificado a los clientes afectados. TPG pausó Optimizely por precaución y afirmó no haber hallado evidencia de compromiso.
