# CGESP Home Assistant

Integração com estações meteorológicas do CGE SP (Ipiranga, etc) via scraping da página oficial.

## Instalação

1. Copie a pasta `custom_components/cgesp` para o diretório `config/custom_components/`.
2. Reinicie o Home Assistant.

## Configuração

No `configuration.yaml`:

```yaml
sensor:
  - platform: cgesp
    station_id: "1000840"  # Ipiranga
    name: "CGE Ipiranga"
```

## Sensores criados

- `sensor.cge_ipiranga_temperatura`
- `sensor.cge_ipiranga_temp_max`
- `sensor.cge_ipiranga_temp_min`
- `sensor.cge_ipiranga_umidade`
- `sensor.cge_ipiranga_umidade_max`
- `sensor.cge_ipiranga_umidade_min`
- `sensor.cge_ipiranga_pressao`
- `sensor.cge_ipiranga_pressao_max`
- `sensor.cge_ipiranga_pressao_min`
- `sensor.cge_ipiranga_vento_direcao`
- `sensor.cge_ipiranga_vento_veloc`
- `sensor.cge_ipiranga_vento_rajada`
- `sensor.cge_ipiranga_chuva_atual`
- `sensor.cge_ipiranga_chuva_anterior`
- `sensor.cge_ipiranga_zeramento`