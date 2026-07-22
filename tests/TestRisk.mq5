//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestRisk.mq5                                           |
//| Purpose : Risk Layer Integration Test                            |
//+------------------------------------------------------------------+
#property strict

#include "../core/risk/RiskEngine.mqh"

//--------------------------------------------------

CRiskEngine Risk;

//--------------------------------------------------

int OnInit()
{
    Risk.MoneyManager().SetRiskPercent(2.0);

    Risk.EquityProtection().SetMinimumEquity(800.0);

    Risk.DrawdownProtection().SetMaxDrawdownPercent(10.0);

    Print("========== RISK ==========");

    Print("Risk %          : ", Risk.MoneyManager().GetRiskPercent());

    Print("Min Equity      : ", Risk.EquityProtection().GetMinimumEquity());

    Print("Max Drawdown %  : ", Risk.DrawdownProtection().GetMaxDrawdownPercent());

    return INIT_SUCCEEDED;
}

//--------------------------------------------------

void OnTick()
{
}

//--------------------------------------------------

void OnDeinit(const int reason)
{
}