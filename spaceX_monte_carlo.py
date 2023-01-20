import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

current = {
    "launch": 2270000000.00,
    "starlink":442060000.00
}

base_assumptions = {
    "launch_market_growth":0.157,
    "launch_market_share": 0.6,
    "starlink_annual_subscriber_growth":0.5,
    "assumed_ps_ratio":51.62
}

years = 3

def calculate_future_valuation(current,assumptions,years):
    
    current_launch_revenue = current["launch"]
    current_starlink_revenue = current["starlink"]
    
    assumed_launch_market_growth = assumptions["launch_market_growth"]
    assumed_launch_market_share = assumptions["launch_market_share"]
    assumed_subscriber_growth = assumptions["starlink_annual_subscriber_growth"]
    assumed_ps_ratio = assumptions["assumed_ps_ratio"]
    
    future_launch_revenue = current_launch_revenue * (1 + assumed_launch_market_growth) ** years
    future_starlink_revenue = current_starlink_revenue * (1 + assumed_subscriber_growth) ** years
    future_total_revenue = future_launch_revenue + future_starlink_revenue
    
    future_valuation = future_total_revenue * assumed_ps_ratio
    
    return future_valuation
    
def generate_value_array(val,std_dev,runs):
    
    vals = val * np.random.normal(1,std_dev,runs)
    
    return vals
    
def calculate_valuations(current,base_assumptions,runs,years):
    
    launch_market_growth_values = generate_value_array(base_assumptions["launch_market_growth"],1,runs)
    launch_market_share_values = generate_value_array(base_assumptions["launch_market_share"],1,runs)
    assumed_subscriber_growth_values = generate_value_array(base_assumptions["starlink_annual_subscriber_growth"],1,runs)
    assumed_ps_ratio_values = generate_value_array(base_assumptions["assumed_ps_ratio"],1,runs)
    
    valuations = []
    
    for i in range(runs):
        
        assumptions = {
            "launch_market_growth":launch_market_growth_values[i],
            "launch_market_share": launch_market_share_values[i],
            "starlink_annual_subscriber_growth":assumed_subscriber_growth_values[i],
            "assumed_ps_ratio":assumed_ps_ratio_values[i]
        }
        
        valuation = calculate_future_valuation(current,assumptions,years)
        valuations.append(valuation)
    
    return valuations


def calc_G(df_bins_agg,f,dS):
    
    G = 0
    
    for index, row in df_bins_agg.iterrows():
        
        s = row.bin_bucket.right
        p = row.norm_absolute_returns
        
        try:
            G = G + math.log(1 + f * s) * p * dS
        except:
            return -1
    
    return G

def calc_f_max(f_values,g_values):
    
    f = f_values[0]
    
    prev_g = 0
    
    for i in range(len(g_values)):
        if i > 0:
            if g_values[i] > prev_g:
                f = f_values[i]
            else:
                return f
                
    return f

def calc_kelly(absolute_returns):

    #get min & max of absolute_returns
    A = np.min(absolute_returns)
    B = np.max(absolute_returns)
    dS = 0.1
    
    s_array = np.arange(A - dS,B + dS,dS)

    #get absolute returns into bins
    bins = pd.cut(x = absolute_returns,bins = s_array)
    
    df_bins = pd.DataFrame(data = {
        "absolute_returns":absolute_returns,
        "bin_bucket":bins
        })
    
    #aggregate bins
    df_bins_agg = df_bins.groupby("bin_bucket").count().reset_index()
    df_bins_agg["norm_absolute_returns"] = df_bins_agg.absolute_returns / df_bins_agg.absolute_returns.sum()
    
    f_values = np.arange(0.01,1.01,0.01)
    g_values = []
    
    for f in f_values:
        G = calc_G(df_bins_agg,f,dS)
        g_values.append(G)
        
    f_max = calc_f_max(f_values,g_values)
    
    return f_max


investment_amount = 25000
current_valuation = 140000000000
valuations = calculate_valuations(current,base_assumptions,1000,3)
valuations = np.where(np.array(valuations) < 0,0,np.array(valuations))
absolute_returns = [v / current_valuation - 1 for v in valuations]

f_max = calc_kelly(absolute_returns)
print(f_max)


# def calc_G(f,s_array,dN):
# 
#     G = 0
#     
#     for s in s_array:
#         try:
#             G = G + math.log(1 + f * s) * dN
#         except:
#             return -1
#     
#     return G
#     
# print(calc_G(0.01,s_array,dN))
# print(calc_G(0.05,s_array,dN))
# print(calc_G(0.1,s_array,dN))
# print(calc_G(0.25,s_array,dN))
# print(calc_G(0.5,s_array,dN))
# print(calc_G(0.75,s_array,dN))
# print(calc_G(0.9,s_array,dN))
# print(calc_G(0.99,s_array,dN))
# print(calc_G(1,s_array,dN))

# print(s_array)
# print("minimum:",round(np.min(absolute_returns),2))
# print("mean:",round(np.mean(absolute_returns),2))
# print("max:",round(np.max(absolute_returns),2))
# 
# print(np.mean(absolute_returns))
# plt.hist(absolute_returns,bins = 100)
# plt.show()
