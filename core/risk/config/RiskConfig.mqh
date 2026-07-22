//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskConfig.mqh                                         |
//| Layer   : Risk / Config                                          |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_CONFIG_RISKCONFIG_MQH
#define CORE_RISK_CONFIG_RISKCONFIG_MQH

class CRiskConfig
{
public:
    double RiskPercent;

    double MaxDailyLossPercent;

    double MaxDrawdownPercent;

    double MaxLot;

    double MinLot;

    CRiskConfig()
    {
        RiskPercent = 1.0;

        MaxDailyLossPercent = 5.0;

        MaxDrawdownPercent = 10.0;

        MaxLot = 10.0;

        MinLot = 0.01;
    }
};

#endif