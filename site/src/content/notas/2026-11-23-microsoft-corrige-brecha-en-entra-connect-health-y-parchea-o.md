---
title: Microsoft corrige brecha en Entra Connect Health y parchea Outlook
dek: El acceso de solo lectura expuso correos de administradores y metadatos; el paquete mensual incluyó más de mil parches y una falla crítica en Outlook.
region: cl
date: '2026-11-23'
why: La combinación de correos de administradores, dominios y datos de licenciamiento podría facilitar campañas de ingeniería social más creíbles contra las organizaciones afectadas. Además, el caso recuerda que los parches de escritorio, como Outlook, siguen siendo una vía de riesgo paralela a los controles de identidad.
source:
  name: FayerWayer
  url: https://www.fayerwayer.com/internet/2026/11/23/metadatos-de-empresas-expuestos-y-mas-de-mil-parches-mensuales-la-doble-presion-de-seguridad-que-enfrenta-microsoft-en-noviembre/
tags:
- ciberseguridad
- microsoft
- phishing
- parches
score: 7.0
demo: false
---
Microsoft notificó un acceso no autorizado a correos de administradores y metadatos organizacionales en Entra Connect Health. La falla ingresó el 23 de julio de 2026, se detectó el 9 de noviembre y se corrigió el 19; la investigación cerró el 20. Según la notificación difundida vía Azure Service Health, el acceso fue de solo lectura y no alteró configuraciones. Quedaron alcanzables identificadores de cliente, dominios iniciales, nivel de licencia, estado de sincronización y un certificado vencido dado de baja en 2024. La empresa descartó exposición de contraseñas, credenciales de sesión o claves criptográficas válidas.

Los administradores no deben instalar actualizaciones por este caso, ya que el ajuste se aplicó en servidores de Microsoft, pero sí preparar a sus equipos ante phishing dirigido a las direcciones expuestas. La compañía recomienda autenticación en dos pasos resistente a phishing en cuentas privilegiadas, revisar la configuración de Connect Health y auditar registros de Entra, además de un script de PowerShell para consultar valores actuales. No se informó cuántas organizaciones fueron afectadas ni quién explotó la falla. Este mes también se corrigió CVE-2026-124194 en Outlook, que exigía actualizar Microsoft 365 Apps for Enterprise y Office LTSC 2021 y 2024.
