from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants

class BeforeElicit(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.subsession.retrieve_percentile()
        

class Elicitation(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.check_and_adjust()
        self.player.percentile_other_guy()
        
    form_model = models.Player
    form_fields = ['q_conf_1','q_conf_2','q_conf_3','q_conf_4','q_conf_5','q_conf_6',
    'q_conf_7','q_conf_8','q_conf_9','q_conf_10']

class HalfWaitPage(WaitPage):
    wait_for_all_groups = True
    body_text = "Waiting for other participants to fill in their table. Afterwards you are going to move on into Task 2. Instructions follow."
    # def is_displayed(self):
    #     return self.round_number == 1

    #def after_all_players_arrive(self):
        
          

class Introduction(Page):
    """Description of the game. Obtain the alpha and the info condition."""
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        for p in self.group.get_players():
            p.count_overconfidence()
            p.pay_elicitation()
        


class BeforeInfo(Page):
    """Here the player will be reminded of the randomization"""

    def before_next_page(self):
        self.player.identify_rel_overconfident()
        self.player.define_alpha()                          
        self.player.define_return()                         
        self.player.meet_friend()
        #self.player.percentile_other_guy()
        #self.player.count_overconfidence()



class Information(Page):
    """Here the player will be informed on the information condition he's into. Obtain the mpcr."""

    def before_next_page(self):
        self.player.define_return()
        
    def vars_for_template(self):
        mate = self.player.meet_friend()

        return{
            'info_condition': self.player.treat,                                            
            'other_confidence': mate.estimate*100,                                              ######### NEEDS TO BE CHECKED ONCE I TRY THE WHOLE THING THROUGH #######
            'other_result' : self.player.result_other*100,
            'MPCR_CTRL' : self.player.mpcr,                                                 
        }

class Contribute(Page):
    """Player will be informed about mpcr and decide contribution."""

    form_model = models.Player
    form_fields = ['contribution']

    timeout_submission = {'contribution': c(Constants.endowment / 2)}

    def vars_for_template(self):
        return{
            'mpcr': self.player.mpcr,                                                         ######### FIX AND PUT BACK ##########
        }

class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.pay_public()


    body_text = "Waiting for other participants to contribute."

class Expectations(Page):
    form_model = models.Player
    form_fields = ['expected_ability', 'expected_contribution']

    def before_next_page(self):
        if self.round_number == Constants.num_rounds:
            self.group.set_payoffs()
            self.player.pay_elicitation()  
             
        else:
            pass

class Results(Page):
    """Players payoff: How much each has earned"""


    def vars_for_template(self):
        mate = self.player.meet_friend()
        return {
            'mate_contribution' : mate.contribution,
            'total_earnings' : self.player.total_contribution * (self.player.mpcr * 2),
            'remainder': c(100) - self.player.contribution
        }

class EndResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
                                                                       ###### NON OTTIMALE CHE VENGA CALCOLATO ORA...
                                                #####PENSACI PERCHE IN CASO DI REFRESH RICALCOLA ###
        return {
            'random_choice' : self.player.rnd,
            'choice' : self.player.choice,
            'random_public' : self.player.rnd_round,
            'payoff_elicit' : self.player.in_round(1).payoff_elicitation,
            'payoff_public' : self.player.in_round(self.player.rnd_round).payoff_public,
            'final' : self.participant.payoff_plus_participation_fee()
        }
        

class EndVince(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

page_sequence = [
    BeforeElicit,
    Elicitation,
    HalfWaitPage,
    # Halfway,
    Introduction,
    BeforeInfo,
    Information,
    Contribute,
    ResultsWaitPage,
    Expectations,
    #Results,
    EndResults,
    EndVince
]
