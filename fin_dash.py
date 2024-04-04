import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

import requests
from bs4 import BeautifulSoup
from io import StringIO

sns.set_palette('Set2')
palette = sns.color_palette("Set2")


def get_financial_info(ticker:str):
    """A partir d'un ticker, retourne des données relatives à l'entreprise en question : nom, prix de l'action à date, market cap, devise, les données financières

    Args:
        ticker (str): ticker de l'entreprise
    """

    headers= {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
    }


    url = f"https://stockanalysis.com/stocks/{ticker}/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        stock_price = float(soup.find('div', class_="text-4xl font-bold inline-block").text)
        info = soup.find('div', class_="mt-[1px] text-tiny text-faded").text
        dev = info.replace(' ','').split('·')[-1]
    except:
        stock_price =''
        dev = ''
    market_cap = soup.find('td', class_="whitespace-nowrap px-0.5 py-[1px] text-left text-smaller font-semibold tiny:text-base xs:px-1 sm:py-2 sm:text-right sm:text-small").text


    url = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find('div', class_="mb-0 text-2xl font-bold text-default sm:text-[26px]").text
    info = soup.find('div', class_="block text-sm text-faded lg:hidden").text
    devise = info.split('.')[0]
    fiscal_y = info.split('.')[1]

    urls = {}
    urls['P&L'] = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    urls['Balance_sheet'] = f"https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/"
    urls['Cash_flow'] = f"https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/"

    data = {}
    for key in urls.keys():
        response = requests.get(urls[key], headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        data[key]= pd.read_html(StringIO(str(soup)), attrs={'data-test': 'financials'})[0]
    
    return name, stock_price, market_cap, dev, devise, fiscal_y, data

def income_analysis(pnl, devise:str):
    """Output un graph analytique du P&L sur les dernières annéess

    Args:
        pnl (DataFrame): donnée P&L
        devise (str): devise
    """
    
    income_stat = pnl
    income_stat = income_stat.set_index('Year').transpose()
    income_stat = income_stat[:-1]

    income_stat.index = income_stat.index.astype(int)

    for col in income_stat.columns:
        income_stat[col] = income_stat[col].replace({'-':0})


    col_modif = income_stat.filter(regex='Growth|Margin|Rate|Change').columns
    for col in col_modif:
        income_stat[col] = income_stat[col].str.replace('%','')
        income_stat[col] = income_stat[col].astype(float)
        income_stat[col] = income_stat[col]/100
    income_stat = income_stat.astype(float)

    ax = income_stat.sort_index().plot(y=['Net Income'], linestyle='-',use_index=False, color='gold')
    income_stat.sort_index().plot.bar(y=['Revenue', 'EBITDA','EBIT'], ax=ax)
    plt.title(f'Performance over the years')
    plt.legend(['Net Income', 'Revenue', 'EBITDA','EBIT'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel(devise);

    return income_stat, ax.get_figure()

def balance_sheet_analysis(bsh, devise:str):
    """Output un graph analytique du bilan sur les dernières annéess

    Args:
        bsh (DataFrame): donnée bilan
        devise (str): devise
    """
    
    bs = bsh
    bs = bs.set_index('Year').transpose()
    bs = bs[:-1]

    bs.index = bs.index.astype(int)

    for col in bs.columns:
        bs[col] = bs[col].replace({'-':0})

    col_modif = bs.filter(regex='Growth|Margin|Rate|Change').columns
    for col in col_modif:
        bs[col] = bs[col].str.replace('%','')
        bs[col] = bs[col].astype(float)
        bs[col] = bs[col]/100
    bs = bs.astype(float)

    bs['Net tangible assets'] = bs['Property, Plant & Equipment'] + bs['Total Current Assets'] - bs['Total Liabilities']
    ax = bs.sort_index().plot(y=["Shareholders' Equity", "Net tangible assets"], linestyle='-',use_index=False, color=['gold', 'royalblue'])
    bs.sort_index().plot.bar(y=['Total Assets','Total Liabilities'], ax=ax)
    plt.title(f'Assets over the years')
    plt.legend(["Equity", 'Net tangible assets', 'Total Assets','Total Liabilities'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel(devise);

    return bs, ax.get_figure()

def cash_analysis(cashflow, devise:str):
    """Output un graph analytique du cashflow statement sur les dernières annéess

    Args:
        cashflow (DataFrame): donnée cashflow
        devise (str): devise
    """
    
    cfw = cashflow
    cfw = cfw.set_index('Year').transpose()
    cfw = cfw[:-1]

    cfw.index = cfw.index.astype(int)

    for col in cfw.columns:
        cfw[col] = cfw[col].replace({'-':0})

    col_modif = cfw.filter(regex='Growth|Margin|Rate|Change').columns
    for col in col_modif:
        cfw[col] = cfw[col].str.replace('%','')
        cfw[col] = cfw[col].astype(float)
        cfw[col] = cfw[col]/100
    cfw = cfw.astype(float)

    ax = cfw.sort_index().plot(y=['Free Cash Flow'], linestyle='-',use_index=False, color='gold')
    cfw.sort_index().plot.bar(y=['Financing Cash Flow', 'Investing Cash Flow','Operating Cash Flow'], ax=ax);
    plt.title(f'Cashflow over the years')
    plt.legend(['FCF', 'Financing', 'Investing','Operating'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel(devise);

    return cfw, ax.get_figure()

# les fonctions qui suivent permettent de faire des analyses graphiques d'éléments spécifiques des différents statements financiers

# margin 

def annotate_line(value, color):
    a=value.index[0]
    for v in value:
        plt.text(a,v+0.03, round(v,2), color=color, fontsize=9, fontweight='bold')
        a = a-1

def operating_analysis_2(pnl, devise):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.bar(pnl.index, pnl['Revenue'], label='revenue')
    ax2.plot(pnl['Gross Margin'], color=palette[1], label='gross margin')
    annotate_line(pnl['Gross Margin'], palette[1])
    ax2.plot(pnl['Operating Margin'], color=palette[2], label='operating margin')
    annotate_line(pnl['Operating Margin'], palette[2])
    if pnl['Operating Margin'].min() < 0:
        ax2.set_ylim(pnl['Operating Margin'].min(), 1)
    else:
        ax2.set_ylim(0, 1)
    plt.legend()
    plt.title(f'Operating income')
    plt.xticks(pnl.index)
    ax1.set_ylabel(devise)
    return fig

def operating_expenses(pnl, devise):
    col = list(pnl.iloc[:,pnl.columns.get_loc('Gross Profit')+1:pnl.columns.get_loc('Operating Expenses')].columns)
    data = pnl[col]

    fig, ax = plt.subplots()
    data.sort_index().plot(kind='bar', stacked=True, ax=ax)
    plt.legend()

    for bar in ax.patches:
        if bar.get_height() != 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() / 2 + bar.get_y(),
                    round(bar.get_height()), ha = 'center',
                    color = 'black', size = 8)

    plt.xticks(rotation=360)
    plt.title(f'Operating expenses')
    plt.ylabel(devise)
    return fig

def net_income_wtf(data, year, devise):
    col = list(data.iloc[:,data.columns.get_loc('Operating Income'):data.columns.get_loc('Net Income Growth')].columns)
    col.remove('Pretax Income')
    waterf_data = data[col]
    for c in col[1:-1]:
        if "Expense" in c or "Tax" in c:
            waterf_data[c] = -1*waterf_data[c]
    
    m = ['relative' for i in col]
    typo = m[:-1] + ['total']
    
    fig = go.Figure(go.Waterfall(
        name=year, orientation='v',
        measure=typo,
        x=waterf_data.columns,
        textposition='outside',
        text = waterf_data.loc[year].values,
        y=waterf_data.loc[year].values
        ))
    fig.update_layout(
        title = f"Net income {year}",
        showlegend = False,
        yaxis_title=f"{devise}",
        yaxis_range=[0,waterf_data.loc[year].values[0]+8000]
        )
    return fig

def margin_squeeze(pnl, devise):
    fig, ax = plt.subplots()
    pnl['Expenses'] = pnl['Cost of Revenue'] + pnl['Operating Expenses']
    ax.plot(pnl.index, pnl['Revenue'], label='income')
    ax.plot(pnl.index, pnl['Expenses'], label='expenses')
    ax.fill_between(pnl.index,pnl['Revenue'],pnl['Expenses'], where=(pnl['Revenue']>pnl['Expenses']), color=palette[0], alpha=0.3)
    ax.fill_between(pnl.index,pnl['Revenue'],pnl['Expenses'], where=(pnl['Revenue']<pnl['Expenses']), color=palette[1], alpha=0.3)
    plt.title(f'Margin squeeze')
    plt.xticks(pnl.index)
    plt.ylabel(devise)
    return fig

# WK

def working_cap_analysis(bs, pnl, devise):
    bs['Working Capital'] = bs['Receivables']+bs['Inventory']+bs['Other Current Assets']-bs['Accounts Payable']-bs['Current Debt']-bs['Other Current Liabilities']
    bs['Ratio_WK'] = bs['Working Capital'] / pnl['Revenue']
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.bar(bs.index, bs['Working Capital'], label='Working capital')
    ax2.plot(bs['Ratio_WK'], color=palette[1], label='Ratio working capital')
    annotate_line(bs['Ratio_WK'], palette[1])
    ax2.set_ylim(bs['Ratio_WK'].min()-0.1, 1.2)
    plt.legend()
    plt.title(f'BFR')
    plt.xticks(bs.index)
    ax1.set_ylabel(devise)
    return fig

def wk_by_year(bs, year, devise):
    bfr = bs[['Receivables','Inventory','Other Current Assets','Accounts Payable','Current Debt','Other Current Liabilities', 'Working Capital']]
    for col in ['Accounts Payable','Current Debt','Other Current Liabilities']:
        bfr[col] = -1*bfr[col]

    if bfr.loc[year].values[-1]<0:
        ymin = bfr.loc[year].values[-1] -20000
    else:
        ymin=0

    fig = go.Figure(go.Waterfall(
        name=year, orientation='v',
        measure=['relative','relative','relative','relative','relative','relative', 'total'],
        x=bfr.columns,
        textposition='outside',
        text = bfr.loc[year].values,
        y=bfr.loc[year].values
        ))
    fig.update_layout(
        title = f"Working capital {year}",
        showlegend = True,
        yaxis_title=f"{devise}",
        yaxis_range=[ymin,bfr.loc[year].values[0]+10000]
        )
    return fig

def turnover_ratio(bs, pnl):
    bs['Turnover_receivables'] = (bs['Receivables'] / pnl['Revenue']) * 365
    bs['Turnover_payables'] = (bs['Accounts Payable'] / pnl['Cost of Revenue']) * 365
    bs['Turnover_inventory'] = (bs['Inventory'] / pnl['Revenue']) * 365

    fig, ax = plt.subplots()
    bs['Turnover_receivables'].plot(kind='line', label='Receivables turnover', ax=ax)
    bs['Turnover_payables'].plot(kind='line', label='Payables turnover', ax=ax)
    bs['Turnover_inventory'].plot(kind='line', label='Inventory turnover', ax=ax)
    plt.legend()
    plt.title(f'Turnover ratio')
    plt.xticks(bs.index)
    plt.ylabel('days')
    return fig

def cur_asset_analysis(bs, devise):
    assets = list(bs.iloc[:,bs.columns.get_loc('Cash & Cash Equivalents'):bs.columns.get_loc('Total Current Assets')].columns)
    assets.remove('Cash Growth')
    bot = 0

    fig, ax = plt.subplots()

    for e in assets:
        ax.bar(bs.index, bs[e], bottom=bot, label=e)
        bot = bot + bs[e]
    
    bs['total_current_assets'] = bs['Total Current Assets'] + bs['Cash & Cash Equivalents']
    plt.ylim(0,bs['total_current_assets'].max()+1000)
    plt.legend()

    for bar in ax.patches:
        if bar.get_height() != 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() / 2 + bar.get_y(),
                    round(bar.get_height()), ha = 'center',
                    color = 'black', size = 8)

    plt.xticks(bs.index)
    plt.title(f'Current Assets')
    plt.ylabel(devise)
    return fig

# investments

def investment_analysis(cfw, devise):
    fig, ax = plt.subplots()
    ax.plot(cfw.index, -cfw['Investing Cash Flow'], label='Investments')
    ax.plot(cfw.index, cfw['Operating Cash Flow'], label='Operating CF')
    plt.title(f'Investment policy')
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xticks(cfw.index)
    plt.ylabel(f'{devise}')
    plt.legend()
    return fig

def lt_asset_analysis(bs, devise):
    assets = bs.iloc[:,bs.columns.get_loc('Total Current Assets'):bs.columns.get_loc('Total Long-Term Assets')].columns
    bot = 0

    fig, ax = plt.subplots()

    for e in assets:
        ax.bar(bs.index, bs[e], bottom=bot, label=e)
        bot = bot + bs[e]
    plt.ylim(0,bs['Total Assets'].max()+10000)
    plt.legend()

    for bar in ax.patches:
        if bar.get_height() != 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() / 2 + bar.get_y(),
                    round(bar.get_height()), ha = 'center',
                    color = 'black', size = 8)

    plt.xticks(bs.index)
    plt.title(f'Assets')
    plt.ylabel(devise)
    return fig

# financing

def liquidity_analysis(cfw, bs):
    cfw['current_ratio'] = bs['Total Current Assets'] / bs['Total Current Liabilities']
    cfw['quick_current_ratio'] = (bs['Total Current Assets'] - bs['Inventory']) / bs['Total Current Liabilities']
    cfw['cash_ratio'] = bs['Cash & Cash Equivalents'] / bs['Total Current Liabilities']

    fig, ax = plt.subplots()
    cfw[['current_ratio','quick_current_ratio','cash_ratio']].sort_index().plot(kind='line', ax=ax)
    plt.title(f'Liquidity')
    plt.legend(['Current ratio','Quick current ratio (w/o inventory)','Cash ratio'])
    plt.xticks(cfw.index)
    return fig

def solvability_analysis(cfw, bs):
    cfw['autonomy_ratio'] = bs["Shareholders' Equity"] / (bs["Shareholders' Equity"] + bs["Total Long-Term Liabilities"])
    cfw['debt_to_equity'] = bs["Total Long-Term Liabilities"] / bs["Shareholders' Equity"]
    cfw['general_liquidity_ratio'] = bs["Total Current Assets"] / (bs["Total Current Liabilities"])
    cfw['CAF'] = cfw['Net Income'] + cfw['Depreciation & Amortization'] + cfw['Change in Investments']
    cfw['reimb_capacity_ratio'] = bs['Total Debt'] / cfw['CAF']

    fig, ax = plt.subplots()
    cfw[['autonomy_ratio','debt_to_equity','general_liquidity_ratio','reimb_capacity_ratio']].sort_index().plot(kind='line', ax=ax)
    plt.title(f'Solvability')
    plt.legend(['Autonomy ratio','Debt-to-Equity ratio','General Liquidity ratio','Capacity of reimbursement'])
    plt.xticks(cfw.index)
    return fig

# General valuation

def profitability_analysis(pnl, bs, tax):
    bs['Average assets']= (bs['Total Assets'] + bs['Total Assets'].shift(-1))/2
    bs['Average equity']= (bs["Shareholders' Equity"] + bs["Shareholders' Equity"].shift(-1))/2

    pnl['ROCE'] = (pnl['Operating Income']*(1-tax))/ (bs["Shareholders' Equity"]-bs['Net Cash / Debt'])
    pnl['ROE'] = pnl['Net Income'] / bs['Average equity']
    pnl['ROA'] = pnl['Net Income'] / bs['Average assets']
    # pnl['Net_debt_cost'] = (pnl['Interest Expense / Income']*(1-tax))/bs['Total Debt']
    # pnl['ROE_opti']= pnl['ROCE'] + (pnl['ROCE']-pnl['Net_debt_cost'])*(bs['Total Debt']/bs["Shareholders' Equity"])

    fig, ax = plt.subplots()
    pnl[['ROCE', 'ROE', 'ROA']].sort_index().plot(kind='line', ax=ax)
    plt.title(f'Rentabilité (effet de levier)')
    plt.legend(['ROCE', 'ROE', 'ROA'])
    plt.xticks(pnl.index)
    return fig

def market_capitalization(extraction):
    scale = extraction[-1]
    mcap = float(extraction[:-1])
    if scale=='T':
        mcap = mcap * 1000000
    elif scale=='B':
        mcap = mcap * 1000
    return mcap

def pe_analysis(stock_price, pnl):
    pe = stock_price / pnl['EPS (Basic)'].values[0]
    txt1 = f"To date, the PE ratio is {pe:.2f}"
    if pe < 7:
        txt2 = "Company in crisis or belonging to an industry in decline."
    elif pe < 12:
        txt2 = "Company unloved by the market at this time. Could be an investment opportunity."
    elif pe < 25:
        txt2 = "Solid company with a good track record."
    else:
        txt2 = "Growth company benefiting from a dominant position or a speculative bubble."
    return pe, txt1, txt2

def pb_analysis(market_cap, bs):
    pb = market_capitalization(market_cap)/bs["Shareholders' Equity"].values[0]
    txt1 = f"To date, the PB ratio is {pb:.2f}"
    if pb > 1:
        txt2 = "The stock price could be overvalued (trading at a premium).\n The PB ratio should be compared with companies within the same sector (with a similar makeup of assets/liabilities)."
    elif pb < 1:
        txt2 = "This stock price may be undervalued (or the assets value might be overstated)."
    return pb, txt1, txt2
