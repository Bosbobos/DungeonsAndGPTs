from CharacterStateEnum import CharacterStateEnum


def SetCharacterState(dbContext, username, state):
    """
    Set the current state of a character in the campaign.

    This function updates or creates a record in the 'character_state' database
    with the specified character state for the given username.

    @param dbContext: The database context for accessing character state information.
    @type dbContext: DatabaseContext

    @param username: The username associated with the character.
    @type username: str

    @param state: The character state to be set.
    @type state: CharacterStateEnum or None

    @return: None
    """
    if state == None or state == CharacterStateEnum.WaitingForWorldCreationInput:
        info = {'Username': username, "current_state": state.name, 'turn': 0}
        dbContext.create_record('character_state', info)
    else:
        dbContext.update_latest_record('character_state', 'username', username, {
                                       "current_state": state.name})


def GetCharacterState(dbContext, username):
    """
    Get the current state of a character in the campaign.

    This function retrieves the current state of the character with the specified
    username from the 'character_state' database.

    @param dbContext: The database context for accessing character state information.
    @type dbContext: DatabaseContext

    @param username: The username associated with the character.
    @type username: str

    @return: The current state of the character or None if the character state is not found.
    @rtype: CharacterStateEnum or None
    """
    record = dbContext.read_latest_record(
        'character_state', 'username', username)
    if record:
        state = record['current_state']
        return CharacterStateEnum[state]
    else:
        return None
