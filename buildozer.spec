[app]
# Nome do seu aplicativo
title = Traffic Counter
# Nome do pacote (sem espaços ou caracteres especiais)
package.name = traffic_counter
# Domínio do pacote (pode ser qualquer um invertido)
package.domain = org.test
# Nome do arquivo principal (deve ser main.py)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Bibliotecas necessárias (MUITO IMPORTANTE)
# Se seu app usa apenas Kivy, deixe assim:
requirements = python3,kivy,datetime

# Orientação da tela
orientation = portrait

# Permissões (se precisar de internet, por exemplo, descomente a linha abaixo)
# android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
