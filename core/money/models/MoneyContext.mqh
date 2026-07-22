//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MoneyContext.mqh                                       |
//| Layer   : Core / Money / Models                                  |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_MODELS_MONEYCONTEXT_MQH
#define CORE_MONEY_MODELS_MONEYCONTEXT_MQH

class CMoneyContext
{
public:
    string Symbol;

    double Balance;

    double Equity;

    double RiskPercent;

    double StopLossPoints;

public:
    CMoneyContext()
    {
        Reset();
    }

    void Reset()
    {
        Symbol = "";
        Balance = 0.0;
        Equity = 0.0;
        RiskPercent = 1.0;
        StopLossPoints = 0.0;
    }
};

#endif