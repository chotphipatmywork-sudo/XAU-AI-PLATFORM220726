//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskSnapshot.mqh                                      |
//| Layer   : Core / Risk / Models                                  |
//| Version : 1.1.0                                                 |
//| Purpose : Risk State Snapshot                                   |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_MODELS_RISKSNAPSHOT_MQH
#define CORE_RISK_MODELS_RISKSNAPSHOT_MQH


class CRiskSnapshot
{
public:

    double Balance;

    double Equity;

    double DrawdownPercent;

    double DailyLossPercent;

    double RiskPercent;

    bool TradingAllowed;


public:


    CRiskSnapshot()
    {
        Reset();
    }


    CRiskSnapshot(
        const CRiskSnapshot &other)
    {
        Balance = other.Balance;
        Equity = other.Equity;
        DrawdownPercent = other.DrawdownPercent;
        DailyLossPercent = other.DailyLossPercent;
        RiskPercent = other.RiskPercent;
        TradingAllowed = other.TradingAllowed;
    }



    void Reset()
    {
        Balance = 0.0;

        Equity = 0.0;

        DrawdownPercent = 0.0;

        DailyLossPercent = 0.0;

        RiskPercent = 0.0;

        TradingAllowed = false;
    }

};


#endif