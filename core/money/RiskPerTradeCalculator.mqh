//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskPerTradeCalculator.mqh                             |
//| Layer   : Core / Money                                           |
//| Version : 1.0.0                                                  |
//| Purpose : Calculate Risk Money Per Trade                         |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_RISKPERTRADECALCULATOR_MQH
#define CORE_MONEY_RISKPERTRADECALCULATOR_MQH

class CRiskPerTradeCalculator
{
public:
    double Calculate(
        const double balance,
        const double riskPercent)
    {
        if (balance <= 0.0)
            return 0.0;

        if (riskPercent <= 0.0)
            return 0.0;

        return balance * (riskPercent / 100.0);
    }
};

#endif