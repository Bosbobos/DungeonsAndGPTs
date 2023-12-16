from enum import Enum


class CharacterStateEnum(Enum):
    WaitingForWorldCreationInput = 'WaitingForWorldCreationInput'
    WaitingForCharacterCreationInput = 'WaitingForCharacterCreationInput'
    WaitingForCharacterCreationAssessment = 'WaitingForCharacterCreationAssessment'
    WaitingForCharacteristicChangeInput = 'WaitingForCharacteristicChangeInput'
    WaitingForGearCreation = 'WaitingForGearCreation'
    WaitingForCampaignStart = 'WaitingForCampaignStart'
    WaitingForPlayerAction = 'WaitingForPlayerAction'
    Exploring = 'Exploring'
    InBattle = 'InBattle'
    WaitingForDmAction = 'WaitingForDmAction'
    WaitingForEnemyAction = 'WaitingForEnemyAction'
    InFinalBattle = 'InFinalBattle'
    FinalBossDefeated = 'FinalBossDefeated'
    CampaignEnded = 'CampaignEnded'
