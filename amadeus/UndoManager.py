class Action:
    def __init__(self):
        self.take_action_list = []
        self.reverse_action_list = []
        self.description = ''

class UndoManager:
    def __init__(self):
        self.actions = []
        self.index = -1
    
    def take_actions(self, arr):
        for function_to_execute in arr:
            function_to_execute()

    def add_action(self, take_action_list, reverse_action_list, description = 'No description given, yell at the devs'):
        new_action = Action()
        new_action.take_action_list = take_action_list
        new_action.reverse_action_list = reverse_action_list
        new_action.description = description
        self.actions = self.actions[:self.index] # overwriting future actions
        self.actions.append(new_action)
        self.index += 1

    def add_action_and_take(self, take_action_list, reverse_action_list, description = 'No description given, yell at the devs'):
        self.add_action(take_action_list, reverse_action_list, description)
        self.take_actions(take_action_list)
    
    def undo(self):
        if self.index == -1:
            raise Exception('No more actions to take, you are as far back as you can go via undo')
        action = self.actions[self.index]
        self.take_actions(action.reverse_action_list)
        self.index -= 1
        return action.description

    def redo(self):
        redo_index = self.index + 1
        if redo_index > len(self.actions):
            raise Exception('No more actions to take, you are at the most recent point in history tracked via redo')
        action = self.actions[self.index]
        self.take_actions(action.take_action_list)
        self.index += 1
        return action.description