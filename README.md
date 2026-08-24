# Wiser HomeTouch Legacy for Home Assistant

Custom Home Assistant integration for the legacy Schneider Electric **Wiser HomeTouch CCT501510**.

> This project is community-maintained and is not affiliated with or endorsed by Schneider Electric.

## Current features

- Local communication with the HomeTouch over its OCF HTTP API
- UI configuration through Home Assistant
- Basic Moments selector:
  - Home
  - Away
  - Sleep
- User Moments selector with dynamically discovered custom moments
- Bidirectional control: changes made on the HomeTouch are reflected in Home Assistant, and selections made in Home Assistant are sent back to the HomeTouch
- Local polling only; no Schneider cloud dependency

## Tested hardware

- Schneider Electric Wiser HomeTouch **CCT501510**
- HomeTouch firmware observed during development: **8.4.2-2737**

## Installation (manual)

Copy the directory:

```text
custom_components/wiser_hometouch_legacy
```

into:

```text
/config/custom_components/
```

Restart Home Assistant, then go to:

**Settings → Devices & services → Add integration → Wiser HomeTouch Legacy**

Enter the local IP address of the HomeTouch.

## Entities

The integration currently creates two `select` entities:

- **Heating mode** — Basic Moments (`Home`, `Away`, `Sleep`)
- **Scenario** — User Moments configured on the HomeTouch

## Roadmap

- Create User Moments from Home Assistant
- Delete User Moments from Home Assistant
- Better retry / resilience handling for older HomeTouch HTTP stacks
- Diagnostics
- Discovery and read-only support for devices still paired to HomeTouch
- Future exploration of thermostat control through HomeTouch for users who retain their legacy Wiser Zigbee network

## Technical notes

The integration uses the local OCF resources exposed by the HomeTouch, including:

```text
/ocf/oic/resx?if=oic.if.b
/ocf/sceneCollection/0
/ocf/sceneCollection/1
```

`sceneCollection/0` contains the fixed Basic Moments. `sceneCollection/1` contains User Moments.

## License

MIT
