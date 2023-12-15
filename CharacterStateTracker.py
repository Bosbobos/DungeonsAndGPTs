from CharacterStateEnum import CharacterStateEnum

def SetCharacterState(dbContext, username, state):
    if state == None:
        info = {'Username': username, "current_state": state.name, 'turn':0}
        dbContext.create_record('character_state', info)
    else:
        dbContext.update_latest_record('character_state', 'username', username, {"current_state": state.name})

def GetCharacterState(dbContext, username):
    record = dbContext.read_latest_record('character_state', 'username', username)
    if record: 
        state = record['current_state']
        return CharacterStateEnum[state]
    else: 
        return None
    