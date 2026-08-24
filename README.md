# Wiser HomeTouch Legacy pour Home Assistant

Intégration personnalisée Home Assistant destinée à l'ancienne passerelle Schneider Electric **Wiser HomeTouch CCT501510**.

> Ce projet est maintenu par la communauté. Il n'est ni affilié à Schneider Electric, ni approuvé officiellement par Schneider Electric.

## Fonctionnalités actuelles

- Communication locale avec le HomeTouch via son API HTTP OCF
- Configuration depuis l'interface de Home Assistant
- Sélecteur des **Basic Moments** affichés en français :
  - Maison
  - Absent
  - Nuit
- Sélecteur des **User Moments**, avec détection dynamique des scénarios personnalisés
- Pilotage bidirectionnel : les changements effectués sur le HomeTouch sont remontés dans Home Assistant et les sélections effectuées dans Home Assistant sont envoyées au HomeTouch
- Fonctionnement entièrement local, sans dépendance au cloud Schneider

## Matériel testé

- Schneider Electric Wiser HomeTouch **CCT501510**
- Firmware HomeTouch observé pendant le développement : **8.4.2-2737**

## Installation manuelle

Copier le dossier :

```text
custom_components/wiser_hometouch_legacy
```

dans :

```text
/config/custom_components/
```

Redémarrer Home Assistant, puis aller dans :

**Paramètres → Appareils et services → Ajouter une intégration → Wiser HomeTouch Legacy**

Renseigner l'adresse IP locale du HomeTouch.

## Entités

L'intégration crée actuellement deux entités `select` :

- **Mode chauffage** — Basic Moments affichés comme `Maison`, `Absent`, `Nuit`
- **Scénario** — User Moments configurés sur le HomeTouch

## Correspondance avec l'API du HomeTouch

L'interface Home Assistant utilise les libellés français, tandis que l'API interne du HomeTouch conserve ses valeurs techniques :

- `Maison` ↔ `Home`
- `Absent` ↔ `Away`
- `Nuit` ↔ `Sleep`

Cette conversion est transparente pour l'utilisateur.

## Feuille de route

- Création des User Moments depuis Home Assistant
- Suppression des User Moments depuis Home Assistant
- Amélioration de la tolérance aux délais d'attente et aux réponses irrégulières de l'ancien serveur HTTP du HomeTouch
- Diagnostics
- Découverte des appareils encore associés au HomeTouch et prise en charge en lecture
- Étude du pilotage des thermostats via le HomeTouch pour les utilisateurs souhaitant conserver leur ancien réseau Zigbee Wiser

## Notes techniques

L'intégration utilise les ressources OCF locales exposées par le HomeTouch, notamment :

```text
/ocf/oic/resx?if=oic.if.b
/ocf/sceneCollection/0
/ocf/sceneCollection/1
```

`sceneCollection/0` contient les Basic Moments fixes (`Home`, `Away`, `Sleep`) utilisés en interne par l'API.

`sceneCollection/1` contient les User Moments personnalisables.

## Licence

MIT
