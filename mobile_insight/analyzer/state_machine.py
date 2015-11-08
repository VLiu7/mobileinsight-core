#!/usr/bin/python
# Filename: state_machine.py
"""
State machine abstraction

Abstract protocol FSMs, and operationnal policies (algorithms)

Author: Yuanjie Li
"""

__all__=["StateMachine"]

class StateMachine(object):
    
    def __init__(self,state_machine,init_callback):
        '''
        Initialize a state machine with a pre-define profile
        Example:

            state_machine={'RRC-IDLE':{'RRC-CONNECTED':conn_callback},
                           'RRC-CONNECTED':{'RRC-IDLE':idle_callback}}
            #define initial state callback
            def init_callback(event):
                if event.type=="RRC setup" or event.type=="RRC reconfig":
                    return "RRC-CONNECTED"
                elif event.type=="SIB" or event.type=="RRC release":
                    return "RRC-IDLE"
            def conn_callback(event):
                return event.type=="RRC Setup"
            def idle_callback(event):
                return event.type=="RRC release"
            x = StateMachine(state_machine,init_callback)


        :param state_machine: a state machnie dictionary {FromState:{ToState:transition_callback}}
        :type state_machine: dictionary
        :param init_callback: the state initialization callback
        :type analyzer: boolean function with 1 parameter
        '''
        self.state_machnie = state_machine
        self.init_callback = init_callback
        self.cur_state = None

    def __init_state(self,event):
        '''
        A specical callback to initiate the current state.
        Why this is needed: when MobileInsight starts, the device can be in any state. 
        The state machnie must have a callback to determine the initial state.
        This callback is protocol specific, since it depends on specific messages
        '''
        if not self.cur_state:
            init_state = init_callback(event)
            if init_state in self.state_machine.keys():
                #Always check if the new state is declared
                self.cur_state = init_state

    def update_state(self,event):
        '''
        Trigger state transition from analyzer events. 
        If more than one state transition is satisfied, return False

        :param event: the event from analyzer
        :type event: Event
        :returns: True if state updated (including no change), or False if transition fails
        '''

        if not self.cur_state:
            #state not initialized yet
            self.__init_state(event)
        else:
            #assert: state always declared in state_machine (checked by __init_state)
            tx_condition=[]
            for item in self.state_machine[self.cur_state]:
                #evaluate the transition condition 1-by-1
                if self.state_machine[self.cur_state][item](event):
                    tx_condition.append(item)
            
            if len(tx_condition)>1:
                #More than 1 state transition is satisfied
                return False
            elif len(tx_condition)==1:
                self.cur_state = tx_condition[0]
            return True
        

    def get_current_state(self):
        '''
        Get current state

        :returns: current state
        '''
        return self.cur_state

    def get_transition_condition(self,src,dest):
        '''
        Get transition condition from source to destination

        :param src: source state
        :type src: string
        :param dest: destination state
        :type dest: string
        :returns: an ordered list of callbacks that represent the state transition
        ''' 
        pass
