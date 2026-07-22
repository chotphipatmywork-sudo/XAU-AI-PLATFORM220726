//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionRiskResult.mqh                                 |
//| Layer   : Core / Risk / Models                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Position Risk Evaluation Result                        |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_MODELS_POSITIONRISKRESULT_MQH
#define CORE_RISK_MODELS_POSITIONRISKRESULT_MQH

class CPositionRiskResult
{
public:
    double LotSize;

    double RiskAmount;

    double StopLossDistance;

    double TakeProfitDistance;

    double RiskRewardRatio;

    bool Valid;

    //--------------------------------------------------

    CPositionRiskResult()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        LotSize = 0.0;

        RiskAmount = 0.0;

        StopLossDistance = 0.0;

        TakeProfitDistance = 0.0;

        RiskRewardRatio = 0.0;

        Valid = false;
    }
};

#endif