from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random


doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 2
    num_rounds = 12

    instructions_template = 'public_goods/Instructions.html'
    options = [('A',''), ('B', '')] 
    # """Amount allocated to each player"""
    endowment = c(100)
    
    individual_alpha = 0.5                                                      #To be substituted at some point with the actual alpha
    

class Subsession(BaseSubsession):
    
    def before_session_starts(self):
        self.group_randomly()
        for g in self.get_groups():
            info_condition = ['Bel', 'Bel', 'Act', 'Act', 'Ctrl', 'Ctrl', 'No', 'No']
            g.info = info_condition[g.id_in_subsession - 1]
            for p in g.get_players():
                p.info_player = g.info
                p.count_treat()   
            #     if p.ctrl_count == 3:          #####Think a bit better what you wanna achieve
            #         pass                                                                                    #####Here, bzw. not random groups but changin                                        
            #     else:                                                                                       #####Treatment
            #         self.subsession.group_randomly
            

    def retrieve_percentile(self):
        for p in self.get_players():
            p.percentile = p.participant.vars['perc']
              

class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    alpha = models.FloatField()
    info = models.CharField()
    mpcr = models.FloatField()

    def define_alpha(self):
        self.alpha = sum(p.percentile for p in self.get_players())
        
    def define_return(self):
        if self.info == "Ctrl":
            self.mpcr = Constants.individual_alpha
        else:
            self.mpcr = Constants.individual_alpha*(self.alpha)

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.individual_share = self.total_contribution * self.mpcr       ##### QUI BISOGNA AGGIUSTARE CON LA NUOVA DEFINIZIONE DI MPCR ######
        for p in self.get_players():
            p.payoff = (Constants.endowment - p.contribution) + self.individual_share



class Player(BasePlayer):
    percentile = models.FloatField()
    estimate = models.FloatField()
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
    )
    guy = models.CharField()
    relative = models.FloatField(
        min=0, max=100, doc="""Estimate of own ranking""")
    guy_relative = models.CharField()
    payoff_elicitation = models.CurrencyField()
    result_other = models.FloatField()
    rnd = models.PositiveIntegerField()
    ctrl_count = models.FloatField()
    no_count = models.FloatField()
    bel_count = models.FloatField()
    act_count = models.FloatField()
    info_player = models.CharField()


    def count_treat(self):
        self.ctrl_count = 0
        self.no_count = 0
        self.bel_count = 0
        self.act_count = 0
        for p in self.in_all_rounds():
            if p.info_player == "Ctrl":
                self.ctrl_count += 1
            elif p.info_player == "No":
                self.no_count += 1
            elif p.info_player == "Bel":
                self.bel_count += 1
            elif p.info_player == "Act":
                self.act_count += 1


    def count_overconfidence(self):                                                         #da spostare
        d = [self.q_conf_1, self.q_conf_2, self.q_conf_3, self.q_conf_4, self.q_conf_5, 
        self.q_conf_6, self.q_conf_7, self.q_conf_8, self.q_conf_9, self.q_conf_10]
        self.estimate = 0
        for i in range(0,10):
            if d[i] == 'A':
                self.estimate += 0.10


    # def identify_overconfident(self):                                                       #da spostare e cambiare
    #     if self.estimate > self.cum_count:
    #         self.guy = "Overconfident"
    #     elif self.estimate == self.cum_count:
    #         self.guy = "On spot"
    #     else:
    #         self.guy = "Underconfident"
    
    def percentile_other_guy(self):
        self.result_other = self.get_others_in_group()[0].percentile



    def identify_rel_overconfident(self):                                                    #da spostare
        if self.estimate > self.percentile:
            self.guy_relative = "Overconfident"
        elif self.estimate == self.percentile:
            self.guy_relative = "On spot"
        elif self.estimate < self.percentile:
            self.guy_relative = "Underconfident"
        else:
            self.guy_relative = "Check manually"
    

    def check_and_adjust(self):                                                                 # da spostare
        for i in range(1,11):
            if getattr(self, "q_conf_{0}".format(i)) == 'B':
                for j in range(i, 11):
                    setattr(self, "q_conf_{0}".format(j), 'B')
        
    
    def pay_elicitation(self):
        self.rnd = random.randint(1,10)
        if getattr(self, "q_conf_{0}".format(self.rnd)) == 'A':
            pool = [i for i in range(1,11)]
            chosen = random.choice(pool)
            if chosen > self.rnd:
                self.payoff_elicitation = 0
            else:
                self.payoff_elicitation = 10                        #PAYOFF TO BE DECIDED
        elif getattr(self, "q_conf_{0}".format(self.rnd)) == 'B':
            if self.result_other > self.percentile:
                self.payoff_elicitation = 0
            elif self.result_other < self.percentile:
                self.payoff_elicitation = 10
            else:
                self.payoff_elicitation = random.choice([0,10])



    q_conf_1 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_2 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_3 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_4 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_5 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_6 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_7 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_8 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_9 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
    q_conf_10 = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())
 


    
