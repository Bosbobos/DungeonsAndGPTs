from enum import Enum

class CharacterStateEnum(Enum):
    WaitingForWorldCreationInput = 'WaitingForWorldCreationInput'
    WaitingForCharacterCreationInput = 'WaitingForCharacterCreationInput'
    WaitingForCharacterCreationAssessment = 'WaitingForCharacterCreationAssessment'
    WaitingForCharacteristicChangeInput = 'WaitingForCharacteristicChangeInput'
    WaitingForGearCreation = 'WaitingForGearCreation'
    WaitingForCampaignStart = 'WaitingForCampaignStart'
    WaitingForDmAction = 'WaitingForDmAction'
    WaitingForEnemyAction = 'WaitingForEnemyAction'
    CampaignEnded = 'CampaignEnded'
