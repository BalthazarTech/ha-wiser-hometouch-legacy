# Wiser HomeTouch Legacy pour Home Assistant

Intégration personnalisée Home Assistant destinée à l'ancienne passerelle Schneider Electric **Wiser HomeTouch CCT501510**.

> Ce projet est maintenu par la communauté. Il n'est ni affilié à Schneider Electric, ni approuvé officiellement par Schneider Electric.

## Fonctionnalités actuelles

- Communication locale avec le HomeTouch via son API HTTP OCF
- Configuration depuis l'interface de Home Assistant
- Modification de l'adresse IP du HomeTouch depuis **Reconfigurer**, sans supprimer l'intégration ni recréer les entités
- Vérification de la nouvelle adresse IP avant enregistrement
- Sélecteur des **Basic Moments** affichés en français :
  - Maison
  - Absent
  - Nuit
- Sélecteur des **User Moments**, avec détection dynamique des scénarios personnalisés
- Pilotage bidirectionnel : les changements effectués sur le HomeTouch sont remontés dans Home Assistant et les sélections effectuées dans Home Assistant sont envoyées au HomeTouch
- Création d'un User Moment depuis les actions Home Assistant
- Suppression d'un User Moment depuis les actions Home Assistant
- Rafraîchissement automatique du sélecteur de scénarios après création ou suppression
- Plusieurs tentatives de lecture avant de déclarer le HomeTouch indisponible
- Fonctionnement entièrement local, sans dépendance au cloud Schneider

## Matériel testé

- Schneider Electric Wiser HomeTouch **CCT501510**
- Firmware HomeTouch observé pendant le développement : **8.4.2-2737**

## Installation

L'intégration peut être installée depuis HACS en ajoutant ce dépôt comme dépôt personnalisé de type **Intégration**.

Pour une installation manuelle, copier le dossier :

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

### Modifier l'adresse IP après l'installation

Si le HomeTouch reçoit une nouvelle adresse IP, il n'est pas nécessaire de supprimer puis réinstaller l'intégration.

Dans **Paramètres → Appareils et services → Wiser HomeTouch Legacy**, ouvrir le menu de l'entrée puis choisir **Reconfigurer**. Saisir la nouvelle adresse IP. Home Assistant vérifie qu'un HomeTouch compatible répond à cette adresse, enregistre la modification puis recharge automatiquement l'intégration.

Les entités et les automatisations existantes sont conservées.

## Entités

L'intégration crée actuellement deux entités `select` :

- **Mode chauffage** — Basic Moments affichés comme `Maison`, `Absent`, `Nuit`
- **Scénario** — User Moments configurés sur le HomeTouch

## Actions Home Assistant

### Créer un scénario

Action :

```text
wiser_hometouch_legacy.create_user_moment
```

Champ requis : `name`

Exemple :

```yaml
action: wiser_hometouch_legacy.create_user_moment
data:
  name: Vacances
```

### Supprimer un scénario

Action :

```text
wiser_hometouch_legacy.delete_user_moment
```

Champ requis : `name`

Exemple :

```yaml
action: wiser_hometouch_legacy.delete_user_moment
data:
  name: Vacances
```

Les actions vérifient respectivement que le scénario n'existe pas déjà ou qu'il existe avant d'envoyer la commande au HomeTouch.

## Correspondance avec l'API du HomeTouch

L'interface Home Assistant utilise les libellés français, tandis que l'API interne du HomeTouch conserve ses valeurs techniques :

- `Maison` ↔ `Home`
- `Absent` ↔ `Away`
- `Nuit` ↔ `Sleep`

Cette conversion est transparente pour l'utilisateur.

## Feuille de route

- Diagnostics
- Options de configuration du délai d'interrogation
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

Pour créer une scène, l'intégration envoie un `POST` à `sceneCollection/1`. Pour la supprimer, elle utilise un `DELETE` sur la même ressource, avec la scène concernée dans `sceneValues`.

## Licence

MIT
