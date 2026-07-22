//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioRiskResult.mqh                                |
//| Layer   : Core / Risk / Models                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Risk Evaluation Result                       |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_MODELS_PORTFOLIORISKRESULT_MQH
#define CORE_RISK_MODELS_PORTFOLIORISKRESULT_MQH

class CPortfolioRiskResult
{
public:
    double TotalExposure;

    double FloatingDrawdown;

    double MarginUsage;

    double EquityProtection;

    bool PortfolioSafe;

    //--------------------------------------------------

    CPortfolioRiskResult()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        TotalExposure = 0.0;

        FloatingDrawdown = 0.0;

        MarginUsage = 0.0;

        EquityProtection = 0.0;

        PortfolioSafe = true;
    }
};

#endif