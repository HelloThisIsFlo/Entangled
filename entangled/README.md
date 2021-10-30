# Entangled

## To get started
- Create a `.env` file in `entangled` folder
- Add the following envvars:
    - `MQTT_USER`
    - `MQTT_PASS`
    - `PLEX_USER`
    - `PLEX_PASS`
    - `PLEX_RESOURCE`
        - Leave this one empty for now
- Run: `pipenv run python print_all_resources.py`
- Update `PLEX_RESOURCE` with desired resource
    - It will show: `<MyPlexResource:XXXXXXXX>`
    - Fill in: `PLEX_RESOURCE='XXXXXXXX'`
- Run: `pipenv shell`