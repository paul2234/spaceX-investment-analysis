import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

class Analysis:
    def __init__(self,current,base_assumptions,years,runs,current_valuation,working_capital):
        self.current = current
        self.base_assumptions = base_assumptions
        self.years = years
        self.runs = runs
        self.current_valuation = current_valuation
        self.working_capital = working_capital
        
        self.valuations = self.calculate_valuations()
        self.valuations = np.where(np.array(self.valuations) < 0,0,np.array(self.valuations))
        
        self.absolute_returns = [v / self.current_valuation for v in self.valuations]
        self.f_max, self.f_values, self.g_values = self.calc_kelly()
        self.investment_amount = self.calc_investment_amount()
        

    def calculate_future_valuation(self,current,assumptions):
    
        current_launch_revenue = current["launch"]
        current_starlink_revenue = current["starlink"]
    
        assumed_launch_market_growth = assumptions["launch_market_growth"]
        assumed_launch_market_share = assumptions["launch_market_share"]
        assumed_subscriber_growth = assumptions["starlink_annual_subscriber_growth"]
        assumed_ps_ratio = assumptions["assumed_ps_ratio"]
    
        future_launch_revenue = current_launch_revenue * (1 + assumed_launch_market_growth) ** self.years
        future_starlink_revenue = current_starlink_revenue * (1 + assumed_subscriber_growth) ** self.years
        future_total_revenue = future_launch_revenue + future_starlink_revenue
    
        future_valuation = future_total_revenue * assumed_ps_ratio
    
        return future_valuation
        
    def generate_value_array(self,val,std_dev,runs):
    
        vals = val * np.random.normal(1,std_dev,runs)
    
        return vals
    
    def calculate_valuations(self):
    
        launch_market_growth_values =       self.generate_value_array(self.base_assumptions["value"]["launch_market_growth"],self.base_assumptions["pct_std_dev"]["launch_market_growth"],self.runs)
        launch_market_share_values =        self.generate_value_array(self.base_assumptions["value"]["launch_market_share"],self.base_assumptions["pct_std_dev"]["launch_market_share"],self.runs)
        assumed_subscriber_growth_values =  self.generate_value_array(self.base_assumptions["value"]["starlink_annual_subscriber_growth"],self.base_assumptions["pct_std_dev"]["starlink_annual_subscriber_growth"],self.runs)
        assumed_ps_ratio_values =           self.generate_value_array(self.base_assumptions["value"]["assumed_ps_ratio"],self.base_assumptions["pct_std_dev"]["assumed_ps_ratio"],self.runs)
    
        valuations = []
    
        for i in range(self.runs):
        
            assumptions = {
                "launch_market_growth":launch_market_growth_values[i],
                "launch_market_share": launch_market_share_values[i],
                "starlink_annual_subscriber_growth":assumed_subscriber_growth_values[i],
                "assumed_ps_ratio":assumed_ps_ratio_values[i]
            }
        
            valuation = self.calculate_future_valuation(current,assumptions)
            valuations.append(valuation)
    
        return valuations
        
    def valuation_distribution(self):
        plt.hist(self.valuations,bins = 100)
        plt.show()
        
        return
        
    def absolute_return_distribution(self):
        plt.hist(self.absolute_returns,bins = 100)
        plt.show()
        
        return
        
    def calc_G(self,df_bins_agg,f,dS):
    
        G = 0
    
        for index, row in df_bins_agg.iterrows():
        
            s = row.bin_bucket.right
            p = row.norm_absolute_returns
        
            try:
                G = G + math.log(1 + f * s) * p * dS
            except:
                return -1
    
        return G

    def calc_f_max(self,f_values,g_values):
    
        f = f_values[0]
    
        prev_g = 0
    
        for i in range(len(g_values)):
            if i > 0:
                if g_values[i] > prev_g:
                    f = f_values[i]
                else:
                    return f
                
        return f

    def calc_kelly(self):

        #get min & max of absolute_returns
        A = np.min(self.absolute_returns)
        B = np.max(self.absolute_returns)
        dS = 0.1
    
        s_array = np.arange(A - dS,B + dS,dS)

        #get absolute returns into bins
        bins = pd.cut(x = self.absolute_returns,bins = s_array)
    
        df_bins = pd.DataFrame(data = {
            "absolute_returns":self.absolute_returns,
            "bin_bucket":bins
            })
    
        #aggregate bins
        df_bins_agg = df_bins.groupby("bin_bucket").count().reset_index()
        df_bins_agg["norm_absolute_returns"] = df_bins_agg.absolute_returns / df_bins_agg.absolute_returns.sum()
    
        f_values = np.arange(0.01,1.01,0.01)
        g_values = []
    
        for f in f_values:
            G = self.calc_G(df_bins_agg,f,dS)
            g_values.append(G)
        
        f_max = self.calc_f_max(f_values,g_values)
    
        return f_max,f_values,g_values
        
    def calc_investment_amount(self):
        
        return self.working_capital * self.f_max

      
current = {
    "launch": 2270000000.00,
    "starlink":980000000.00
}

base_assumptions = {
    "value":{"launch_market_growth":0.157,
        "launch_market_share": 0.6,
        "starlink_annual_subscriber_growth":0.5,
        "assumed_ps_ratio":51.62
    }
    ,"pct_std_dev":{"launch_market_growth":0.5,
        "launch_market_share": 0.5,
        "starlink_annual_subscriber_growth":0.5,
        "assumed_ps_ratio":0.5
    }
}

years = 3
runs = 10000
current_valuation = 140000000000
working_capital = 250000

spaceX = Analysis(current,base_assumptions,years,runs,current_valuation,working_capital)
spaceX.absolute_return_distribution()

        