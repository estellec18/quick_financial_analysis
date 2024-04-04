import streamlit as st
import fin_dash
import seaborn as sns

sns.set_palette('Set2')
palette = sns.color_palette("Set2")

st.set_page_config(
    page_title="Quick financial analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.container():
    st.title("Quick and dirty financial analysis")
    st.markdown(
        '<h1 style="font-size:18px">This dashboard has been created to show in one go all the relevant information needed to get an idea of a company</h1>',
        unsafe_allow_html=True,
    )

with st.container():
    col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25], gap='medium')
    with col1:
        ticker = st.text_input('Ticker of the company')
    with col2:
        year = st.text_input('Year of analysis')
    with col3:
        tax = st.text_input('Tax rate')
    with col4:
        st.markdown("#")
        analysis = st.checkbox("Display analysis")
    if analysis:
        name, stock_price, market_cap, dev, devise, fiscal_y, data = fin_dash.get_financial_info(ticker)
        st.markdown("###")
        st.markdown(f'<h1 style="font-size:20px">{name} - {stock_price} {dev}</h1>', unsafe_allow_html=True)

list_tab = ["Statements","Margin","Working Capital","Investments","Financing","General Valuation"]
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([s for s in list_tab])

if analysis:

    with tab1:
        col1, col2, col3 = st.columns([0.33, 0.33, 0.33], gap='medium')
        with col1:
            st.markdown('**Income Statement**')
            pl, fig = fin_dash.income_analysis(data['P&L'], devise)
            st.pyplot(fig)
        with col2:
            st.markdown('**Balance sheet**')
            bs, fig = fin_dash.balance_sheet_analysis(data['Balance_sheet'], devise)
            st.pyplot(fig)
        with col3:
            st.markdown('**Cash Flow statement**')
            cfw, fig = fin_dash.cash_analysis(data['Cash_flow'], devise)
            st.pyplot(fig)

    with tab2:
        col1, col2 = st.columns([0.5, 0.5], gap='medium')
        with col1:
            fig = fin_dash.operating_analysis_2(pl, devise)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.net_income_wtf(pl, int(year), devise)
            st.plotly_chart(fig)
        with col1:
            st.markdown("###")
            fig = fin_dash.operating_expenses(pl, devise)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.margin_squeeze(pl, devise)
            st.pyplot(fig)

    with tab3:
        col1, col2 = st.columns([0.5, 0.5], gap='medium')
        with col1:
            fig = fin_dash.working_cap_analysis(bs, pl, devise)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.wk_by_year(bs, int(year), devise)
            st.plotly_chart(fig)
        with col1:
            st.markdown("###")
            fig = fin_dash.turnover_ratio(bs, pl)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.cur_asset_analysis(bs, devise)
            st.pyplot(fig)

    with tab4:
        col1, col2 = st.columns([0.5, 0.5], gap='medium')
        with col1:
            fig = fin_dash.investment_analysis(cfw, devise)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.lt_asset_analysis(bs, devise)
            st.pyplot(fig)

    with tab5:
        col1, col2 = st.columns([0.5, 0.5], gap='medium')
        with col1:
            fig = fin_dash.liquidity_analysis(cfw, bs)
            st.pyplot(fig)
        with col2:
            fig = fin_dash.solvability_analysis(cfw, bs)
            st.pyplot(fig)
    
    with tab6:
        col1, col2 = st.columns([0.5, 0.5], gap='medium')
        with col1:
            fig = fin_dash.profitability_analysis(pl, bs, float(tax))
            st.pyplot(fig)
        with col2:
            pe, txt1, txt2 = fin_dash.pe_analysis(stock_price, pl)
            st.markdown("#")
            st.markdown(txt1)
            st.markdown(txt2)
            st.markdown("#")
            pb, txt1, txt2 = fin_dash.pb_analysis(market_cap, bs)
            st.markdown(txt1)
            st.markdown(txt2)
